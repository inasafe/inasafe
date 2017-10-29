# coding=utf-8
"""A converter for USGS shakemap grid.xml files."""

import codecs
import logging
import os
import shutil
import sys
from datetime import datetime
from subprocess import call, CalledProcessError
from xml.dom import minidom

import pytz
# This import is required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
from osgeo import gdal, ogr
from osgeo.gdalconst import GA_ReadOnly
from pytz import timezone
from qgis.core import (
    QgsPoint,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsRectangle,
    QgsRaster,
    QgsRasterLayer)

from safe.common.exceptions import (
    GridXmlFileNotFoundError,
    GridXmlParseError,
    ContourCreationError,
    InvalidLayerError,
    CallGDALError)
from safe.common.utilities import which, romanise
from safe.datastore.folder import Folder
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.hazard_category import hazard_category_single_event
from safe.definitions.hazard_classifications import earthquake_mmi_scale
from safe.definitions.layer_geometry import layer_geometry_raster
from safe.definitions.layer_modes import layer_mode_continuous
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.definitions.units import unit_mmi
from safe.definitions.versions import inasafe_keyword_version
from safe.utilities.direction_distance import get_direction_distance
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.styling import mmi_colour

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


def data_dir():
    """Return the path to the standard data dir for e.g. geonames data

    :returns: Returns the default data directory.
    :rtype: str
    """
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'converter_data'))
    return dir_path


class ShakeGrid(object):
    """A converter for USGS shakemap grid.xml files to geotiff."""

    def __init__(
            self,
            title,
            source,
            grid_xml_path,
            place_layer=None,
            name_field=None,
            population_field=None,
            output_dir=None,
            output_basename=None,
            algorithm_filename_flag=True):
        """Constructor.

        :param title: The title of the earthquake that will be also added to
            keywords file on some generated products.
        :type title: str

        :param source: The source of the earthquake that will be also added
            to keywords file on some generated products.
        :type source: str

        :param grid_xml_path: Path to grid XML file.
        :type grid_xml_path: str

        :param output_dir: mmi output directory
        :type output_dir: str

        :param output_basename: mmi file name without extension.
        :type output_basename: str

        :param algorithm_filename_flag: Flag whether to use the algorithm in
            the output file's name.
        :type algorithm_filename_flag: bool

        :returns: The instance of the class.
        :rtype: ShakeGrid

        :raises: EventXmlParseError
        """
        self.title = title
        self.source = source
        self.latitude = None
        self.longitude = None
        self.magnitude = None
        self.depth = None
        self.description = None
        self.location = None
        self.day = None
        self.month = None
        self.year = None
        self.time = None
        self.hour = None
        self.minute = None
        self.second = None
        self.time_zone = None
        self.x_minimum = None
        self.x_maximum = None
        self.y_minimum = None
        self.y_maximum = None
        # The bounding box of the grid as QgsRectangle
        self.grid_bounding_box = None
        self.rows = None
        self.columns = None
        self.mmi_data = None
        if output_dir is None:
            self.output_dir = os.path.dirname(grid_xml_path)
        else:
            self.output_dir = output_dir
        if output_basename is None:
            self.output_basename = "mmi"
        else:
            self.output_basename = output_basename
        self.algorithm_name = algorithm_filename_flag
        self.grid_xml_path = grid_xml_path
        self.parse_grid_xml()
        self.place_layer = place_layer
        self.name_field = name_field
        self.population_field = population_field
        self.locality = None
        self.nearby_cities = None

    def extract_date_time(self, the_time_stamp):
        """Extract the parts of a date given a timestamp as per below example.

        :param the_time_stamp: The 'event_timestamp' attribute from  grid.xml.
        :type the_time_stamp: str

        # now separate out its parts
        # >>> e = "2012-08-07T01:55:12WIB"
        #>>> e[0:10]
        #'2012-08-07'
        #>>> e[12:-3]
        #'01:55:11'
        #>>> e[-3:]
        #'WIB'   (WIB = Western Indonesian Time)
        """
        date_tokens = the_time_stamp[0:10].split('-')
        self.year = int(date_tokens[0])
        self.month = int(date_tokens[1])
        self.day = int(date_tokens[2])

        time_tokens = the_time_stamp[11:19].split(':')
        self.hour = int(time_tokens[0])
        self.minute = int(time_tokens[1])
        self.second = int(time_tokens[2])

        # right now only handles Indonesian Timezones
        tz_dict = {
            'WIB': 'Asia/Jakarta',
            'WITA': 'Asia/Makassar',
            'WIT': 'Asia/Jayapura'
        }
        if self.time_zone in tz_dict:
            self.time_zone = tz_dict.get(self.time_zone, self.time_zone)

        try:
            if not self.time_zone:
                # default to utc if empty
                tzinfo = pytz.utc
            else:
                tzinfo = timezone(self.time_zone)
        except:
            tzinfo = pytz.utc

        self.time = datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            # For now realtime always uses Indonesia Time
            tzinfo=tzinfo)

    def parse_grid_xml(self):
        """Parse the grid xyz and calculate the bounding box of the event.

        :raises: GridXmlParseError

        The grid xyz dataset looks like this::

           <?xml version="1.0" encoding="US-ASCII" standalone="yes"?>
           <shakemap_grid xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns="http://earthquake.usgs.gov/eqcenter/shakemap"
           xsi:schemaLocation="http://earthquake.usgs.gov
           http://earthquake.usgs.gov/eqcenter/shakemap/xml/schemas/
           shakemap.xsd" event_id="20120807015938" shakemap_id="20120807015938"
           shakemap_version="1" code_version="3.5"
           process_timestamp="2012-08-06T18:28:37Z" shakemap_originator="us"
           map_status="RELEASED" shakemap_event_type="ACTUAL">
           <event magnitude="5.1" depth="206" lat="2.800000"
               lon="128.290000" event_timestamp="2012-08-07T01:55:12WIB"
               event_network="" event_description="Halmahera, Indonesia    " />
           <grid_specification lon_min="126.290000" lat_min="0.802000"
               lon_max="130.290000" lat_max="4.798000"
               nominal_lon_spacing="0.025000" nominal_lat_spacing="0.024975"
               nlon="161" nlat="161" />
           <grid_field index="1" name="LON" units="dd" />
           <grid_field index="2" name="LAT" units="dd" />
           <grid_field index="3" name="PGA" units="pctg" />
           <grid_field index="4" name="PGV" units="cms" />
           <grid_field index="5" name="MMI" units="intensity" />
           <grid_field index="6" name="PSA03" units="pctg" />
           <grid_field index="7" name="PSA10" units="pctg" />
           <grid_field index="8" name="PSA30" units="pctg" />
           <grid_field index="9" name="STDPGA" units="pctg" />
           <grid_field index="10" name="URAT" units="" />
           <grid_field index="11" name="SVEL" units="ms" />
           <grid_data>
           126.2900 04.7980 0.01 0.02 1.16 0.05 0.02 0 0.5 1 600
           126.3150 04.7980 0.01 0.02 1.16 0.05 0.02 0 0.5 1 600
           126.3400 04.7980 0.01 0.02 1.17 0.05 0.02 0 0.5 1 600
           126.3650 04.7980 0.01 0.02 1.17 0.05 0.02 0 0.5 1 600
           ...
           ... etc

        .. note:: We could have also obtained some of this data from the
           grid.xyz and event.xml but the **grid.xml** is preferred because it
           contains clear and unequivical metadata describing the various
           fields and attributes. Also it provides all the data we need in a
           single file.
        """
        LOGGER.debug('ParseGridXml requested.')
        grid_path = self.grid_file_path()
        try:
            document = minidom.parse(grid_path)
            event_element = document.getElementsByTagName('event')
            event_element = event_element[0]
            self.magnitude = float(
                event_element.attributes['magnitude'].nodeValue)
            self.longitude = float(
                event_element.attributes['lon'].nodeValue)
            self.latitude = float(
                event_element.attributes['lat'].nodeValue)
            self.location = event_element.attributes[
                'event_description'].nodeValue.strip()
            self.depth = float(
                event_element.attributes['depth'].nodeValue)
            # Get the date - it's going to look something like this:
            # 2012-08-07T01:55:12WIB
            time_stamp = event_element.attributes['event_timestamp'].nodeValue
            # Note the timezone here is inconsistent with YZ from grid.xml
            # use the latter
            self.time_zone = time_stamp[19:]
            self.extract_date_time(time_stamp)

            specification_element = document.getElementsByTagName(
                'grid_specification')
            specification_element = specification_element[0]
            self.x_minimum = float(
                specification_element.attributes['lon_min'].nodeValue)
            self.x_maximum = float(
                specification_element.attributes['lon_max'].nodeValue)
            self.y_minimum = float(
                specification_element.attributes['lat_min'].nodeValue)
            self.y_maximum = float(
                specification_element.attributes['lat_max'].nodeValue)
            self.grid_bounding_box = QgsRectangle(
                self.x_minimum, self.y_maximum, self.x_maximum, self.y_minimum)
            self.rows = float(
                specification_element.attributes['nlat'].nodeValue)
            self.columns = float(
                specification_element.attributes['nlon'].nodeValue)
            data_element = document.getElementsByTagName(
                'grid_data')
            data_element = data_element[0]
            data = data_element.firstChild.nodeValue

            # Extract the 1,2 and 5th (MMI) columns and populate mmi_data
            longitude_column = 0
            latitude_column = 1
            mmi_column = 4
            self.mmi_data = []
            for line in data.split('\n'):
                if not line:
                    continue
                tokens = line.split(' ')
                longitude = tokens[longitude_column]
                latitude = tokens[latitude_column]
                mmi = tokens[mmi_column]
                mmi_tuple = (longitude, latitude, mmi)
                self.mmi_data.append(mmi_tuple)

        except Exception, e:
            LOGGER.exception('Event parse failed')
            raise GridXmlParseError(
                'Failed to parse grid file.\n%s\n%s' % (e.__class__, str(e)))

    def grid_file_path(self):
        """Validate that grid file path points to a file.

        :return: The grid xml file path.
        :rtype: str

        :raises: GridXmlFileNotFoundError
        """
        if os.path.isfile(self.grid_xml_path):
            return self.grid_xml_path
        else:
            raise GridXmlFileNotFoundError

    def mmi_to_delimited_text(self):
        """Return the mmi data as a delimited test string.

        :returns: A delimited text string that can easily be written to disk
            for e.g. use by gdal_grid.
        :rtype: str

        The returned string will look like this::

           123.0750,01.7900,1
           123.1000,01.7900,1.14
           123.1250,01.7900,1.15
           123.1500,01.7900,1.16
           etc...
        """
        delimited_text = 'lon,lat,mmi\n'
        for row in self.mmi_data:
            delimited_text += '%s,%s,%s\n' % (row[0], row[1], row[2])
        return delimited_text

    def mmi_to_delimited_file(self, force_flag=True):
        """Save mmi_data to delimited text file suitable for gdal_grid.

        The output file will be of the same format as strings returned from
        :func:`mmi_to_delimited_text`.

        :param force_flag: Whether to force the regeneration of the output
            file. Defaults to False.
        :type force_flag: bool

        :returns: The absolute file system path to the delimited text file.
        :rtype: str

        .. note:: An accompanying .csvt will be created which gdal uses to
           determine field types. The csvt will contain the following string:
           "Real","Real","Real". These types will be used in other conversion
           operations. For example to convert the csv to a shp you would do::

              ogr2ogr -select mmi -a_srs EPSG:4326 mmi.shp mmi.vrt mmi
        """
        LOGGER.debug('mmi_to_delimited_text requested.')

        csv_path = os.path.join(
            self.output_dir, 'mmi.csv')
        # short circuit if the csv is already created.
        if os.path.exists(csv_path) and force_flag is not True:
            return csv_path
        csv_file = file(csv_path, 'w')
        csv_file.write(self.mmi_to_delimited_text())
        csv_file.close()

        # Also write the .csvt which contains metadata about field types
        csvt_path = os.path.join(
            self.output_dir, self.output_basename + '.csvt')
        csvt_file = file(csvt_path, 'w')
        csvt_file.write('"Real","Real","Real"')
        csvt_file.close()

        return csv_path

    def mmi_to_vrt(self, force_flag=True):
        """Save the mmi_data to an ogr vrt text file.

        :param force_flag: Whether to force the regeneration of the output
            file. Defaults to False.
        :type force_flag: bool

        :returns: The absolute file system path to the .vrt text file.
        :rtype: str

        :raises: None
        """
        # Ensure the delimited mmi file exists
        LOGGER.debug('mmi_to_vrt requested.')

        vrt_path = os.path.join(
            self.output_dir,
            self.output_basename + '.vrt')

        # short circuit if the vrt is already created.
        if os.path.exists(vrt_path) and force_flag is not True:
            return vrt_path

        csv_path = self.mmi_to_delimited_file(True)

        vrt_string = (
            '<OGRVRTDataSource>'
            '  <OGRVRTLayer name="mmi">'
            '    <SrcDataSource>%s</SrcDataSource>'
            '    <GeometryType>wkbPoint</GeometryType>'
            '    <GeometryField encoding="PointFromColumns"'
            '                      x="lon" y="lat" z="mmi"/>'
            '  </OGRVRTLayer>'
            '</OGRVRTDataSource>' % csv_path)

        with codecs.open(vrt_path, 'w', encoding='utf-8') as f:
            f.write(vrt_string)

        return vrt_path

    def _run_command(self, command):
        """Run a command and raise any error as needed.

        This is a simple runner for executing gdal commands.

        :param command: A command string to be run.
        :type command: str

        :raises: Any exceptions will be propagated.
        """
        try:
            my_result = call(command, shell=True)
            del my_result
        except CalledProcessError, e:
            LOGGER.exception('Running command failed %s' % command)
            message = (
                'Error while executing the following shell '
                'command: %s\nError message: %s' % (command, str(e)))
            # shameless hack - see https://github.com/AIFDR/inasafe/issues/141
            if sys.platform == 'darwin':  # Mac OS X
                if 'Errno 4' in str(e):
                    # continue as the error seems to be non critical
                    pass
                else:
                    raise Exception(message)
            else:
                raise Exception(message)

    def mmi_to_raster(self, force_flag=False, algorithm='nearest'):
        """Convert the grid.xml's mmi column to a raster using gdal_grid.

        A geotiff file will be created.

        Unfortunately no python bindings exist for doing this so we are
        going to do it using a shell call.

        .. see also:: http://www.gdal.org/gdal_grid.html

        Example of the gdal_grid call we generate::

           gdal_grid -zfield "mmi" -a invdist:power=2.0:smoothing=1.0 \
           -txe 126.29 130.29 -tye 0.802 4.798 -outsize 400 400 -of GTiff \
           -ot Float16 -l mmi mmi.vrt mmi.tif

        .. note:: It is assumed that gdal_grid is in your path.

        :param force_flag: Whether to force the regeneration of the output
            file. Defaults to False.
        :type force_flag: bool

        :param algorithm: Which re-sampling algorithm to use.
            valid options are 'nearest' (for nearest neighbour), 'invdist'
            (for inverse distance), 'average' (for moving average). Defaults
            to 'nearest' if not specified. Note that passing re-sampling alg
            parameters is currently not supported. If None is passed it will
            be replaced with 'nearest'.
        :type algorithm: str

        :returns: Path to the resulting tif file.
        :rtype: str

        .. note:: For interest you can also make quite beautiful smoothed
          raster using this:

          gdal_grid -zfield "mmi" -a_srs EPSG:4326
          -a invdist:power=2.0:smoothing=1.0 -txe 122.45 126.45
          -tye -2.21 1.79 -outsize 400 400 -of GTiff
          -ot Float16 -l mmi mmi.vrt mmi-trippy.tif
        """
        LOGGER.debug('mmi_to_raster requested.')

        if algorithm is None:
            algorithm = 'nearest'

        if self.algorithm_name:
            tif_path = os.path.join(
                self.output_dir, '%s-%s.tif' % (
                    self.output_basename, algorithm))
        else:
            tif_path = os.path.join(
                self.output_dir, '%s.tif' % self.output_basename)
        # short circuit if the tif is already created.
        if os.path.exists(tif_path) and force_flag is not True:
            return tif_path

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        vrt_path = self.mmi_to_vrt(force_flag)

        # now generate the tif using default nearest neighbour interpolation
        # options. This gives us the same output as the mi.grd generated by
        # the earthquake server.

        if 'invdist' in algorithm:
            algorithm = 'invdist:power=2.0:smoothing=1.0'

        # (Sunni): I'm not sure how this 'mmi' will work
        # (Tim): Its the mapping to which field in the CSV contains the data
        #    to be gridded.
        command = (
            (
                '%(gdal_grid)s -a %(alg)s -zfield "mmi" -txe %(xMin)s '
                '%(xMax)s -tye %(yMin)s %(yMax)s -outsize %(dimX)i '
                '%(dimY)i -of GTiff -ot Float16 -a_srs EPSG:4326 -l mmi '
                '"%(vrt)s" "%(tif)s"'
            ) % {
                'gdal_grid': which('gdal_grid')[0],
                'alg': algorithm,
                'xMin': self.x_minimum,
                'xMax': self.x_maximum,
                'yMin': self.y_minimum,
                'yMax': self.y_maximum,
                'dimX': self.columns,
                'dimY': self.rows,
                'vrt': vrt_path,
                'tif': tif_path
            }
        )

        LOGGER.info('Created this gdal command:\n%s' % command)
        # Now run GDAL warp scottie...
        self._run_command(command)

        # We will use keywords file name with simple algorithm name since it
        # will raise an error in windows related to having double colon in path
        if 'invdist' in algorithm:
            algorithm = 'invdist'

        if  self.place_layer is not None:
            self.generate_locality_info(tif_path)
        # copy the keywords file from fixtures for this layer
        self.create_keyword_file(algorithm)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        if self.algorithm_name:
            qml_path = os.path.join(
                self.output_dir, '%s-%s.qml' % (
                    self.output_basename, algorithm))
        else:
            qml_path = os.path.join(
                self.output_dir, '%s.qml' % self.output_basename)
        qml_source_path = os.path.join(data_dir(), 'mmi.qml')
        shutil.copyfile(qml_source_path, qml_path)
        return tif_path

    def mmi_to_shapefile(self, force_flag=False):
        """Convert grid.xml's mmi column to a vector shp file using ogr2ogr.

        An ESRI shape file will be created.

        :param force_flag: bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.

        :return: Path to the resulting tif file.
        :rtype: str

        Example of the ogr2ogr call we generate::

           ogr2ogr -select mmi -a_srs EPSG:4326 mmi.shp mmi.vrt mmi

        .. note:: It is assumed that ogr2ogr is in your path.
        """
        LOGGER.debug('mmi_to_shapefile requested.')

        shp_path = os.path.join(
            self.output_dir, '%s-points.shp' % self.output_basename)
        # Short circuit if the tif is already created.
        if os.path.exists(shp_path) and force_flag is not True:
            return shp_path

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        vrt_path = self.mmi_to_vrt(force_flag)

        # now generate the tif using default interpolation options

        binary_list = which('ogr2ogr')
        LOGGER.debug('Path for ogr2ogr: %s' % binary_list)
        if len(binary_list) < 1:
            raise CallGDALError(
                tr('ogr2ogr could not be found on your computer'))
        # Use the first matching gdalwarp found
        binary = binary_list[0]
        command = (
            ('%(ogr2ogr)s -overwrite -select mmi -a_srs EPSG:4326 '
             '%(shp)s %(vrt)s mmi') % {
                'ogr2ogr': binary,
                'shp': shp_path,
                'vrt': vrt_path})

        LOGGER.info('Created this ogr command:\n%s' % command)
        # Now run ogr2ogr ...
        # noinspection PyProtectedMember
        self._run_command(command)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        qml_path = os.path.join(
            self.output_dir, '%s-points.qml' % self.output_basename)
        source_qml = os.path.join(data_dir(), 'mmi-shape.qml')
        shutil.copyfile(source_qml, qml_path)
        return shp_path

    def mmi_to_contours(self, force_flag=True, algorithm='nearest'):
        """Extract contours from the event's tif file.

        Contours are extracted at a 0.5 MMI interval. The resulting file will
        be saved in the extract directory. In the easiest use case you can

        :param force_flag:  (Optional). Whether to force the
         regeneration of contour product. Defaults to False.
        :type force_flag: bool

        :param algorithm: (Optional) Which interpolation algorithm to
                  use to create the underlying raster. Defaults to 'nearest'.
        :type algorithm: str
         **Only enforced if theForceFlag is true!**

        :returns: An absolute filesystem path pointing to the generated
            contour dataset.
        :exception: ContourCreationError

         simply do::

           shake_grid = ShakeGrid()
           contour_path = shake_grid.mmi_to_contours()

        which will return the contour dataset for the latest event on the
        ftp server.
        """
        LOGGER.debug('mmi_to_contours requested.')
        # TODO: Use sqlite rather?
        output_file_base = os.path.join(
            self.output_dir,
            '%s-contours-%s.' % (self.output_basename, algorithm))
        output_file = output_file_base + 'shp'
        if os.path.exists(output_file) and force_flag is not True:
            return output_file
        elif os.path.exists(output_file):
            try:
                os.remove(output_file_base + 'shp')
                os.remove(output_file_base + 'shx')
                os.remove(output_file_base + 'dbf')
                os.remove(output_file_base + 'prj')
            except OSError:
                LOGGER.exception(
                    'Old contour files not deleted'
                    ' - this may indicate a file permissions issue.')

        tif_path = self.mmi_to_raster(force_flag, algorithm)
        # Based largely on
        # http://svn.osgeo.org/gdal/trunk/autotest/alg/contour.py
        driver = ogr.GetDriverByName('ESRI Shapefile')
        ogr_dataset = driver.CreateDataSource(output_file)
        if ogr_dataset is None:
            # Probably the file existed and could not be overriden
            raise ContourCreationError(
                'Could not create datasource for:\n%s. Check that the file '
                'does not already exist and that you do not have file system '
                'permissions issues' % output_file)
        layer = ogr_dataset.CreateLayer('contour')
        field_definition = ogr.FieldDefn('ID', ogr.OFTInteger)
        layer.CreateField(field_definition)
        field_definition = ogr.FieldDefn('MMI', ogr.OFTReal)
        layer.CreateField(field_definition)
        # So we can fix the x pos to the same x coord as centroid of the
        # feature so labels line up nicely vertically
        field_definition = ogr.FieldDefn('X', ogr.OFTReal)
        layer.CreateField(field_definition)
        # So we can fix the y pos to the min y coord of the whole contour so
        # labels line up nicely vertically
        field_definition = ogr.FieldDefn('Y', ogr.OFTReal)
        layer.CreateField(field_definition)
        # So that we can set the html hex colour based on its MMI class
        field_definition = ogr.FieldDefn('RGB', ogr.OFTString)
        layer.CreateField(field_definition)
        # So that we can set the label in it roman numeral form
        field_definition = ogr.FieldDefn('ROMAN', ogr.OFTString)
        layer.CreateField(field_definition)
        # So that we can set the label horizontal alignment
        field_definition = ogr.FieldDefn('ALIGN', ogr.OFTString)
        layer.CreateField(field_definition)
        # So that we can set the label vertical alignment
        field_definition = ogr.FieldDefn('VALIGN', ogr.OFTString)
        layer.CreateField(field_definition)
        # So that we can set feature length to filter out small features
        field_definition = ogr.FieldDefn('LEN', ogr.OFTReal)
        layer.CreateField(field_definition)

        tif_dataset = gdal.Open(tif_path, GA_ReadOnly)
        # see http://gdal.org/java/org/gdal/gdal/gdal.html for these options
        band = 1
        contour_interval = 0.5
        contour_base = 0
        fixed_level_list = []
        use_no_data_flag = 0
        no_data_value = -9999
        id_field = 0  # first field defined above
        elevation_field = 1  # second (MMI) field defined above
        try:
            gdal.ContourGenerate(
                tif_dataset.GetRasterBand(band),
                contour_interval,
                contour_base,
                fixed_level_list,
                use_no_data_flag,
                no_data_value,
                layer,
                id_field,
                elevation_field)
        except Exception, e:
            LOGGER.exception('Contour creation failed')
            raise ContourCreationError(str(e))
        finally:
            del tif_dataset
            ogr_dataset.Release()

        # Copy over the standard .prj file since ContourGenerate does not
        # create a projection definition
        qml_path = os.path.join(
            self.output_dir,
            '%s-contours-%s.prj' % (self.output_basename, algorithm))
        source_qml = os.path.join(data_dir(), 'mmi-contours.prj')
        shutil.copyfile(source_qml, qml_path)

        # Lastly copy over the standard qml (QGIS Style file)
        qml_path = os.path.join(
            self.output_dir,
            '%s-contours-%s.qml' % (self.output_basename, algorithm))
        source_qml = os.path.join(data_dir(), 'mmi-contours.qml')
        shutil.copyfile(source_qml, qml_path)

        # Now update the additional columns - X,Y, ROMAN and RGB
        try:
            self.set_contour_properties(output_file)
        except InvalidLayerError:
            raise

        return output_file

    def set_contour_properties(self, input_file):
        """Set the X, Y, RGB, ROMAN attributes of the contour layer.

        :param input_file: (Required) Name of the contour layer.
        :type input_file: str

        :raise: InvalidLayerError if anything is amiss with the layer.
        """
        LOGGER.debug('set_contour_properties requested for %s.' % input_file)
        layer = QgsVectorLayer(input_file, 'mmi-contours', "ogr")
        if not layer.isValid():
            raise InvalidLayerError(input_file)

        layer.startEditing()
        # Now loop through the db adding selected features to mem layer
        request = QgsFeatureRequest()
        fields = layer.fields()

        for feature in layer.getFeatures(request):
            if not feature.isValid():
                LOGGER.debug('Skipping feature')
                continue
            # Work out x and y
            line = feature.geometry().asPolyline()
            y = line[0].y()

            x_max = line[0].x()
            x_min = x_max
            for point in line:
                if point.y() < y:
                    y = point.y()
                x = point.x()
                if x < x_min:
                    x_min = x
                if x > x_max:
                    x_max = x
            x = x_min + ((x_max - x_min) / 2)

            # Get length
            length = feature.geometry().length()

            mmi_value = float(feature['MMI'])
            # We only want labels on the whole number contours
            if mmi_value != round(mmi_value):
                roman = ''
            else:
                roman = romanise(mmi_value)

            # RGB from http://en.wikipedia.org/wiki/Mercalli_intensity_scale
            rgb = mmi_colour(mmi_value)

            # Now update the feature
            feature_id = feature.id()
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('X'), x)
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('Y'), y)
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('RGB'), rgb)
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('ROMAN'), roman)
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('ALIGN'), 'Center')
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('VALIGN'), 'HALF')
            layer.changeAttributeValue(
                feature_id, fields.indexFromName('LEN'), length)

        layer.commitChanges()

    def mmi_point_sampling(self, place_layer, raster_mmi_path):
        """Get MMI information from ShakeMap Tiff on place location.

        Get the MMI value on each cities/places from the generated tiff files.
        :param place_layer: Point layer generated from distance calculation
        :type place_layer: QgsVectorLayer
        :param raster_mmi_path: Path to converted mmi raster.
        :type raster_mmi_path: str
        :return: Modified place layer containing MMI values
        :rtype: QgsVectorLayer
        """
        shake_raster = QgsRasterLayer(raster_mmi_path, 'shake_raster')
        shake_provider = shake_raster.dataProvider()

        place_fields = place_layer.dataProvider().fields()
        mmi_field_index = place_fields.indexFromName('mmi')

        place_layer.startEditing()
        for feature in place_layer.getFeatures():
            fid = feature.id()
            point = feature.geometry().asPoint()
            mmi_identify = shake_provider.identify(
                point,
                QgsRaster.IdentifyFormatValue
            )
            mmi = mmi_identify.results()[1]
            place_layer.changeAttributeValue(fid, mmi_field_index, mmi)
        place_layer.commitChanges()
        # save the memory place layer
        data_store = Folder(self.output_dir)
        data_store.default_vector_format = 'geojson'
        data_store.add_layer(
            place_layer,
            '%s-nearby-places' % self.output_basename
        )
        return place_layer

    def generate_locality_info(self, raster_mmi_path):
        """Generate information related to the locality of the hazard.

        :param raster_mmi_path: path to converted raster mmi
        :type raster_mmi_path: str
        """

        epicenter = QgsPoint(self.longitude, self.latitude)
        place_layer = self.place_layer

        measured_place_layer = get_direction_distance(epicenter, place_layer)
        mmi_point_layer = self.mmi_point_sampling(
            measured_place_layer,
            raster_mmi_path
        )
        places = []
        for feature in mmi_point_layer.getFeatures():
            place = {
                'name': feature[self.name_field],
                'population': feature[self.population_field],
                'distance': feature['distance'],
                'bearing_to': feature['bearing_to'],
                'dir_to': feature['dir_to'],
                'mmi_values': feature['mmi']
            }
            places.append(place)
        # sort the place by mmi and by population
        sorted_places = sorted(
            places,
            key=itemgetter('mmi_values', 'population'),
            reverse=True
        )
        nearest_place = sorted_places[0]
        # combine locality text
        city_name = nearest_place['name']
        city_distance = nearest_place['distance']
        city_bearing = nearest_place['bearing_to']
        city_direction = nearest_place['dir_to']
        self.locality = 'Located ' + str(math.floor(city_distance / 1000)) + \
                        ' km, ' + str(math.floor(city_bearing)) + '° ' + \
                        str(city_direction) + ' of ' + str(city_name)
        self.nearby_cities = sorted_places[:5]

    def create_keyword_file(self, algorithm):
        """Create keyword file for the raster file created.

        Basically copy a template from keyword file in converter data
        and add extra keyword (usually a title)

        :param algorithm: Which re-sampling algorithm to use.
            valid options are 'nearest' (for nearest neighbour), 'invdist'
            (for inverse distance), 'average' (for moving average). Defaults
            to 'nearest' if not specified. Note that passing re-sampling alg
            parameters is currently not supported. If None is passed it will
            be replaced with 'nearest'.
        :type algorithm: str
        """
        keyword_io = KeywordIO()

        classes = {}
        for item in earthquake_mmi_scale['classes']:
            classes[item['key']] = [
                item['numeric_default_min'], item['numeric_default_max']]

        extra_keywords = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'magnitude': self.magnitude,
            'depth': self.depth,
            'description': self.description,
            'location': self.location,
            'locality': self.locality,
            # 'day': self.day,
            # 'month': self.month,
            # 'year': self.year,
            # 'time': self.time,
            # 'hour': self.hour,
            # 'minute': self.minute,
            # 'second': self.second,
            'time_zone': self.time_zone,
            'x_minimum': self.x_minimum,
            'x_maximum': self.x_maximum,
            'y_minimum': self.y_minimum,
            'y_maximum': self.y_maximum,
        }
        # Delete empty element.
        empty_keys = []
        for key, value in extra_keywords.items():
            if value is None:
                empty_keys.append(key)
        for empty_key in empty_keys:
            extra_keywords.pop(empty_key)
        keywords = {
            'hazard': hazard_earthquake['key'],
            'hazard_category': hazard_category_single_event['key'],
            'keyword_version': inasafe_keyword_version,
            'layer_geometry': layer_geometry_raster['key'],
            'layer_mode': layer_mode_continuous['key'],
            'layer_purpose': layer_purpose_hazard['key'],
            'continuous_hazard_unit': unit_mmi['key'],
            'classification': earthquake_mmi_scale['key'],
            'thresholds': classes,
            'extra_keywords': extra_keywords
        }

        if self.algorithm_name:
            layer_path = os.path.join(
                self.output_dir, '%s-%s.tif' % (
                    self.output_basename, algorithm))
        else:
            layer_path = os.path.join(
                self.output_dir, '%s.tif' % self.output_basename)

        # append title and source to the keywords file
        if len(self.title.strip()) == 0:
            keyword_title = self.output_basename
        else:
            keyword_title = self.title

        keywords['title'] = keyword_title

        hazard_layer = QgsRasterLayer(layer_path, keyword_title)

        if not hazard_layer.isValid():
            raise InvalidLayerError()

        keyword_io.write_keywords(hazard_layer, keywords)


def convert_mmi_data(
        grid_xml_path,
        title,
        source,
        place_layer=None,
        place_name=None,
        place_population=None,
        output_path=None,
        algorithm=None,
        algorithm_filename_flag=True):
    """Convenience function to convert a single file.

    :param grid_xml_path: Path to the xml shake grid file.
    :type grid_xml_path: str

    :param title: The title of the earthquake.
    :type title: str

    :param source: The source of the shake data.
    :type source: str

    :param place_layer: Nearby cities/places.
    :type place_layer: QgsVectorLayer

    :param place_name: Column name that indicates name of the cities.
    :type place_name: str

    :param place_population: Column name that indicates number of population.
    :type place_population: str

    :param output_path: Specify which path to use as an alternative to the
        default.
    :type output_path: str

    :param algorithm: Type of algorithm to be used.
    :type algorithm: str

    :param algorithm_filename_flag: Flag whether to use the algorithm in the
        output file's name.
    :type algorithm_filename_flag: bool

    :returns: A path to the resulting raster file.
    :rtype: str
    """
    LOGGER.debug(grid_xml_path)
    LOGGER.debug(output_path)
    if output_path is not None:
        output_dir, output_basename = os.path.split(output_path)
        output_basename, _ = os.path.splitext(output_basename)
        LOGGER.debug('output_dir : ' + output_dir +
                     'output_basename : ' + output_basename)
    else:
        output_dir = output_path
        output_basename = None
    converter = ShakeGrid(
        title,
        source,
        grid_xml_path,
        place_layer,
        place_name,
        place_population,
        output_dir=output_dir,
        output_basename=output_basename,
        algorithm_filename_flag=algorithm_filename_flag)
    return converter.mmi_to_raster(force_flag=True, algorithm=algorithm)
