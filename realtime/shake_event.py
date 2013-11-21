# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake events.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '1/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import shutil
import cPickle as pickle
from xml.dom import minidom
import math
from subprocess import call, CalledProcessError
import logging
from datetime import datetime

import numpy
import pytz  # sudo apt-get install python-tz
import ogr
import gdal
from gdalconst import GA_ReadOnly

from sftp_shake_data import SftpShakeData


# TODO I think QCoreApplication is needed for tr() check hefore removing
from PyQt4.QtCore import (
    QCoreApplication,
    QObject,
    QVariant,
    QFileInfo,
    QString,
    QStringList,
    QUrl,
    QSize,
    Qt,
    QTranslator)
from PyQt4.QtXml import QDomDocument
# We should remove the following pylint suppressions when we support only QGIS2
# pylint: disable=E0611
# pylint: disable=W0611
# Above for pallabelling
from qgis.core import (
    QgsPoint,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsVectorLayer,
    QgsRaster,
    QgsRasterLayer,
    QgsRectangle,
    QgsDataSourceURI,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsComposition,
    QgsMapLayerRegistry,
    QgsMapRenderer,
    QgsPalLabeling,
    QgsProviderRegistry,
    QgsFeatureRequest)
# pylint: enable=E0611
# pylint: enable=W0611
from safe_qgis.utilities.utilities_for_testing import get_qgis_app
from safe_qgis.exceptions import TranslationLoadError
from safe.common.version import get_version
from safe.api import get_plugins as safe_get_plugins
from safe.api import read_layer as safe_read_layer
from safe.api import calculate_impact as safe_calculate_impact
from safe.api import Table, TableCell, TableRow
from safe_qgis.utilities.utilities import getWGS84resolution
from safe_qgis.utilities.clipper import extent_to_geoarray, clip_layer
from safe_qgis.utilities.styling import mmi_colour
from utils import shakemapExtractDir, dataDir
from rt_exceptions import (
    GridXmlFileNotFoundError,
    GridXmlParseError,
    ContourCreationError,
    InvalidLayerError,
    ShapefileCreationError,
    CityMemoryLayerCreationError,
    FileNotFoundError,
    MapComposerError)
from realtime.utils import setupLogger
# from shake_data import ShakeData

setupLogger()
LOGGER = logging.getLogger('InaSAFE')
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ShakeEvent(QObject):
    """The ShakeEvent class encapsulates behaviour and data relating to an
    earthquake, including epicenter, magnitude etc."""

    def __init__(self,
                 theEventId=None,
                 theLocale='en',
                 thePopulationRasterPath=None,
                 theForceFlag=False,
                 theDataIsLocalFlag=False):
        """Constructor for the shake event class.

        Args:
            * theEventId - (Optional) Id of the event. Will be used to
                fetch the ShakeData for this event (either from cache or from
                ftp server as required). The grid.xml file in the unpacked
                event will be used to intialise the state of the ShakeEvent
                instance.
                If no event id is supplied, the most recent event recorded
                on the server will be used.
            * theLocale - (Optional) string for iso locale to use for outputs.
                Defaults to en. Can also use 'id' or possibly more as
                translations are added.
            * thePopulationRasterPath - (Optional)path to the population raster
                that will be used if you want to calculate the impact. This
                is optional because there are various ways this can be
                specified before calling :func:`calculateImpacts`.
            * theForceFlag: bool Whether to force retrieval of the dataset from
                the ftp server.
            * theDataIsLocalFlag: bool Whether the data is already extracted
                and exists locally. Use this in cases where you manually want
                to run a grid.xml without first doing a download.

        Returns: Instance

        Raises: EventXmlParseError
        """
        # We inherit from QObject for translation support
        QObject.__init__(self)

        self.checkEnvironment()

        if theDataIsLocalFlag:
            self.eventId = theEventId
        else:
            # fetch the data from (s)ftp
            #self.data = ShakeData(theEventId, theForceFlag)
            self.data = SftpShakeData(
                theEvent=theEventId,
                theForceFlag=theForceFlag)
            self.data.extract()
            self.eventId = self.data.eventId

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
        self.timeZone = None
        self.xMinimum = None
        self.xMaximum = None
        self.yMinimum = None
        self.yMaximum = None
        self.rows = None
        self.columns = None
        self.mmiData = None
        self.populationRasterPath = thePopulationRasterPath
        # Path to tif of impact result - probably we wont even use it
        self.impactFile = None
        # Path to impact keywords file - this is GOLD here!
        self.impactKeywordsFile = None
        # number of people killed per mmi band
        self.fatalityCounts = None
        # Total number of predicted fatalities
        self.fatalityTotal = 0
        # number of people displaced per mmi band
        self.displacedCounts = None
        # number of people affected per mmi band
        self.affectedCounts = None
        # After selecting affected cities near the event, the bbox of
        # shake map + cities
        self.extentWithCities = None
        # How much to iteratively zoom out by when searching for cities
        self.zoomFactor = 1.25
        # The search boxes used to find extent_with_cities
        # Stored in the form [{'city_count': int, 'geometry': QgsRectangle()}]
        self.searchBoxes = None
        # Stored as a dict with dir_to, dist_to,  dist_from etc e.g.
        #{'dir_from': 16.94407844543457,
        #'dir_to': -163.05592346191406,
        #'roman': 'II',
        #'dist_to': 2.504295825958252,
        #'mmi': 1.909999966621399,
        #'name': 'Tondano',
        #'id': 57,
        #'population': 33317}
        self.mostAffectedCity = None
        # for localization
        self.translator = None
        self.locale = theLocale
        self.setupI18n()
        self.parseGridXml()

    def checkEnvironment(self):
        """A helper class to check that QGIS is correctly initialised.

        Args: None

        Returns: None

        Raises: EnvironmentError if the environment is not correct.
        """
        # noinspection PyArgumentList
        myRegistry = QgsProviderRegistry.instance()
        myList = myRegistry.pluginList()
        if len(myList) < 1:
            raise EnvironmentError('QGIS data provider list is empty!')

    def gridFilePath(self):
        """A helper to retrieve the path to the grid.xml file

        Args: None

        Returns: An absolute filesystem path to the grid.xml file.

        Raises: GridXmlFileNotFoundError
        """
        LOGGER.debug('Event path requested.')
        myGridXmlPath = os.path.join(shakemapExtractDir(),
                                     self.eventId,
                                     'grid.xml')
        #short circuit if the tif is already created.
        if os.path.exists(myGridXmlPath):
            return myGridXmlPath
        else:
            LOGGER.error('Event file not found. %s' % myGridXmlPath)
            raise GridXmlFileNotFoundError('%s not found' % myGridXmlPath)

    def extractDateTime(self, theTimeStamp):
        """Extract the parts of a date given a timestamp as per below example.

        :param theTimeStamp: (str) as provided by the 'event_timestamp'
                attribute in the grid.xml.

        # now separate out its parts
        # >>> e = "2012-08-07T01:55:12WIB"
        #>>> e[0:10]
        #'2012-08-07'
        #>>> e[12:-3]
        #'01:55:11'
        #>>> e[-3:]
        #'WIB'   (WIB = Western Indonesian Time)
        """
        myDateTokens = theTimeStamp[0:10].split('-')
        self.year = int(myDateTokens[0])
        self.month = int(myDateTokens[1])
        self.day = int(myDateTokens[2])
        myTimeTokens = theTimeStamp[11:-3].split(':')
        self.hour = int(myTimeTokens[0])
        self.minute = int(myTimeTokens[1])
        self.second = int(myTimeTokens[2])

    def parseGridXml(self):
        """Parse the grid xyz and calculate the bounding box of the event.

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


        Args: None

        Returns: None

        Raises: GridXmlParseError
        """
        LOGGER.debug('ParseGridXml requested.')
        myPath = self.gridFilePath()
        try:
            myDocument = minidom.parse(myPath)
            myEventElement = myDocument.getElementsByTagName('event')
            myEventElement = myEventElement[0]
            self.magnitude = float(myEventElement.attributes[
                                   'magnitude'].nodeValue)
            self.longitude = float(myEventElement.attributes[
                                   'lon'].nodeValue)
            self.latitude = float(myEventElement.attributes[
                                  'lat'].nodeValue)
            self.location = myEventElement.attributes[
                'event_description'].nodeValue.strip()
            self.depth = float(myEventElement.attributes['depth'].nodeValue)
            # Get the date - its going to look something like this:
            # 2012-08-07T01:55:12WIB
            myTimeStamp = myEventElement.attributes[
                'event_timestamp'].nodeValue
            self.extractDateTime(myTimeStamp)
            # Note the timezone here is inconsistent with YZ from grid.xml
            # use the latter
            self.timeZone = myTimeStamp[-3:]

            mySpecificationElement = myDocument.getElementsByTagName(
                'grid_specification')
            mySpecificationElement = mySpecificationElement[0]
            self.xMinimum = float(mySpecificationElement.attributes[
                                  'lon_min'].nodeValue)
            self.xMaximum = float(mySpecificationElement.attributes[
                                  'lon_max'].nodeValue)
            self.yMinimum = float(mySpecificationElement.attributes[
                                  'lat_min'].nodeValue)
            self.yMaximum = float(mySpecificationElement.attributes[
                                  'lat_max'].nodeValue)
            self.rows = float(mySpecificationElement.attributes[
                              'nlat'].nodeValue)
            self.columns = float(mySpecificationElement.attributes[
                                 'nlon'].nodeValue)
            myDataElement = myDocument.getElementsByTagName(
                'grid_data')
            myDataElement = myDataElement[0]
            myData = myDataElement.firstChild.nodeValue

            # Extract the 1,2 and 5th (MMI) columns and populate mmi_data
            myLonColumn = 0
            myLatColumn = 1
            myMMIColumn = 4
            self.mmiData = []
            for myLine in myData.split('\n'):
                if not myLine:
                    continue
                myTokens = myLine.split(' ')
                myLon = myTokens[myLonColumn]
                myLat = myTokens[myLatColumn]
                myMMI = myTokens[myMMIColumn]
                myTuple = (myLon, myLat, myMMI)
                self.mmiData.append(myTuple)

        except Exception, e:
            LOGGER.exception('Event parse failed')
            raise GridXmlParseError(
                'Failed to parse grid file.\n%s\n%s'
                % (e.__class__, str(e)))

    def mmiDataToDelimitedText(self):
        """Return the mmi data as a delimited test string.

        The returned string will look like this::

           123.0750,01.7900,1
           123.1000,01.7900,1.14
           123.1250,01.7900,1.15
           123.1500,01.7900,1.16
           etc...

        Args: None

        Returns: str - a delimited text string that can easily be written to
            disk for e.g. use by gdal_grid.

        Raises: None

        """
        myString = 'lon,lat,mmi\n'
        for myRow in self.mmiData:
            myString += '%s,%s,%s\n' % (myRow[0], myRow[1], myRow[2])
        return myString

    def mmiDataToDelimitedFile(self, theForceFlag=True):
        """Save the mmi_data to a delimited text file suitable for processing
        with gdal_grid.

        The output file will be of the same format as strings returned from
        :func:`mmi_to_delimited_text`.

        .. note:: An accompanying .csvt will be created which gdal uses to
           determine field types. The csvt will contain the following string:
           "Real","Real","Real". These types will be used in other conversion
           operations. For example to convert the csv to a shp you would do::

              ogr2ogr -select mmi -a_srs EPSG:4326 mmi.shp mmi.vrt mmi

        Args: theForceFlag bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.

        Returns: str The absolute file system path to the delimited text
            file.

        Raises: None
        """
        LOGGER.debug('mmi_to_delimited_text requested.')

        myPath = os.path.join(shakemapExtractDir(),
                              self.eventId,
                              'mmi.csv')
        #short circuit if the csv is already created.
        if os.path.exists(myPath) and theForceFlag is not True:
            return myPath
        myFile = file(myPath, 'wt')
        myFile.write(self.mmiDataToDelimitedText())
        myFile.close()

        # Also write the .csv which contains metadata about field types
        myCsvPath = os.path.join(
            shakemapExtractDir(), self.eventId, 'mmi.csvt')
        myFile = file(myCsvPath, 'wt')
        myFile.write('"Real","Real","Real"')
        myFile.close()
        return myPath

    def mmiDataToVrt(self, theForceFlag=True):
        """Save the mmi_data to an ogr vrt text file.

        Args: theForceFlag bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.

        Returns: str The absolute file system path to the .vrt text file.

        Raises: None
        """
        # Ensure the delimited mmi file exists
        LOGGER.debug('mmi_to_vrt requested.')

        myVrtPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi.vrt')

        #short circuit if the vrt is already created.
        if os.path.exists(myVrtPath) and theForceFlag is not True:
            return myVrtPath

        myCsvPath = self.mmiDataToDelimitedFile(theForceFlag)

        myVrtString = ('<OGRVRTDataSource>'
                       '  <OGRVRTLayer name="mmi">'
                       '    <SrcDataSource>%s</SrcDataSource>'
                       '    <GeometryType>wkbPoint</GeometryType>'
                       '    <GeometryField encoding="PointFromColumns"'
                       '                      x="lon" y="lat" z="mmi"/>'
                       '  </OGRVRTLayer>'
                       '</OGRVRTDataSource>' % myCsvPath)
        myFile = file(myVrtPath, 'wt')
        myFile.write(myVrtString)
        myFile.close()
        return myVrtPath

    def _addExecutablePrefix(self, theCommand):
        """Add the executable prefix for gdal binaries.

        This is primarily needed for OSX where gdal tools are tucked away in
        the Library path.

        Args: theCommand str - Required. A string containing the command to
            which the prefix will be prepended.

        Returns: str - A copy of the command with the prefix added.

        Raises: None
        """

        myExecutablePrefix = ''
        if sys.platform == 'darwin':  # Mac OS X
            # .. todo:: FIXME - softcode gdal version in this path
            myExecutablePrefix = ('/Library/Frameworks/GDAL.framework/'
                                  'Versions/1.9/Programs/')
        theCommand = myExecutablePrefix + theCommand
        return theCommand

    def _runCommand(self, theCommand):
        """Run a command and raise any error as needed.

        This is a simple runner for executing gdal commands.

        Args: theCommand str - Required. A command string to be run.

        Returns: None

        Raises: Any exceptions will be propagated.
        """

        myCommand = self._addExecutablePrefix(theCommand)

        try:
            myResult = call(myCommand, shell=True)
            del myResult
        except CalledProcessError, e:
            LOGGER.exception('Running command failed %s' % myCommand)
            myMessage = ('Error while executing the following shell '
                         'command: %s\nError message: %s'
                         % (myCommand, str(e)))
            # shameless hack - see https://github.com/AIFDR/inasafe/issues/141
            if sys.platform == 'darwin':  # Mac OS X
                if 'Errno 4' in str(e):
                    # continue as the error seems to be non critical
                    pass
                else:
                    raise Exception(myMessage)
            else:
                raise Exception(myMessage)

    def mmiDataToShapefile(self, theForceFlag=False):
        """Convert grid.xml's mmi column to a vector shp file using ogr2ogr.

        An ESRI shape file will be created.

        :param theForceFlag: bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.

        ;:return: str Path to the resulting tif file.

        Example of the ogr2ogr call we generate::

           ogr2ogr -select mmi -a_srs EPSG:4326 mmi.shp mmi.vrt mmi

        .. note:: It is assumed that ogr2ogr is in your path.
        """
        LOGGER.debug('mmiDataToShapefile requested.')

        myShpPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-points.shp')
        # Short circuit if the tif is already created.
        if os.path.exists(myShpPath) and theForceFlag is not True:
            return myShpPath

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        myVrtPath = self.mmiDataToVrt(theForceFlag)

        #now generate the tif using default interpolation options

        myCommand = (
            ('ogr2ogr -overwrite -select mmi -a_srs EPSG:4326 '
             '%(shp)s %(vrt)s mmi') % {'shp': myShpPath, 'vrt': myVrtPath})

        LOGGER.info('Created this gdal command:\n%s' % myCommand)
        # Now run GDAL warp scottie...
        self._runCommand(myCommand)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-points.qml')
        mySourceQml = os.path.join(dataDir(), 'mmi-shape.qml')
        shutil.copyfile(mySourceQml, myQmlPath)
        return myShpPath

    def mmiDataToRaster(self, theForceFlag=False, theAlgorithm='nearest'):
        """Convert the grid.xml's mmi column to a raster using gdal_grid.

        A geotiff file will be created.

        Unfortunately no python bindings exist for doing this so we are
        going to do it using a shell call.

        :param theForceFlag: bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.
        :param theAlgorithm:str (Optional). Which resampling algorithm to use.
            vallid options are 'nearest' (for nearest neighbour), 'invdist'
            (for inverse distance), 'average' (for moving average). Defaults
            to 'nearest' if not specified. Note that passing resampling alg
            parameters is currently not supported. If None is passed it will
            be replaced with 'nearest'.
        .. seealso:: http://www.gdal.org/gdal_grid.html

        :return str Path to the resulting tif file.

        Example of the gdal_grid call we generate::

           gdal_grid -zfield "mmi" -a invdist:power=2.0:smoothing=1.0 \
           -txe 126.29 130.29 -tye 0.802 4.798 -outsize 400 400 -of GTiff \
           -ot Float16 -l mmi mmi.vrt mmi.tif

        .. note:: It is assumed that gdal_grid is in your path.

        .. note:: For interest you can also make quite beautiful smoothed
          rasters using this:

          gdal_grid -zfield "mmi" -a_srs EPSG:4326
          -a invdist:power=2.0:smoothing=1.0 -txe 122.45 126.45
          -tye -2.21 1.79 -outsize 400 400 -of GTiff
          -ot Float16 -l mmi mmi.vrt mmi-trippy.tif

        Raises: None
        """
        LOGGER.debug('mmi_to_raster requested.')

        if theAlgorithm is None:
            theAlgorithm = 'nearest'

        myTifPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-%s.tif' % theAlgorithm)
        #short circuit if the tif is already created.
        if os.path.exists(myTifPath) and theForceFlag is not True:
            return myTifPath

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        myVrtPath = self.mmiDataToVrt(theForceFlag)

        # now generate the tif using default nearest neighbour interpolation
        # options. This gives us the same output as the mi.grd generated by
        # the earthquake server.

        if 'invdist' in theAlgorithm:
            myAlgorithm = 'invdist:power=2.0:smoothing=1.0'
        else:
            myAlgorithm = theAlgorithm

        myOptions = {
            'alg': myAlgorithm,
            'xMin': self.xMinimum,
            'xMax': self.xMaximum,
            'yMin': self.yMinimum,
            'yMax': self.yMaximum,
            'dimX': self.columns,
            'dimY': self.rows,
            'vrt': myVrtPath,
            'tif': myTifPath}

        myCommand = (('gdal_grid -a %(alg)s -zfield "mmi" -txe %(xMin)s '
                      '%(xMax)s -tye %(yMin)s %(yMax)s -outsize %(dimX)i '
                      '%(dimY)i -of GTiff -ot Float16 -a_srs EPSG:4326 -l mmi '
                      '%(vrt)s %(tif)s') % myOptions)

        LOGGER.info('Created this gdal command:\n%s' % myCommand)
        # Now run GDAL warp scottie...
        self._runCommand(myCommand)

        # copy the keywords file from fixtures for this layer
        myKeywordPath = os.path.join(
            shakemapExtractDir(),
            self.eventId,
            'mmi-%s.keywords' % theAlgorithm)
        mySourceKeywords = os.path.join(dataDir(), 'mmi.keywords')
        shutil.copyfile(mySourceKeywords, myKeywordPath)
        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-%s.qml' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi.qml')
        shutil.copyfile(mySourceQml, myQmlPath)
        return myTifPath

    def mmiDataToContours(self, theForceFlag=True, theAlgorithm='nearest'):
        """Extract contours from the event's tif file.

        Contours are extracted at a 0.5 MMI interval. The resulting file will
        be saved in the extract directory. In the easiest use case you can
        :param theForceFlag: bool - (Optional). Whether to force the
        regeneration of contour product. Defaults to False.
        :param theAlgorithm: str - (Optional) Which interpolation algorithm to
                  use to create the underlying raster. Defaults to 'nearest'.
        **Only enforced if theForceFlag is true!**
        :returns: An absolute filesystem path pointing to the generated
            contour dataset.
        :exception: ContourCreationError
        simply do::

           myShakeEvent = myShakeData.shakeEvent()
           myContourPath = myShakeEvent.mmiToContours()

        which will return the contour dataset for the latest event on the
        ftp server.
        """
        LOGGER.debug('mmiDataToContours requested.')
        # TODO: Use sqlite rather?
        myOutputFileBase = os.path.join(shakemapExtractDir(),
                                        self.eventId,
                                        'mmi-contours-%s.' % theAlgorithm)
        myOutputFile = myOutputFileBase + 'shp'
        if os.path.exists(myOutputFile) and theForceFlag is not True:
            return myOutputFile
        elif os.path.exists(myOutputFile):
            try:
                os.remove(myOutputFileBase + 'shp')
                os.remove(myOutputFileBase + 'shx')
                os.remove(myOutputFileBase + 'dbf')
                os.remove(myOutputFileBase + 'prj')
            except OSError:
                LOGGER.exception(
                    'Old contour files not deleted'
                    ' - this may indicate a file permissions issue.')

        myTifPath = self.mmiDataToRaster(theForceFlag, theAlgorithm)
        # Based largely on
        # http://svn.osgeo.org/gdal/trunk/autotest/alg/contour.py
        myDriver = ogr.GetDriverByName('ESRI Shapefile')
        myOgrDataset = myDriver.CreateDataSource(myOutputFile)
        if myOgrDataset is None:
            # Probably the file existed and could not be overriden
            raise ContourCreationError('Could not create datasource for:\n%s'
                                       'Check that the file does not already '
                                       'exist and that you '
                                       'do not have file system permissions '
                                       'issues')
        myLayer = myOgrDataset.CreateLayer('contour')
        myFieldDefinition = ogr.FieldDefn('ID', ogr.OFTInteger)
        myLayer.CreateField(myFieldDefinition)
        myFieldDefinition = ogr.FieldDefn('MMI', ogr.OFTReal)
        myLayer.CreateField(myFieldDefinition)
        # So we can fix the x pos to the same x coord as centroid of the
        # feature so labels line up nicely vertically
        myFieldDefinition = ogr.FieldDefn('X', ogr.OFTReal)
        myLayer.CreateField(myFieldDefinition)
        # So we can fix the y pos to the min y coord of the whole contour so
        # labels line up nicely vertically
        myFieldDefinition = ogr.FieldDefn('Y', ogr.OFTReal)
        myLayer.CreateField(myFieldDefinition)
        # So that we can set the html hex colour based on its MMI class
        myFieldDefinition = ogr.FieldDefn('RGB', ogr.OFTString)
        myLayer.CreateField(myFieldDefinition)
        # So that we can set the label in it roman numeral form
        myFieldDefinition = ogr.FieldDefn('ROMAN', ogr.OFTString)
        myLayer.CreateField(myFieldDefinition)
        # So that we can set the label horizontal alignment
        myFieldDefinition = ogr.FieldDefn('ALIGN', ogr.OFTString)
        myLayer.CreateField(myFieldDefinition)
        # So that we can set the label vertical alignment
        myFieldDefinition = ogr.FieldDefn('VALIGN', ogr.OFTString)
        myLayer.CreateField(myFieldDefinition)
        # So that we can set feature length to filter out small features
        myFieldDefinition = ogr.FieldDefn('LEN', ogr.OFTReal)
        myLayer.CreateField(myFieldDefinition)

        myTifDataset = gdal.Open(myTifPath, GA_ReadOnly)
        # see http://gdal.org/java/org/gdal/gdal/gdal.html for these options
        myBand = 1
        myContourInterval = 0.5
        myContourBase = 0
        myFixedLevelList = []
        myUseNoDataFlag = 0
        myNoDataValue = -9999
        myIdField = 0  # first field defined above
        myElevationField = 1  # second (MMI) field defined above
        try:
            gdal.ContourGenerate(myTifDataset.GetRasterBand(myBand),
                                 myContourInterval,
                                 myContourBase,
                                 myFixedLevelList,
                                 myUseNoDataFlag,
                                 myNoDataValue,
                                 myLayer,
                                 myIdField,
                                 myElevationField)
        except Exception, e:
            LOGGER.exception('Contour creation failed')
            raise ContourCreationError(str(e))
        finally:
            del myTifDataset
            myOgrDataset.Release()

        # Copy over the standard .prj file since ContourGenerate does not
        # create a projection definition
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-contours-%s.prj' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi-contours.prj')
        shutil.copyfile(mySourceQml, myQmlPath)

        # Lastly copy over the standard qml (QGIS Style file)
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-contours-%s.qml' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi-contours.qml')
        shutil.copyfile(mySourceQml, myQmlPath)

        # Now update the additional columns - X,Y, ROMAN and RGB
        try:
            self.setContourProperties(myOutputFile)
        except InvalidLayerError:
            raise

        return myOutputFile

    def romanize(self, the_mmi_value):
        """Return the roman numeral for an mmi value.
        :param the_mmi_value:float
        :return str Roman numeral equivalent of the value
        """
        if the_mmi_value is None:
            LOGGER.debug('Romanize passed None')
            return ''

        LOGGER.debug('Romanising %f' % float(the_mmi_value))
        my_roman_list = ['0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII',
                         'IX', 'X', 'XI', 'XII']
        try:
            my_roman = my_roman_list[int(float(the_mmi_value))]
        except ValueError:
            LOGGER.exception('Error converting MMI value to roman')
            return None
        return my_roman

    def mmi_shaking(self, the_mmi_value):
        """Return the perceived shaking for an mmi value as translated string.
        :param the_mmi_value: float or int required.
        :return str: internationalised string representing perceived shaking
             level e.g. weak, severe etc.
        """
        my_shaking_dict = {
            1: self.tr('Not felt'),
            2: self.tr('Weak'),
            3: self.tr('Weak'),
            4: self.tr('Light'),
            5: self.tr('Moderate'),
            6: self.tr('Strong'),
            7: self.tr('Very strong'),
            8: self.tr('Severe'),
            9: self.tr('Violent'),
            10: self.tr('Extreme'),
        }
        return my_shaking_dict[the_mmi_value]

    def mmi_potential_damage(self, the_mmi_value):
        """Return the potential damage for an mmi value as translated string.
        :param the_mmi_value: float or int required.
        :return str: internationalised string representing potential damage
            level e.g. Light, Moderate etc.
        """
        my_damage_dict = {
            1: self.tr('None'),
            2: self.tr('None'),
            3: self.tr('None'),
            4: self.tr('None'),
            5: self.tr('Very light'),
            6: self.tr('Light'),
            7: self.tr('Moderate'),
            8: self.tr('Mod/Heavy'),
            9: self.tr('Heavy'),
            10: self.tr('Very heavy')
        }
        return my_damage_dict[the_mmi_value]

    def setContourProperties(self, theFile):
        """
        Set the X, Y, RGB, ROMAN attributes of the contour layer.

        :param theFile:str (Required) Name of the contour layer.
        :return: None
        :raise InvalidLayerError if anything is amiss with the layer.
        """
        LOGGER.debug('setContourProperties requested for %s.' % theFile)
        myLayer = QgsVectorLayer(theFile, 'mmi-contours', "ogr")
        if not myLayer.isValid():
            raise InvalidLayerError(theFile)

        myLayer.startEditing()
        # Now loop through the db adding selected features to mem layer
        myRequest = QgsFeatureRequest()
        myFields = myLayer.dataProvider().fields()

        for myFeature in myLayer.getFeatures(myRequest):
            if not myFeature.isValid():
                LOGGER.debug('Skipping feature')
                continue
            # Work out myX and myY
            myLine = myFeature.geometry().asPolyline()
            myY = myLine[0].y()

            myXMax = myLine[0].x()
            myXMin = myXMax
            for myPoint in myLine:
                if myPoint.y() < myY:
                    myY = myPoint.y()
                myX = myPoint.x()
                if myX < myXMin:
                    myXMin = myX
                if myX > myXMax:
                    myXMax = myX
            myX = myXMin + ((myXMax - myXMin) / 2)

            # Get length
            myLength = myFeature.geometry().length()

            myMMIValue = float(myFeature['MMI'].toString())

            # We only want labels on the whole number contours
            if myMMIValue != round(myMMIValue):
                myRoman = ''
            else:
                myRoman = self.romanize(myMMIValue)

            #LOGGER.debug('MMI: %s ----> %s' % (
            #    myAttributes[myMMIIndex].toString(), myRoman))

            # RGB from http://en.wikipedia.org/wiki/Mercalli_intensity_scale
            myRGB = mmi_colour(myMMIValue)

            # Now update the feature
            myId = myFeature.id()
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('X'), QVariant(myX))
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('Y'), QVariant(myY))
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('RGB'), QVariant(myRGB))
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('ROMAN'), QVariant(myRoman))
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('ALIGN'), QVariant('Center'))
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('VALIGN'), QVariant('HALF'))
            myLayer.changeAttributeValue(
                myId, myFields.indexFromName('LEN'), QVariant(myLength))

        myLayer.commitChanges()

    def boundsToRectangle(self):
        """Convert the event bounding box to a QgsRectangle.

        Args: theForceFlag bool - (Optional). Whether to force the regeneration
                  of contour product. Defaults to False.

        Returns: QgsRectangle

        Raises: None
        """
        LOGGER.debug('bounds to rectangle called.')
        myRectangle = QgsRectangle(self.xMinimum,
                                   self.yMaximum,
                                   self.xMaximum,
                                   self.yMinimum)
        return myRectangle

    def citiesToShapefile(self, theForceFlag=False):
        """Write a cities memory layer to a shapefile.

        :param theForceFlag: bool (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        .. note:: The file will be saved into the shakemap extract dir
           event id folder. Any existing shp by the same name will be
           overwritten if theForceFlag is False, otherwise it will
           be returned directly without creating a new file.
        :return str Path to the created shapefile
        :raise ShapefileCreationError
        """
        myFileName = 'mmi-cities'
        myMemoryLayer = self.localCitiesMemoryLayer()
        return self.memoryLayerToShapefile(theFileName=myFileName,
                                           theMemoryLayer=myMemoryLayer,
                                           theForceFlag=theForceFlag)

    def citySearchBoxesToShapefile(self, theForceFlag=False):
        """Write a cities memory layer to a shapefile.

        :param theForceFlag: bool (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        .. note:: The file will be saved into the shakemap extract dir
           event id folder. Any existing shp by the same name will be
           overwritten if theForceFlag is False, otherwise it will
           be returned directly without creating a new file.

        :return str Path to the created shapefile
        :raise ShapefileCreationError
        """
        myFileName = 'city-search-boxes'
        myMemoryLayer = self.citySearchBoxMemoryLayer()
        return self.memoryLayerToShapefile(theFileName=myFileName,
                                           theMemoryLayer=myMemoryLayer,
                                           theForceFlag=theForceFlag)

    def memoryLayerToShapefile(self,
                               theFileName,
                               theMemoryLayer,
                               theForceFlag=False):
        """Write a memory layer to a shapefile.

        :param theFileName: str filename excluding path and ext. e.g.
        'mmi-cities'
        :param theMemoryLayer: QGIS memory layer instance.
        :param theForceFlag: bool (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        .. note:: The file will be saved into the shakemap extract dir
           event id folder. If a qml matching theFileName.qml can be
           found it will automatically copied over to the output dir.
           Any existing shp by the same name will be overridden if
           theForceFlag is True, otherwise the existing file will be returned.

        :return str Path to the created shapefile
        :raise ShapefileCreationError
        """
        LOGGER.debug('memoryLayerToShapefile requested.')

        LOGGER.debug(str(theMemoryLayer.dataProvider().attributeIndexes()))
        if theMemoryLayer.featureCount() < 1:
            raise ShapefileCreationError('Memory layer has no features')

        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        myOutputFileBase = os.path.join(shakemapExtractDir(),
                                        self.eventId,
                                        '%s.' % theFileName)
        myOutputFile = myOutputFileBase + 'shp'
        if os.path.exists(myOutputFile) and theForceFlag is not True:
            return myOutputFile
        elif os.path.exists(myOutputFile):
            try:
                os.remove(myOutputFileBase + 'shp')
                os.remove(myOutputFileBase + 'shx')
                os.remove(myOutputFileBase + 'dbf')
                os.remove(myOutputFileBase + 'prj')
            except OSError:
                LOGGER.exception(
                    'Old shape files not deleted'
                    ' - this may indicate a file permissions issue.')

        # Next two lines a workaround for a QGIS bug (lte 1.8)
        # preventing mem layer attributes being saved to shp.
        theMemoryLayer.startEditing()
        theMemoryLayer.commitChanges()

        LOGGER.debug('Writing mem layer to shp: %s' % myOutputFile)
        # Explicitly giving all options, not really needed but nice for clarity
        myErrorMessage = QString()
        myOptions = QStringList()
        myLayerOptions = QStringList()
        mySelectedOnlyFlag = False
        mySkipAttributesFlag = False
        # May differ from myOutputFile
        myActualNewFileName = QString()
        myResult = QgsVectorFileWriter.writeAsVectorFormat(
            theMemoryLayer,
            myOutputFile,
            'utf-8',
            myGeoCrs,
            "ESRI Shapefile",
            mySelectedOnlyFlag,
            myErrorMessage,
            myOptions,
            myLayerOptions,
            mySkipAttributesFlag,
            myActualNewFileName)

        if myResult == QgsVectorFileWriter.NoError:
            LOGGER.debug('Wrote mem layer to shp: %s' % myOutputFile)
        else:
            raise ShapefileCreationError(
                'Failed with error: %s' % myResult)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 '%s.qml' % theFileName)
        mySourceQml = os.path.join(dataDir(), '%s.qml' % theFileName)
        shutil.copyfile(mySourceQml, myQmlPath)

        return myOutputFile

    def localCityFeatures(self):
        """Create a list of features representing cities impacted.

        The following fields will be created for each city feature:

            QgsField('id', QVariant.Int),
            QgsField('name', QVariant.String),
            QgsField('population', QVariant.Int),
            QgsField('mmi', QVariant.Double),
            QgsField('dist_to', QVariant.Double),
            QgsField('dir_to', QVariant.Double),
            QgsField('dir_from', QVariant.Double),
            QgsField('roman', QVariant.String),
            QgsField('colour', QVariant.String),

        The 'name' and 'population' fields will be obtained from our geonames
        dataset.

        A raster lookup for each city will be done to set the mmi field
        in the city feature with the value on the raster. The raster should be
        one generated using :func:`mmiDatToRaster`. The raster will be created
        first if needed.

        The distance to and direction to/from fields will be set using QGIS
        geometry API.

        It is a requirement that there will always be at least one city
        on the map for context so we will iteratively do a city selection,
        starting with the extents of the MMI dataset and then zooming
        out by self.zoom_factor until we have some cities selected.

        After making a selection the extents used (taking into account the
        iterative scaling mentioned above) will be stored in the class
        attributes so that when producing a map it can be used to ensure
        the cities and the shake area are visible on the map. See
        :samp:`self.extent_with_cities` in :func:`__init__`.

        .. note:: We separate the logic of creating features from writing a
          layer so that we can write to any format we like whilst reusing the
          core logic.

        Args: None

        Returns: list of QgsFeature instances, each representing a place/city.

        Raises: InvalidLayerError

        .. note:: The original dataset will be modified in place.
        """
        LOGGER.debug('localCityValues requested.')
        # Setup the raster layer for interpolated mmi lookups
        myPath = self.mmiDataToRaster()
        myFileInfo = QFileInfo(myPath)
        myBaseName = myFileInfo.baseName()
        myRasterLayer = QgsRasterLayer(myPath, myBaseName)
        if not myRasterLayer.isValid():
            raise InvalidLayerError('Layer failed to load!\n%s' % myPath)

        # Setup the cities table, querying on event bbox
        # Path to sqlitedb containing geonames table
        myDBPath = os.path.join(dataDir(), 'indonesia.sqlite')
        myUri = QgsDataSourceURI()
        myUri.setDatabase(myDBPath)
        myTable = 'geonames'
        myGeometryColumn = 'geom'
        mySchema = ''
        myUri.setDataSource(mySchema, myTable, myGeometryColumn)
        myLayer = QgsVectorLayer(myUri.uri(), 'Towns', 'spatialite')
        if not myLayer.isValid():
            raise InvalidLayerError(myDBPath)
        myRectangle = self.boundsToRectangle()

        # Do iterative selection using expanding selection area
        # Until we have got some cities selected

        myAttemptsLimit = 5
        myMinimumCityCount = 1
        myFoundFlag = False
        mySearchBoxes = []
        myRequest = None
        LOGGER.debug('Search polygons for cities:')
        for _ in range(myAttemptsLimit):
            LOGGER.debug(myRectangle.asWktPolygon())
            myLayer.removeSelection()
            myRequest = QgsFeatureRequest().setFilterRect(myRectangle)
            myRequest.setFlags(QgsFeatureRequest.ExactIntersect)
            # This is klunky - must be a better way in the QGIS api!?
            # but myLayer.selectedFeatureCount() relates to gui
            # selection it seems...
            myCount = 0
            for _ in myLayer.getFeatures(myRequest):
                myCount += 1
            # Store the box plus city count so we can visualise it later
            myRecord = {'city_count': myCount, 'geometry': myRectangle}
            LOGGER.debug('Found cities in search box: %s' % myRecord)
            mySearchBoxes.append(myRecord)
            if myCount < myMinimumCityCount:
                myRectangle.scale(self.zoomFactor)
            else:
                myFoundFlag = True
                break

        self.searchBoxes = mySearchBoxes
        # TODO: Perhaps it might be neater to combine the bbox of cities and
        #       mmi to get a tighter AOI then do a small zoom out.
        self.extentWithCities = myRectangle
        if not myFoundFlag:
            LOGGER.debug(
                'Could not find %s cities after expanding rect '
                '%s times.' % (myMinimumCityCount, myAttemptsLimit))
        # Setup field indexes of our input and out datasets
        myCities = []

        #myFields = QgsFields()
        #myFields.append(QgsField('id', QVariant.Int))
        #myFields.append(QgsField('name', QVariant.String))
        #myFields.append(QgsField('population', QVariant.Int))
        #myFields.append(QgsField('mmi', QVariant.Double))
        #myFields.append(QgsField('dist_to', QVariant.Double))
        #myFields.append(QgsField('dir_to', QVariant.Double))
        #myFields.append(QgsField('dir_from', QVariant.Double))
        #myFields.append(QgsField('roman', QVariant.String))
        #myFields.append(QgsField('colour', QVariant.String))

        # For measuring distance and direction from each city to epicenter
        myEpicenter = QgsPoint(self.longitude, self.latitude)

        # Now loop through the db adding selected features to mem layer
        for myFeature in myLayer.getFeatures(myRequest):
            if not myFeature.isValid():
                LOGGER.debug('Skipping feature')
                continue
                #LOGGER.debug('Writing feature to mem layer')
            # calculate the distance and direction from this point
            # to and from the epicenter
            myId = str(myFeature.id())

            # Make sure the fcode contains PPL (populated place)
            myCode = str(myFeature['fcode'].toString())
            if 'PPL' not in myCode:
                continue

            # Make sure the place is populated
            myPopulation = myFeature['population'].toInt()[0]
            if myPopulation < 1:
                continue

            myPoint = myFeature.geometry().asPoint()
            myDistance = myPoint.sqrDist(myEpicenter)
            myDirectionTo = myPoint.azimuth(myEpicenter)
            myDirectionFrom = myEpicenter.azimuth(myPoint)
            myPlaceName = str(myFeature['asciiname'].toString())

            myNewFeature = QgsFeature()
            myNewFeature.setGeometry(myFeature.geometry())

            # Populate the mmi field by raster lookup
            # Get a {int, QVariant} back
            myRasterValues = myRasterLayer.dataProvider().identify(
                myPoint, QgsRaster.IdentifyFormatValue).results()
            myRasterValues = myRasterValues.values()
            if not myRasterValues or len(myRasterValues) < 1:
                # position not found on raster
                continue
            myValue = myRasterValues[0]  # Band 1
            LOGGER.debug('MyValue: %s' % myValue)
            if 'no data' not in myValue.toString():
                myMmi = myValue.toFloat()[0]
            else:
                myMmi = 0

            LOGGER.debug('Looked up mmi of %s on raster for %s' %
                         (myMmi, myPoint.toString()))

            myRoman = self.romanize(myMmi)
            if myRoman is None:
                continue

            # myNewFeature.setFields(myFields)
            # Column positions are determined by setFields above
            myAttributes = [
                myId,
                myPlaceName,
                myPopulation,
                QVariant(myMmi),
                QVariant(myDistance),
                QVariant(myDirectionTo),
                QVariant(myDirectionFrom),
                QVariant(myRoman),
                QVariant(mmi_colour(myMmi))]
            myNewFeature.setAttributes(myAttributes)
            myCities.append(myNewFeature)
        return myCities

    def localCitiesMemoryLayer(self):
        """Fetch a collection of the cities that are nearby.

        Args: None

        Returns: QgsVectorLayer - A QGIS memory layer

        Raises: an exceptions will be propagated
        """
        LOGGER.debug('localCitiesMemoryLayer requested.')
        # Now store the selection in a temporary memory layer
        myMemoryLayer = QgsVectorLayer('Point', 'affected_cities', 'memory')

        myMemoryProvider = myMemoryLayer.dataProvider()
        # add field defs
        myMemoryProvider.addAttributes([
            QgsField('id', QVariant.Int),
            QgsField('name', QVariant.String),
            QgsField('population', QVariant.Int),
            QgsField('mmi', QVariant.Double),
            QgsField('dist_to', QVariant.Double),
            QgsField('dir_to', QVariant.Double),
            QgsField('dir_from', QVariant.Double),
            QgsField('roman', QVariant.String),
            QgsField('colour', QVariant.String)])
        myCities = self.localCityFeatures()
        myResult = myMemoryProvider.addFeatures(myCities)
        if not myResult:
            LOGGER.exception('Unable to add features to cities memory layer')
            raise CityMemoryLayerCreationError(
                'Could not add any features to cities memory layer.')

        myMemoryLayer.commitChanges()
        myMemoryLayer.updateExtents()

        LOGGER.debug('Feature count of mem layer:  %s' %
                     myMemoryLayer.featureCount())

        return myMemoryLayer

    def citySearchBoxMemoryLayer(self, theForceFlag=False):
        """Return the search boxes used to search for cities as a memory layer.

        This is mainly useful for diagnostic purposes.

        :param theForceFlag: bool (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        :return QgsVectorLayer - A QGIS memory layer
        :raise an exceptions will be propagated
        """
        LOGGER.debug('citySearchBoxMemoryLayer requested.')
        # There is a dependency on localCitiesMemoryLayer so run it first
        if self.searchBoxes is None or theForceFlag:
            self.localCitiesMemoryLayer()
        # Now store the selection in a temporary memory layer
        myMemoryLayer = QgsVectorLayer('Polygon',
                                       'City Search Boxes',
                                       'memory')
        myMemoryProvider = myMemoryLayer.dataProvider()
        # add field defs
        myField = QgsField('cities_found', QVariant.Int)
        myMemoryProvider.addAttributes([myField])
        myFeatures = []
        for mySearchBox in self.searchBoxes:
            myNewFeature = QgsFeature()
            myRectangle = mySearchBox['geometry']
            # noinspection PyArgumentList
            myGeometry = QgsGeometry.fromWkt(myRectangle.asWktPolygon())
            myNewFeature.setGeometry(myGeometry)
            myNewFeature.setAttributes([mySearchBox['city_count']])
            myFeatures.append(myNewFeature)

        myResult = myMemoryProvider.addFeatures(myFeatures)
        if not myResult:
            LOGGER.exception('Unable to add features to city search boxes'
                             'memory layer')
            raise CityMemoryLayerCreationError(
                'Could not add any features to city search boxes memory layer')

        myMemoryLayer.commitChanges()
        myMemoryLayer.updateExtents()

        LOGGER.debug('Feature count of search box mem layer:  %s' %
                     myMemoryLayer.featureCount())

        return myMemoryLayer

    def sortedImpactedCities(self, theCount=5):
        """Return a data structure with place, mmi, pop sorted by mmi then pop.

        :param theCount: int optional limit to how many rows should be
                returned. Defaults to 5 if not specified.
        :returns
            list: An list of dicts containing the sorted cities and their
                attributes. See below for example output.

                [{'dir_from': 16.94407844543457,
                 'dir_to': -163.05592346191406,
                 'roman': 'II',
                 'dist_to': 2.504295825958252,
                 'mmi': 1.909999966621399,
                 'name': 'Tondano',
                 'id': 57,
                 'population': 33317}]

        Straw man illustrating how sorting is done:

        m = [
             {'name': 'b', 'mmi': 10,  'pop':10},
             {'name': 'a', 'mmi': 100, 'pop': 20},
             {'name': 'c', 'mmi': 10, 'pop': 14}]

        sorted(m, key=lambda d: (-d['mmi'], -d['pop'], d['name']))
        Out[10]:
        [{'mmi': 100, 'name': 'a', 'pop': 20},
         {'mmi': 10, 'name': 'c', 'pop': 14},
         {'mmi': 10, 'name': 'b', 'pop': 10}]

        .. note:: self.most_affected_city will also be populated with
            the dictionary of details for the most affected city.

        .. note:: It is possible that there is no affected city! e.g. if
            all nearby cities fall outside of the shake raster.

        """
        myLayer = self.localCitiesMemoryLayer()
        myFields = myLayer.dataProvider().fields()
        myCities = []
        # pylint: disable=W0612
        myCount = 0
        # pylint: enable=W0612
        # Now loop through the db adding selected features to mem layer
        myRequest = QgsFeatureRequest()

        for myFeature in myLayer.getFeatures(myRequest):
            if not myFeature.isValid():
                LOGGER.debug('Skipping feature')
                continue
            myCount += 1
            # calculate the distance and direction from this point
            # to and from the epicenter
            myId = myFeature.id()
            # We should be able to do this:
            # myPlaceName = str(myFeature['name'].toString())
            # But its not working so we do this:
            myPlaceName = str(
                myFeature[myFields.indexFromName('name')].toString())
            myMmi = myFeature[myFields.indexFromName('mmi')].toFloat()[0]
            myPopulation = (
                myFeature[myFields.indexFromName('population')].toInt()[0])
            myRoman = str(
                myFeature[myFields.indexFromName('roman')].toString())
            myDirectionTo = (
                myFeature[myFields.indexFromName('dir_to')].toFloat()[0])
            myDirectionFrom = (
                myFeature[myFields.indexFromName('dir_from')].toFloat()[0])
            myDistanceTo = (
                myFeature[myFields.indexFromName('dist_to')].toFloat()[0])
            myCity = {'id': myId,
                      'name': myPlaceName,
                      'mmi-int': int(myMmi),
                      'mmi': myMmi,
                      'population': myPopulation,
                      'roman': myRoman,
                      'dist_to': myDistanceTo,
                      'dir_to': myDirectionTo,
                      'dir_from': myDirectionFrom}
            myCities.append(myCity)
        LOGGER.debug('%s features added to sorted impacted cities list.')
        #LOGGER.exception(myCities)
        mySortedCities = sorted(myCities,
                                key=lambda d: (
                                    # we want to use whole no's for sort
                                    - d['mmi-int'],
                                    - d['population'],
                                    d['name'],
                                    d['mmi'],  # not decimals
                                    d['roman'],
                                    d['dist_to'],
                                    d['dir_to'],
                                    d['dir_from'],
                                    d['id']))
        # TODO: Assumption that place names are unique is bad....
        if len(mySortedCities) > 0:
            self.mostAffectedCity = mySortedCities[0]
        else:
            self.mostAffectedCity = None
        # Slice off just the top theCount records now
        if len(mySortedCities) > 5:
            mySortedCities = mySortedCities[0: theCount]
        return mySortedCities

    def write_html_table(self, the_file_name, the_table):
        """Write a Table object to disk with a standard header and footer.

        This is a helper function that allows you to easily write a table
        to disk with a standard header and footer. The header contains
        some inlined css markup for our mmi charts which will be ignored
        if you are not using the css classes it defines.

        The bootstrap.css file will also be written to the same directory
        where the table is written.

        :param the_file_name: file name (without full path) .e.g foo.html
        :param the_table: A Table instance.
        :return str: full path to file that was created on disk.
        """
        my_path = os.path.join(shakemapExtractDir(),
                               self.eventId,
                               the_file_name)
        my_html_file = file(my_path, 'wt')
        my_header_file = os.path.join(dataDir(), 'header.html')
        my_footer_file = os.path.join(dataDir(), 'footer.html')
        my_header_file = file(my_header_file, 'rt')
        my_header = my_header_file.read()
        my_header_file.close()
        my_footer_file = file(my_footer_file, 'rt')
        my_footer = my_footer_file.read()
        my_footer_file.close()
        my_html_file.write(my_header)
        my_html_file.write(the_table.toNewlineFreeString())
        my_html_file.write(my_footer)
        my_html_file.close()
        # Also bootstrap gets copied to extract dir
        my_destination = os.path.join(shakemapExtractDir(),
                                      self.eventId,
                                      'bootstrap.css')
        my_source = os.path.join(dataDir(), 'bootstrap.css')
        shutil.copyfile(my_source, my_destination)

        return my_path

    def impacted_cities_table(self, the_count=5):
        """Return a table object of sorted impacted cities.
        :param the_count:optional maximum number of cities to show.
                Default is 5.

        The cities will be listed in the order computed by sortedImpactedCities
        but will only list in the following format:

        +------+--------+-----------------+-----------+
        | Icon | Name   | People Affected | Intensity |
        +======+========+=================+===========+
        | img  | Padang |    2000         |    IV     +
        +------+--------+-----------------+-----------+

        .. note:: Population will be rounded pop / 1000

        The icon img will be an image with an icon showing the relevant colour.

        :return
            two tuple of:
                A Table object (see :func:`safe.impact_functions.tables.Table`)
                A file path to the html file saved to disk.

        :raise
            Propagates any exceptions.
        """
        my_table_data = self.sortedImpactedCities(the_count)
        my_table_body = []
        my_header = TableRow(['',
                              self.tr('Name'),
                              self.tr('Affected (x 1000)'),
                              self.tr('Intensity')],
                             header=True)
        for my_row_data in my_table_data:
            my_intensity = my_row_data['roman']
            my_name = my_row_data['name']
            my_population = int(round(my_row_data['population'] / 1000))
            my_colour = mmi_colour(my_row_data['mmi'])
            my_colour_box = ('<div style="width: 16px; height: 16px;'
                             'background-color: %s"></div>' % my_colour)
            my_row = TableRow([my_colour_box,
                               my_name,
                               my_population,
                               my_intensity])
            my_table_body.append(my_row)

        my_table = Table(my_table_body, header_row=my_header,
                         table_class='table table-striped table-condensed')
        # Also make an html file on disk
        my_path = self.write_html_table(the_file_name='affected-cities.html',
                                        the_table=my_table)

        return my_table, my_path

    def impact_table(self):
        """Create the html listing affected people per mmi interval.

        Expects that calculate impacts has run and set pop affected etc.
        already.

        self.: A dictionary with keys mmi levels and values affected count
                as per the example below. This is typically going to be passed
                from the :func:`calculateImpacts` function defined below.


        Args:
            None

        Returns:
            str: full absolute path to the saved html content.

        Example:
                {2: 0.47386375223673427,
                3: 0.024892573693488258,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0}
        """
        my_header = [
            TableCell(self.tr('Intensity'), header=True)]
        my_affected_row = [
            TableCell(self.tr('People Affected (x 1000)'), header=True)]
        my_impact_row = [
            TableCell(self.tr('Perceived Shaking'), header=True)]
        for my_mmi in range(2, 10):
            my_header.append(
                TableCell(self.romanize(my_mmi),
                          cell_class='mmi-%s' % my_mmi,
                          header=True))
            if my_mmi in self.affectedCounts:
                # noinspection PyTypeChecker
                my_affected_row.append(
                    '%i' % round(self.affectedCounts[my_mmi] / 1000))
            else:
                # noinspection PyTypeChecker
                my_affected_row.append(0.00)

            my_impact_row.append(TableCell(self.mmi_shaking(my_mmi)))

        my_table_body = list()
        my_table_body.append(my_affected_row)
        my_table_body.append(my_impact_row)
        my_table = Table(my_table_body, header_row=my_header,
                         table_class='table table-striped table-condensed')
        my_path = self.write_html_table(the_file_name='impacts.html',
                                        the_table=my_table)
        return my_path

    def calculateImpacts(self,
                         thePopulationRasterPath=None,
                         theForceFlag=False,
                         theAlgorithm='nearest'):
        """Use the SAFE ITB earthquake function to calculate impacts.

        :param thePopulationRasterPath: str optional. see
                :func:`_getPopulationPath` for more details on how the path
                will be resolved if not explicitly given.
        :param theForceFlag:bool - (Optional). Whether to force the
                regeneration of contour product. Defaults to False.
        :param theAlgorithm: str - (Optional) Which interpolation algorithm to
                use to create the underlying raster. see
                :func:`mmiToRasterData` for information about default
                behaviour
        :returns
            str: the path to the computed impact file.
                The class members self.impact_file, self.fatality_counts,
                self.displaced_counts and self.affected_counts will be
                populated.
                self.*Counts are dicts containing fatality / displaced /
                affected counts for the shake events. Keys for the dict will be
                MMI classes (I-X) and values will be count type for that class.
            str: Path to the html report showing a table of affected people per
                mmi interval.
        """
        if (
                thePopulationRasterPath is None or (
                not os.path.isfile(thePopulationRasterPath) and not
                os.path.islink(thePopulationRasterPath))):

            myExposurePath = self._getPopulationPath()
        else:
            myExposurePath = thePopulationRasterPath

        myHazardPath = self.mmiDataToRaster(
            theForceFlag=theForceFlag,
            theAlgorithm=theAlgorithm)

        myClippedHazard, myClippedExposure = self.clipLayers(
            theShakeRasterPath=myHazardPath,
            thePopulationRasterPath=myExposurePath)

        myClippedHazardLayer = safe_read_layer(
            str(myClippedHazard.source()))
        myClippedExposureLayer = safe_read_layer(
            str(myClippedExposure.source()))
        myLayers = [myClippedHazardLayer, myClippedExposureLayer]

        myFunctionId = 'I T B Fatality Function'
        myFunction = safe_get_plugins(myFunctionId)[0][myFunctionId]

        myResult = safe_calculate_impact(myLayers, myFunction)
        try:
            myFatalities = myResult.keywords['fatalites_per_mmi']
            myAffected = myResult.keywords['exposed_per_mmi']
            myDisplaced = myResult.keywords['displaced_per_mmi']
            myTotalFatalities = myResult.keywords['total_fatalities']
        except:
            LOGGER.exception(
                'Fatalities_per_mmi key not found in:\n%s' %
                myResult.keywords)
            raise
        # Copy the impact layer into our extract dir.
        myTifPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'impact-%s.tif' % theAlgorithm)
        shutil.copyfile(myResult.filename, myTifPath)
        LOGGER.debug('Copied impact result to:\n%s\n' % myTifPath)
        # Copy the impact keywords layer into our extract dir.
        myKeywordsPath = os.path.join(
            shakemapExtractDir(),
            self.eventId,
            'impact-%s.keywords' % theAlgorithm)
        myKeywordsSource = os.path.splitext(myResult.filename)[0]
        myKeywordsSource = '%s.keywords' % myKeywordsSource
        shutil.copyfile(myKeywordsSource, myKeywordsPath)
        LOGGER.debug('Copied impact keywords to:\n%s\n' % myKeywordsPath)

        self.impactFile = myTifPath
        self.impactKeywordsFile = myKeywordsPath
        self.fatalityCounts = myFatalities
        self.fatalityTotal = myTotalFatalities
        self.displacedCounts = myDisplaced
        self.affectedCounts = myAffected
        LOGGER.info('***** Fatalities: %s ********' % self.fatalityCounts)
        LOGGER.info('***** Displaced: %s ********' % self.displacedCounts)
        LOGGER.info('***** Affected: %s ********' % self.affectedCounts)

        myImpactTablePath = self.impact_table()
        return self.impactFile, myImpactTablePath

    def clipLayers(self, theShakeRasterPath, thePopulationRasterPath):
        """Clip population (exposure) layer to dimensions of shake data.

        It is possible (though unlikely) that the shake may be clipped too.

        :param theShakeRasterPath: Path to the shake raster.
        :param thePopulationRasterPath: Path to the population raster.
        :return
            str, str: Path to the clipped datasets (clipped shake, clipped
            pop).
        :raise
            FileNotFoundError
        """

        # _ is a syntactical trick to ignore second returned value
        myBaseName, _ = os.path.splitext(theShakeRasterPath)
        myHazardLayer = QgsRasterLayer(theShakeRasterPath, myBaseName)
        myBaseName, _ = os.path.splitext(thePopulationRasterPath)
        myExposureLayer = QgsRasterLayer(thePopulationRasterPath, myBaseName)

        # Reproject all extents to EPSG:4326 if needed
        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        # Get the Hazard extents as an array in EPSG:4326
        # Note that we will always clip to this extent regardless of
        # whether the exposure layer completely covers it. This differs
        # from safe_qgis which takes care to ensure that the two layers
        # have coincidental coverage before clipping. The
        # clipper function will take care to null padd any missing data.
        myHazardGeoExtent = extent_to_geoarray(
            myHazardLayer.extent(),
            myHazardLayer.crs())

        # Next work out the ideal spatial resolution for rasters
        # in the analysis. If layers are not native WGS84, we estimate
        # this based on the geographic extents
        # rather than the layers native extents so that we can pass
        # the ideal WGS84 cell size and extents to the layer prep routines
        # and do all preprocessing in a single operation.
        # All this is done in the function getWGS84resolution
        extraExposureKeywords = {}

        # Hazard layer is raster
        myHazardGeoCellSize = getWGS84resolution(myHazardLayer)

        # In case of two raster layers establish common resolution
        myExposureGeoCellSize = getWGS84resolution(myExposureLayer)

        if myHazardGeoCellSize < myExposureGeoCellSize:
            myCellSize = myHazardGeoCellSize
        else:
            myCellSize = myExposureGeoCellSize

        # Record native resolution to allow rescaling of exposure data
        if not numpy.allclose(myCellSize, myExposureGeoCellSize):
            extraExposureKeywords['resolution'] = myExposureGeoCellSize

        # The extents should already be correct but the cell size may need
        # resampling, so we pass the hazard layer to the clipper
        myClippedHazard = clip_layer(
            layer=myHazardLayer,
            extent=myHazardGeoExtent,
            cell_size=myCellSize)

        myClippedExposure = clip_layer(
            layer=myExposureLayer,
            extent=myHazardGeoExtent,
            cell_size=myCellSize,
            extra_keywords=extraExposureKeywords)

        return myClippedHazard, myClippedExposure

    def _getPopulationPath(self):
        """Helper to determine population raster spath.

        The following priority will be used to determine the path:
            1) the class attribute self.populationRasterPath
                will be checked and if not None it will be used.
            2) the environment variable 'INASAFE_POPULATION_PATH' will be
               checked if set it will be used.
            4) A hard coded path of
               :file:`/fixtures/exposure/population.tif` will be appended
               to os.path.abspath(os.path.curdir)
            5) A hard coded path of
               :file:`/usr/local/share/inasafe/exposure/population.tif`
               will be used.

        Args:
            None
        Returns:
            str - path to a population raster file.
        Raises:
            FileNotFoundError

        TODO: Consider automatically fetching from
        http://web.clas.ufl.edu/users/atatem/pub/IDN.7z

        Also see http://web.clas.ufl.edu/users/atatem/pub/
        https://github.com/AIFDR/inasafe/issues/381
        """
        # When used via the scripts make_shakemap.sh
        myFixturePath = os.path.join(
            dataDir(), 'exposure', 'population.tif')

        myLocalPath = '/usr/local/share/inasafe/exposure/population.tif'
        if self.populationRasterPath is not None:
            return self.populationRasterPath
        elif 'INASAFE_POPULATION_PATH' in os.environ:
            return os.environ['INASAFE_POPULATION_PATH']
        elif os.path.exists(myFixturePath):
            return myFixturePath
        elif os.path.exists(myLocalPath):
            return myLocalPath
        else:
            raise FileNotFoundError('Population file could not be found')

    def renderMap(self, theForceFlag=False):
        """This is the 'do it all' method to render a pdf.

        :param theForceFlag: bool - (Optional). Whether to force the
                regeneration of map product. Defaults to False.
        :return str - path to rendered pdf.
        :raise Propagates any exceptions.
        """
        myPdfPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 '%s-%s.pdf' % (self.eventId, self.locale))
        myImagePath = os.path.join(shakemapExtractDir(),
                                   self.eventId,
                                   '%s-%s.png' % (self.eventId, self.locale))
        myThumbnailImagePath = os.path.join(shakemapExtractDir(),
                                            self.eventId,
                                            '%s-thumb-%s.png' % (
                                            self.eventId, self.locale))
        pickle_path = os.path.join(
            shakemapExtractDir(),
            self.eventId,
            '%s-metadata-%s.pickle' % (self.eventId, self.locale))

        if not theForceFlag:
            # Check if the images already exist and if so
            # short circuit.
            myShortCircuitFlag = True
            if not os.path.exists(myPdfPath):
                myShortCircuitFlag = False
            if not os.path.exists(myImagePath):
                myShortCircuitFlag = False
            if not os.path.exists(myThumbnailImagePath):
                myShortCircuitFlag = False
            if myShortCircuitFlag:
                LOGGER.info('%s (already exists)' % myPdfPath)
                LOGGER.info('%s (already exists)' % myImagePath)
                LOGGER.info('%s (already exists)' % myThumbnailImagePath)
                return myPdfPath

        # Make sure the map layers have all been removed before we
        # start otherwise in batch mode we will get overdraws.
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        myMmiShapeFile = self.mmiDataToShapefile(theForceFlag=theForceFlag)
        logging.info('Created: %s', myMmiShapeFile)
        myCitiesHtmlPath = None
        myCitiesShapeFile = None

        # 'average', 'invdist', 'nearest' - currently only nearest works
        myAlgorithm = 'nearest'
        try:
            myContoursShapeFile = self.mmiDataToContours(
                theForceFlag=theForceFlag,
                theAlgorithm=myAlgorithm)
        except:
            raise
        logging.info('Created: %s', myContoursShapeFile)
        try:
            myCitiesShapeFile = self.citiesToShapefile(
                theForceFlag=theForceFlag)
            logging.info('Created: %s', myCitiesShapeFile)
            mySearchBoxFile = self.citySearchBoxesToShapefile(
                theForceFlag=theForceFlag)
            logging.info('Created: %s', mySearchBoxFile)
            _, myCitiesHtmlPath = self.impacted_cities_table()
            logging.info('Created: %s', myCitiesHtmlPath)
        except:  # pylint: disable=W0702
            logging.exception('No nearby cities found!')

        _, myImpactsHtmlPath = self.calculateImpacts()
        logging.info('Created: %s', myImpactsHtmlPath)

        # Load our project
        if 'INSAFE_REALTIME_PROJECT' in os.environ:
            myProjectPath = os.environ['INSAFE_REALTIME_PROJECT']
        else:
            myProjectPath = os.path.join(dataDir(), 'realtime.qgs')
        # noinspection PyArgumentList
        QgsProject.instance().setFileName(myProjectPath)
        # noinspection PyArgumentList
        QgsProject.instance().read()

        if 'INSAFE_REALTIME_TEMPLATE' in os.environ:
            myTemplatePath = os.environ['INSAFE_REALTIME_TEMPLATE']
        else:
            myTemplatePath = os.path.join(dataDir(), 'realtime-template.qpt')

        myTemplateFile = file(myTemplatePath, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()

        myDocument = QDomDocument()
        myDocument.setContent(myTemplateContent)

        # Set up the map renderer that will be assigned to the composition
        myMapRenderer = QgsMapRenderer()
        # Set the labelling engine for the canvas
        myLabellingEngine = QgsPalLabeling()
        myMapRenderer.setLabelingEngine(myLabellingEngine)

        # Enable on the fly CRS transformations
        myMapRenderer.setProjectionsEnabled(False)
        # Now set up the composition
        myComposition = QgsComposition(myMapRenderer)

        # You can use this to replace any string like this [key]
        # in the template with a new value. e.g. to replace
        # [date] pass a map like this {'date': '1 Jan 2012'}
        myLocationInfo = self.eventInfo()
        LOGGER.debug(myLocationInfo)
        mySubstitutionMap = {'location-info': myLocationInfo,
                             'version': self.version()}
        mySubstitutionMap.update(self.eventDict())
        LOGGER.debug(mySubstitutionMap)

        pickle_file = file(pickle_path, 'w')
        pickle.dump(mySubstitutionMap, pickle_file)
        pickle_file.close()

        myResult = myComposition.loadFromTemplate(myDocument,
                                                  mySubstitutionMap)
        if not myResult:
            LOGGER.exception('Error loading template %s with keywords\n %s',
                             myTemplatePath, mySubstitutionMap)
            raise MapComposerError

        # Get the main map canvas on the composition and set
        # its extents to the event.
        myMap = myComposition.getComposerMapById(0)
        if myMap is not None:
            myMap.setNewExtent(self.extentWithCities)
            myMap.renderModeUpdateCachedImage()
        else:
            LOGGER.exception('Map 0 could not be found in template %s',
                             myTemplatePath)
            raise MapComposerError

        # Set the impacts report up
        myImpactsItem = myComposition.getComposerItemById(
            'impacts-table')
        if myImpactsItem is None:
            myMessage = 'impacts-table composer item could not be found'
            LOGGER.exception(myMessage)
            raise MapComposerError(myMessage)
        myImpactsHtml = myComposition.getComposerHtmlByItem(
            myImpactsItem)
        if myImpactsHtml is None:
            myMessage = 'Impacts QgsComposerHtml could not be found'
            LOGGER.exception(myMessage)
            raise MapComposerError(myMessage)
        myImpactsHtml.setUrl(QUrl(myImpactsHtmlPath))

        # Set the affected cities report up
        myCitiesItem = myComposition.getComposerItemById('affected-cities')
        if myCitiesItem is None:
            myMessage = 'affected-cities composer item could not be found'
            LOGGER.exception(myMessage)
            raise MapComposerError(myMessage)
        myCitiesHtml = myComposition.getComposerHtmlByItem(myCitiesItem)
        if myCitiesHtml is None:
            myMessage = 'Cities QgsComposerHtml could not be found'
            LOGGER.exception(myMessage)
            raise MapComposerError(myMessage)

        if myCitiesHtmlPath is not None:
            myCitiesHtml.setUrl(QUrl(myCitiesHtmlPath))
        else:
            # We used to raise an error here but it is actually feasible that
            # no nearby cities with a valid mmi value are found - e.g.
            # if the event is way out in the ocean.
            LOGGER.info('No nearby cities found.')

        # Load the contours and cities shapefile into the map
        myContoursLayer = QgsVectorLayer(
            myContoursShapeFile,
            'mmi-contours', "ogr")
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([myContoursLayer])

        myCitiesLayer = None
        if myCitiesShapeFile is not None:
            myCitiesLayer = QgsVectorLayer(
                myCitiesShapeFile,
                'mmi-cities', "ogr")
            if myCitiesLayer.isValid():
                # noinspection PyArgumentList
                QgsMapLayerRegistry.instance().addMapLayers([myCitiesLayer])

        # Now add our layers to the renderer so they appear in the print out
        myLayers = reversed(CANVAS.layers())
        myLayerList = []
        for myLayer in myLayers:
            myLayerList.append(myLayer.id())

        myLayerList.append(myContoursLayer.id())
        if myCitiesLayer is not None and myCitiesLayer.isValid():
            myLayerList.append(myCitiesLayer.id())

        myMapRenderer.setLayerSet(myLayerList)
        LOGGER.info(str(myLayerList))

        # Save a pdf.
        myComposition.exportAsPDF(myPdfPath)
        LOGGER.info('Generated PDF: %s' % myPdfPath)
        # Save a png
        myPageNumber = 0
        myImage = myComposition.printPageAsRaster(myPageNumber)
        myImage.save(myImagePath)
        LOGGER.info('Generated Image: %s' % myImagePath)
        # Save a thumbnail
        mySize = QSize(200, 200)
        myThumbnailImage = myImage.scaled(
            mySize, Qt.KeepAspectRatioByExpanding)
        myThumbnailImage.save(myThumbnailImagePath)
        LOGGER.info('Generated Thumbnail: %s' % myThumbnailImagePath)

        # Save a QGIS Composer template that you can open in QGIS
        myTemplateDocument = QDomDocument()
        myElement = myTemplateDocument.createElement('Composer')
        myComposition.writeXML(
            myElement, myTemplateDocument)
        myTemplateDocument.appendChild(myElement)
        myTemplatePath = os.path.join(
            shakemapExtractDir(),
            self.eventId,
            'composer-template.qpt')
        myFile = file(myTemplatePath, 'wt')
        myFile.write(myTemplateDocument.toByteArray())
        myFile.close()

        # Save a QGIS project that you can open in QGIS
        # noinspection PyArgumentList
        myProject = QgsProject.instance()
        myProjectPath = os.path.join(
            shakemapExtractDir(),
            self.eventId,
            'project.qgs')
        myProject.write(QFileInfo(myProjectPath))

    def bearingToCardinal(self, theBearing):
        """Given a bearing in degrees return it as compass units e.g. SSE.

        :param theBearing: theBearing float (required)
        :return str Compass bearing derived from theBearing or None if
            theBearing is None or can not be resolved to a float.

        .. note:: This method is heavily based on http://hoegners.de/Maxi/geo/
           which is licensed under the GPL V3.
        """
        myDirectionList = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW',
                           'NW', 'NNW']
        try:
            myBearing = float(theBearing)
        except ValueError:
            LOGGER.exception('Error casting bearing to a float')
            return None

        myDirectionsCount = len(myDirectionList)
        myDirectionsInterval = 360. / myDirectionsCount
        myIndex = int(round(myBearing / myDirectionsInterval))
        myIndex %= myDirectionsCount
        return myDirectionList[myIndex]

    def eventInfo(self):
        """Get a short paragraph describing the event.

        Args:
            None

        Returns:
            str: A string describing the event e.g.
                'M 5.0 26-7-2012 2:15:35 Latitude: 0°12'36.00"S
                 Longitude: 124°27'0.00"E Depth: 11.0km
                 Located 2.50km SSW of Tondano'
        Raises:
            None
        """
        myDict = self.eventDict()
        myString = ('M %(mmi)s %(date)s %(time)s '
                    '%(latitude-name)s: %(latitude-value)s '
                    '%(longitude-name)s: %(longitude-value)s '
                    '%(depth-name)s: %(depth-value)s%(depth-unit)s '
                    '%(located-label)s %(distance)s%(distance-unit)s '
                    '%(bearing-compass)s '
                    '%(direction-relation)s %(place-name)s') % myDict
        return myString

    def eventDict(self):
        """Get a dict of key value pairs that describe the event.

        Args:

        Returns:
            dict: key-value pairs describing the event.

        Raises:
            propagates any exceptions

        """
        myMapName = self.tr('Estimated Earthquake Impact')
        myExposureTableName = self.tr(
            'Estimated number of people affected by each MMI level')
        myFatalitiesName = self.tr('Estimated fatalities')
        myFatalitiesCount = self.fatalityTotal

        # put the estimate into neat ranges 0-100, 100-1000, 1000-10000. etc
        myLowerLimit = 0
        myUpperLimit = 100
        while myFatalitiesCount > myUpperLimit:
            myLowerLimit = myUpperLimit
            myUpperLimit = math.pow(myUpperLimit, 2)
        myFatalitiesRange = '%i - %i' % (myLowerLimit, myUpperLimit)

        myCityTableName = self.tr('Places Affected')
        myLegendName = self.tr('Population density')
        myLimitations = self.tr(
            'This impact estimation is automatically generated and only takes'
            ' into account the population and cities affected by different '
            'levels of ground shaking. The estimate is based on ground '
            'shaking data from BMKG, population density data from asiapop'
            '.org, place information from geonames.org and software developed'
            ' by BNPB. Limitations in the estimates of ground shaking, '
            'population  data and place names datasets may result in '
            'significant misrepresentation of the on-the-ground situation in '
            'the figures shown here. Consequently decisions should not be '
            'made solely on the information presented here and should always '
            'be verified by ground truthing and other reliable information '
            'sources. The fatality calculation assumes that '
            'no fatalities occur for shake levels below MMI 4. Fatality '
            'counts of less than 50 are disregarded.')
        myCredits = self.tr(
            'Supported by the Australia-Indonesia Facility for Disaster '
            'Reduction, Geoscience Australia and the World Bank-GFDRR.')
        #Format the lat lon from decimal degrees to dms
        myPoint = QgsPoint(self.longitude, self.latitude)
        myCoordinates = myPoint.toDegreesMinutesSeconds(2)
        myTokens = myCoordinates.split(',')
        myLongitude = myTokens[0]
        myLatitude = myTokens[1]
        myKmText = self.tr('km')
        myDirectionalityText = self.tr('of')
        myBearingText = self.tr('bearing')
        LOGGER.debug(myLongitude)
        LOGGER.debug(myLatitude)
        if self.mostAffectedCity is None:
            # Check why we have this line - perhaps setting class state?
            self.sortedImpactedCities()
            myDirection = 0
            myDistance = 0
            myKeyCityName = self.tr('n/a')
            myBearing = self.tr('n/a')
        else:
            myDirection = self.mostAffectedCity['dir_to']
            myDistance = self.mostAffectedCity['dist_to']
            myKeyCityName = self.mostAffectedCity['name']
            myBearing = self.bearingToCardinal(myDirection)

        myElapsedTimeText = self.tr('Elapsed time since event')
        myElapsedTime = self.elapsedTime()[1]
        myDegreeSymbol = '\xb0'
        myDict = {
            'map-name': myMapName,
            'exposure-table-name': myExposureTableName,
            'city-table-name': myCityTableName,
            'legend-name': myLegendName,
            'limitations': myLimitations,
            'credits': myCredits,
            'fatalities-name': myFatalitiesName,
            'fatalities-range': myFatalitiesRange,
            'fatalities-count': '%s' % myFatalitiesCount,
            'mmi': '%s' % self.magnitude,
            'date': '%s-%s-%s' % (
                self.day, self.month, self.year),
            'time': '%s:%s:%s' % (
                self.hour, self.minute, self.second),
            'formatted-date-time': self.elapsedTime()[0],
            'latitude-name': self.tr('Latitude'),
            'latitude-value': '%s' % myLatitude,
            'longitude-name': self.tr('Longitude'),
            'longitude-value': '%s' % myLongitude,
            'depth-name': self.tr('Depth'),
            'depth-value': '%s' % self.depth,
            'depth-unit': myKmText,
            'located-label': self.tr('Located'),
            'distance': '%.2f' % myDistance,
            'distance-unit': myKmText,
            'direction-relation': myDirectionalityText,
            'bearing-degrees': '%.2f%s' % (myDirection, myDegreeSymbol),
            'bearing-compass': '%s' % myBearing,
            'bearing-text': myBearingText,
            'place-name': myKeyCityName,
            'elapsed-time-name': myElapsedTimeText,
            'elapsed-time': myElapsedTime
        }
        return myDict

    def elapsedTime(self):
        """Calculate how much time has elapsed since the event.

        Args:
            None

        Returns:
            str - local formatted date

        Raises:
            None

        .. note:: Code based on Ole's original impact_map work.
        """
        # Work out interval since earthquake (assume both are GMT)
        year = self.year
        month = self.month
        day = self.day
        hour = self.hour
        minute = self.minute
        second = self.second

        eq_date = datetime(year, month, day, hour, minute, second)

        # Hack - remove when ticket:10 has been resolved
        tz = pytz.timezone('Asia/Jakarta')  # Or 'Etc/GMT+7'
        now = datetime.utcnow()
        now_jakarta = now.replace(tzinfo=pytz.utc).astimezone(tz)
        eq_jakarta = eq_date.replace(tzinfo=tz).astimezone(tz)
        time_delta = now_jakarta - eq_jakarta

        # Work out string to report time elapsed after quake
        if time_delta.days == 0:
            # This is within the first day after the quake
            hours = int(time_delta.seconds / 3600)
            minutes = int((time_delta.seconds % 3600) / 60)

            if hours == 0:
                lapse_string = '%i %s' % (minutes, self.tr('minute(s)'))
            else:
                lapse_string = '%i %s %i %s' % (hours,
                                                self.tr('hour(s)'),
                                                minutes,
                                                self.tr('minute(s)'))
        else:
            # This at least one day after the quake

            weeks = int(time_delta.days / 7)
            days = int(time_delta.days % 7)

            if weeks == 0:
                lapse_string = '%i %s' % (days, self.tr('days'))
            else:
                lapse_string = '%i %s %i %s' % (weeks,
                                                self.tr('weeks'),
                                                days,
                                                self.tr('days'))

        # Convert date to GMT+7
        # FIXME (Ole) Hack - Remove this as the shakemap data always
        # reports the time in GMT+7 but the timezone as GMT.
        # This is the topic of ticket:10
        #tz = pytz.timezone('Asia/Jakarta')  # Or 'Etc/GMT+7'
        #eq_date_jakarta = eq_date.replace(tzinfo=pytz.utc).astimezone(tz)
        eq_date_jakarta = eq_date

        # The character %b will use the local word for month
        # However, setting the locale explicitly to test, does not work.
        #locale.setlocale(locale.LC_TIME, 'id_ID')

        date_str = eq_date_jakarta.strftime('%d-%b-%y %H:%M:%S %Z')
        return date_str, lapse_string

    def version(self):
        """Return a string showing the version of Inasafe.

        Args: None

        Returns: str
        """
        return self.tr('Version: %s' % get_version())

    def getCityById(self, theId):
        """A helper to get the info of an affected city given it's id.

        :param theId: int mandatory, the id number of the city to retrieve.
        :return dict: various properties for the given city including distance
                from the epicenter and direction to and from the epicenter.
        """

    def __str__(self):
        """The unicode representation for an event object's state.

        Args: None

        Returns: str A string describing the ShakeEvent instance

        Raises: None
        """
        if self.extentWithCities is not None:
            # noinspection PyUnresolvedReferences
            myExtentWithCities = self.extentWithCities.asWktPolygon()
        else:
            myExtentWithCities = 'Not set'

        if self.mmiData:
            mmiData = 'Populated'
        else:
            mmiData = 'Not populated'

        myDict = {'latitude': self.latitude,
                  'longitude': self.longitude,
                  'eventId': self.eventId,
                  'magnitude': self.magnitude,
                  'depth': self.depth,
                  'description': self.description,
                  'location': self.location,
                  'day': self.day,
                  'month': self.month,
                  'year': self.year,
                  'time': self.time,
                  'time_zone': self.timeZone,
                  'x_minimum': self.xMinimum,
                  'x_maximum': self.xMaximum,
                  'y_minimum': self.yMinimum,
                  'y_maximum': self.yMaximum,
                  'rows': self.rows,
                  'columns': self.columns,
                  'mmi_data': mmiData,
                  'populationRasterPath': self.populationRasterPath,
                  'impact_file': self.impactFile,
                  'impact_keywords_file': self.impactKeywordsFile,
                  'fatality_counts': self.fatalityCounts,
                  'displaced_counts': self.displacedCounts,
                  'affected_counts': self.affectedCounts,
                  'extent_with_cities': myExtentWithCities,
                  'zoom_factor': self.zoomFactor,
                  'search_boxes': self.searchBoxes}

        myString = (
            'latitude: %(latitude)s\n'
            'longitude: %(longitude)s\n'
            'eventId: %(eventId)s\n'
            'magnitude: %(magnitude)s\n'
            'depth: %(depth)s\n'
            'description: %(description)s\n'
            'location: %(location)s\n'
            'day: %(day)s\n'
            'month: %(month)s\n'
            'year: %(year)s\n'
            'time: %(time)s\n'
            'time_zone: %(time_zone)s\n'
            'x_minimum: %(x_minimum)s\n'
            'x_maximum: %(x_maximum)s\n'
            'y_minimum: %(y_minimum)s\n'
            'y_maximum: %(y_maximum)s\n'
            'rows: %(rows)s\n'
            'columns: %(columns)s\n'
            'mmi_data: %(mmi_data)s\n'
            'populationRasterPath: %(populationRasterPath)s\n'
            'impact_file: %(impact_file)s\n'
            'impact_keywords_file: %(impact_keywords_file)s\n'
            'fatality_counts: %(fatality_counts)s\n'
            'displaced_counts: %(displaced_counts)s\n'
            'affected_counts: %(affected_counts)s\n'
            'extent_with_cities: %(extent_with_cities)s\n'
            'zoom_factor: %(zoom_factor)s\n'
            'search_boxes: %(search_boxes)s\n'
            % myDict)
        return myString

    def setupI18n(self):
        """Setup internationalisation for the reports.

        Args:
           None
        Returns:
           None.
        Raises:
           TranslationLoadException
        """
        myLocaleName = self.locale
        # Also set the system locale to the user overridden local
        # so that the inasafe library functions gettext will work
        # .. see:: :py:func:`common.utilities`
        os.environ['LANG'] = str(myLocaleName)

        myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        myTranslationPath = os.path.join(
            myRoot, 'safe_qgis', 'i18n',
            'inasafe_' + str(myLocaleName) + '.qm')
        if os.path.exists(myTranslationPath):
            self.translator = QTranslator()
            myResult = self.translator.load(myTranslationPath)
            LOGGER.debug('Switched locale to %s' % myTranslationPath)
            if not myResult:
                myMessage = 'Failed to load translation for %s' % myLocaleName
                LOGGER.exception(myMessage)
                raise TranslationLoadError(myMessage)
            # noinspection PyTypeChecker
            QCoreApplication.installTranslator(self.translator)
        else:
            if myLocaleName != 'en':
                myMessage = 'No translation exists for %s' % myLocaleName
                LOGGER.exception(myMessage)
