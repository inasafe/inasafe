# -*- coding: utf-8 -*-
"""**Functionality related to convert format file.**

InaSAFE Disaster risk assessment tool developed by AusAid and World Bank

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

Adapted from shake_event.py
"""
__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '11/02/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import shutil
from xml.dom import minidom
from subprocess import call, CalledProcessError
import logging


from safe.common.exceptions import (
    GridXmlFileNotFoundError,
    GridXmlParseError)

# The logger is initialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')


def data_dir():
    """Return the path to the standard data dir for e.g. geonames data

    :returns: Returns the default data directory.
    :rtype: str
    """
    my_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'converter_data'))
    return my_dir


class ShakeGridConverter():
    """A converter for USGS shakemap grid.xml files to geotiff."""

    def __init__(
            self,
            grid_xml_path,
            output_dir=None,
            output_basename=None,
            algorithm_filename_flag=True):
        """Constructor.

        :param grid_xml_path: Path to grid XML file
        :type grid_xml_path:str

        :param output_dir: mmi output directory
        :type output_dir: str

        :param output_basename: mmi file name without extension
        :type output_basename: str

        :param algorithm_filename_flag: Flag whether to use the algorithm in
            the output file's name
        :type algorithm_filename_flag: bool

        :returns: Instance
        :rtype: ShakeGridConverter

        :raises: EventXmlParseError
        """
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

    def extract_date_time(self, the_time_stamp):
        """Extract the parts of a date given a timestamp as per below example.

        :param the_time_stamp: Is the 'event_timestamp' attribute from  grid
         .xml.
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
        my_date_tokens = the_time_stamp[0:10].split('-')
        self.year = int(my_date_tokens[0])
        self.month = int(my_date_tokens[1])
        self.day = int(my_date_tokens[2])
        my_time_tokens = the_time_stamp[11:-3].split(':')
        self.hour = int(my_time_tokens[0])
        self.minute = int(my_time_tokens[1])
        self.second = int(my_time_tokens[2])

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
        my_path = self.grid_file_path()
        try:
            document = minidom.parse(my_path)
            event_element = document.getElementsByTagName('event')
            event_element = event_element[0]
            self.magnitude = float(event_element.attributes[
                'magnitude'].nodeValue)
            self.longitude = float(event_element.attributes[
                'lon'].nodeValue)
            self.latitude = float(event_element.attributes[
                'lat'].nodeValue)
            self.location = event_element.attributes[
                'event_description'].nodeValue.strip()
            self.depth = float(event_element.attributes['depth'].nodeValue)
            # Get the date - its going to look something like this:
            # 2012-08-07T01:55:12WIB
            my_time_stamp = event_element.attributes[
                'event_timestamp'].nodeValue
            self.extract_date_time(my_time_stamp)
            # Note the timezone here is inconsistent with YZ from grid.xml
            # use the latter
            self.time_zone = my_time_stamp[-3:]

            my_specification_element = document.getElementsByTagName(
                'grid_specification')
            my_specification_element = my_specification_element[0]
            self.x_minimum = float(my_specification_element.attributes[
                'lon_min'].nodeValue)
            self.x_maximum = float(my_specification_element.attributes[
                'lon_max'].nodeValue)
            self.y_minimum = float(my_specification_element.attributes[
                'lat_min'].nodeValue)
            self.y_maximum = float(my_specification_element.attributes[
                'lat_max'].nodeValue)
            self.rows = float(my_specification_element.attributes[
                'nlat'].nodeValue)
            self.columns = float(my_specification_element.attributes[
                'nlon'].nodeValue)
            data_element = document.getElementsByTagName(
                'grid_data')
            data_element = data_element[0]
            my_data = data_element.firstChild.nodeValue
            # Extract the 1,2 and 5th (MMI) columns and populate mmi_data
            my_lonitude_column = 0
            my_latitude_column = 1
            my_mmi_column = 4
            self.mmi_data = []
            for my_line in my_data.split('\n'):
                if not my_line:
                    continue
                my_tokens = my_line.split(' ')
                my_longitude = my_tokens[my_lonitude_column]
                my_latitude = my_tokens[my_latitude_column]
                my_mmi = my_tokens[my_mmi_column]
                my_tuple = (my_longitude, my_latitude, my_mmi)
                self.mmi_data.append(my_tuple)

        except Exception, e:
            LOGGER.exception('Event parse failed')
            raise GridXmlParseError('Failed to parse grid file.\n%s\n%s'
                                    % (e.__class__, str(e)))

    def grid_file_path(self):
        """ Validate that grid file path points to a file.

        :raises: GridXmlFileNotFoundError

        :return: grid xml file path
        :rtype: str
        """
        if os.path.isfile(self.grid_xml_path):
            return self.grid_xml_path
        else:
            raise GridXmlFileNotFoundError

    def mmi_to_delimited_text(self):
        """Return the mmi data as a delimited test string.

        :returns: a delimited text string that can easily be written to disk
            for e.g. use by gdal_grid.
        :rtype: str

        The returned string will look like this::

           123.0750,01.7900,1
           123.1000,01.7900,1.14
           123.1250,01.7900,1.15
           123.1500,01.7900,1.16
           etc...
        """
        my_string = 'lon,lat,mmi\n'
        for my_row in self.mmi_data:
            my_string += '%s,%s,%s\n' % (my_row[0], my_row[1], my_row[2])
        return my_string

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

        # TODO(Sunni): I'm not sure how this 'mmi' will work
        my_path = os.path.join(self.output_dir, 'mmi.csv')
        # TODO(Sunni): I'm not sure how this 'mmi' will work
        #short circuit if the csv is already created.
        if os.path.exists(my_path) and force_flag is not True:
            return my_path
        my_file = file(my_path, 'wt')
        my_file.write(self.mmi_to_delimited_text())
        my_file.close()

        # Also write the .csv which contains metadata about field types
        my_csv_path = os.path.join(
            self.output_dir, self.output_basename + '.csvt')
        my_file = file(my_csv_path, 'wt')
        my_file.write('"Real","Real","Real"')
        my_file.close()
        return my_path

    def mmi_to_vrt(self, force_flag=True):
        """Save the mmi_data to an ogr vrt text file.

        :param force_flag: Whether to force the regeneration of the output
            file. Defaults to False.
        :type force_flag: bool


        :returns: The absolute file system path to the .vrt text file.
        :rtype: str

        Raises: None
        """
        # Ensure the delimited mmi file exists
        LOGGER.debug('mmi_to_vrt requested.')

        my_vrt_path = os.path.join(
            self.output_dir,
            self.output_basename + '.vrt')

        #short circuit if the vrt is already created.
        if os.path.exists(my_vrt_path) and force_flag is not True:
            return my_vrt_path

        my_csv_path = self.mmi_to_delimited_file(True)

        my_vrt_string = (
            '<OGRVRTDataSource>'
            '  <OGRVRTLayer name="mmi">'
            '    <SrcDataSource>%s</SrcDataSource>'
            '    <GeometryType>wkbPoint</GeometryType>'
            '    <GeometryField encoding="PointFromColumns"'
            '                      x="lon" y="lat" z="mmi"/>'
            '  </OGRVRTLayer>'
            '</OGRVRTDataSource>' % my_csv_path)
        my_file = file(my_vrt_path, 'wt')
        my_file.write(my_vrt_string)
        my_file.close()
        return my_vrt_path

    def _add_executable_prefix(self, command):
        """Add the executable prefix for gdal binaries.

        This is primarily needed for OSX where gdal tools are tucked away in
        the Library path.

        :param command: The command to which the prefix will be prepended.
        :type command: str

        :returns: A copy of the command with the prefix added.
        :rtype: str
        """

        my_executable_prefix = ''
        if sys.platform == 'darwin':  # Mac OS X
            my_executable_prefix = (
                '/Library/Frameworks/GDAL'
                '.framework/Versions/Current/Programs/')
        command = my_executable_prefix + command
        return command

    def _run_command(self, command):
        """Run a command and raise any error as needed.

        This is a simple runner for executing gdal commands.

        :param command: A command string to be run.
        :type command: str

        :raises: Any exceptions will be propagated.
        """

        my_command = self._add_executable_prefix(command)

        try:
            my_result = call(my_command, shell=True)
            del my_result
        except CalledProcessError, e:
            LOGGER.exception('Running command failed %s' % my_command)
            my_message = (
                'Error while executing the following shell '
                'command: %s\nError message: %s' % (my_command, str(e)))
            # shameless hack - see https://github.com/AIFDR/inasafe/issues/141
            if sys.platform == 'darwin':  # Mac OS X
                if 'Errno 4' in str(e):
                    # continue as the error seems to be non critical
                    pass
                else:
                    raise Exception(my_message)
            else:
                raise Exception(my_message)

    def mmi_to_raster(
            self, force_flag=False, algorithm='nearest'):
        """Convert the grid.xml' s mmi column to a raster using gdal_grid.

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
            my_tif_path = os.path.join(
                self.output_dir, '%s-%s.tif' % (
                    self.output_basename, algorithm))
        else:
            my_tif_path = os.path.join(
                self.output_dir, '%s.tif' % self.output_basename)
        #short circuit if the tif is already created.
        if os.path.exists(my_tif_path) and force_flag is not True:
            return my_tif_path

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        my_vrt_path = self.mmi_to_vrt(force_flag)

        # now generate the tif using default nearest neighbour interpolation
        # options. This gives us the same output as the mi.grd generated by
        # the earthquake server.

        if 'invdist' in algorithm:
            myAlgorithm = 'invdist:power=2.0:smoothing=1.0'
        else:
            myAlgorithm = algorithm

        # (Sunni): I'm not sure how this 'mmi' will work
        # (Tim): Its the mapping to which field in the CSV contains the data
        #    to be gridded.
        command = ((
            'gdal_grid -a %(alg)s -zfield "mmi" -txe %(xMin)s '
            '%(xMax)s -tye %(yMin)s %(yMax)s -outsize %(dimX)i '
            '%(dimY)i -of GTiff -ot Float16 -a_srs EPSG:4326 -l mmi '
            '%(vrt)s %(tif)s') %
            {
                'alg': myAlgorithm,
                'xMin': self.x_minimum,
                'xMax': self.x_maximum,
                'yMin': self.y_minimum,
                'yMax': self.y_maximum,
                'dimX': self.columns,
                'dimY': self.rows,
                'vrt': my_vrt_path,
                'tif': my_tif_path
            })

        LOGGER.info('Created this gdal command:\n%s' % command)
        # Now run GDAL warp scottie...
        self._run_command(command)

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
        my_source_qml = os.path.join(data_dir(), 'mmi.qml')
        shutil.copyfile(my_source_qml, qml_path)
        return my_tif_path

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
        if self.algorithm_name:
            keyword_path = os.path.join(
                self.output_dir, '%s-%s.keywords' % (
                    self.output_basename, algorithm))
        else:
            keyword_path = os.path.join(
                self.output_dir, '%s.keywords' % self.output_basename)
        mmi_keywords = os.path.join(data_dir(), 'mmi.keywords')
        shutil.copyfile(mmi_keywords, keyword_path)
        # append title to the keywords file
        with open(keyword_path, 'a') as my_file:
            my_file.write('title: ' + self.output_basename)


def convert_mmi_data(
        grid_xml_path,
        output_path=None,
        algorithm=None,
        algorithm_filename_flag=True):
    """Convenience function to convert a single file.

    :param grid_xml_path: Path to the xml file
    :type grid_xml_path: str

    :param output_path: Specify which path to use as an alternative to the
        default.
    :type output_path: str

    :param algorithm: Type of algorithm to be used.
    :type algorithm: str

    :param algorithm_filename_flag: Flag whether to use the algorithm in the
        output file's name
    :type algorithm_filename_flag: bool

    :returns: A path to the resulting raster file
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
    converter = ShakeGridConverter(
        grid_xml_path, output_dir, output_basename,
        algorithm_filename_flag)
    return converter.mmi_to_raster(force_flag=True, algorithm=algorithm)
