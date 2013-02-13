# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake events.**

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

import ogr
import gdal
from gdalconst import GA_ReadOnly


# TODO I think QCoreApplication is needed for tr() check hefore removing
from PyQt4.QtCore import (QString,
                          QStringList
                          )
from qgis.core import (QgsVectorFileWriter,
                       QgsCoordinateReferenceSystem)
#TODO refactor this into a utility class as it is no longer only used by test
from realtime.utils import shakemapExtractDir, dataDir
from realtime.rt_exceptions import (GridXmlFileNotFoundError,
                                    GridXmlParseError,
                                    ContourCreationError,
                                    InvalidLayerError,
                                    ShapefileCreationError)

# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')


class ShakeEvent():
    """The ShakeEvent class encapsulates behaviour and data relating to an
    earthquake, including epicenter, magnitude etc."""

    def __init__(self, gridXMLPath):
        """Constructor for the shake event class.

        Args:
            * theForceFlag: bool Whether to force retrieval of the dataset from
                the ftp server.

        Returns: Instance

        Raises: EventXmlParseError
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
        self.timeZone = None
        self.xMinimum = None
        self.xMaximum = None
        self.yMinimum = None
        self.yMaximum = None
        self.rows = None
        self.columns = None
        self.mmiData = None
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
        # The search boxes used to find extentWithCities
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
        self.outputPath = None
        self.gridXmlPath = gridXMLPath
        self.parseGridXml()

    def setOutputDirectory(self, outputPathDir):
        """Set output
        """

    def extractDateTime(self, theTimeStamp):
        """Extract the parts of a date given a timestamp as per below example.

        Args:
            theTimeStamp: str - as provided by the 'event_timestamp'
                attribute in the grid.xml.

        Returns:
            None

        Raises:
            None

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
        print myPath
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
            # Extract the 1,2 and 5th (MMI) columns and populate mmiData
            myLonColumn = 0
            myLatColumn = 1
            myMMIColumn = 4
            self.mmiData = []
            for myLine in myData.split('\n'):
                # print myLine
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
            raise GridXmlParseError('Failed to parse grid file.\n%s\n%s'
                                    % (e.__class__, str(e)))

    def gridFilePath(self):
        if os.path.isfile(self.gridXmlPath):
            return self.gridXmlPath
        else:
            raise GridXmlFileNotFoundError

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
        """Save the mmiData to a delimited text file suitable for processing
        with gdal_grid.

        The output file will be of the same format as strings returned from
        :func:`mmiDataToDelimitedText`.

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
        LOGGER.debug('mmiDataToDelimitedText requested.')

        myPath = os.path.join(shakemapExtractDir(),
                              'mmi.csv')
        #short circuit if the csv is already created.
        if os.path.exists(myPath) and theForceFlag is not True:
            return myPath
        myFile = file(myPath, 'wt')
        myFile.write(self.mmiDataToDelimitedText())
        myFile.close()

        # Also write the .csv which contains metadata about field types
        myCsvPath = os.path.join(shakemapExtractDir(),
                                 'mmi.csvt')
        myFile = file(myCsvPath, 'wt')
        myFile.write('"Real","Real","Real"')
        myFile.close()
        return myPath

    def mmiDataToVrt(self, theForceFlag=True):
        """Save the mmiData to an ogr vrt text file.

        Args: theForceFlag bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.

        Returns: str The absolute file system path to the .vrt text file.

        Raises: None
        """
        # Ensure the delimited mmi file exists
        LOGGER.debug('mmiDataToVrt requested.')

        myVrtPath = os.path.join(shakemapExtractDir(),
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

        Raises: Any exceptions will be propogated.
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

        Example of the ogr2ogr call we generate::

           ogr2ogr -select mmi -a_srs EPSG:4326 mmi.shp mmi.vrt mmi

        .. note:: It is assumed that ogr2ogr is in your path.

        Args: theForceFlag bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.

        Return: str Path to the resulting tif file.

        Raises: None
        """
        LOGGER.debug('mmiDataToShapefile requested.')

        myShpPath = os.path.join(shakemapExtractDir(),
                                 'mmi-points.shp')
        # Short circuit if the tif is already created.
        if os.path.exists(myShpPath) and theForceFlag is not True:
            return myShpPath

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        myVrtPath = self.mmiDataToVrt(theForceFlag)

        #now generate the tif using default interpoation options

        myCommand = (('ogr2ogr -overwrite -select mmi -a_srs EPSG:4326 '
                      '%(shp)s %(vrt)s mmi') % {
                         'shp': myShpPath,
                         'vrt': myVrtPath
                     })

        LOGGER.info('Created this gdal command:\n%s' % myCommand)
        # Now run GDAL warp scottie...
        self._runCommand(myCommand)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 'mmi-points.qml')
        mySourceQml = os.path.join(dataDir(), 'mmi-shape.qml')
        shutil.copyfile(mySourceQml, myQmlPath)
        return myShpPath

    def mmiDataToRaster(self, theForceFlag=False,
                        theAlgorithm='nearest', tifPath=None):
        """Convert the grid.xml's mmi column to a raster using gdal_grid.

        A geotiff file will be created.

        Unfortunately no python bindings exist for doing this so we are
        going to do it using a shell call.

        .. seealso:: http://www.gdal.org/gdal_grid.html

        Example of the gdal_grid call we generate::

           gdal_grid -zfield "mmi" -a invdist:power=2.0:smoothing=1.0 \
           -txe 126.29 130.29 -tye 0.802 4.798 -outsize 400 400 -of GTiff \
           -ot Float16 -l mmi mmi.vrt mmi.tif

        .. note:: It is assumed that gdal_grid is in your path.

        Args:
          theForceFlag bool (Optional). Whether to force the regeneration
            of the output file. Defaults to False.
          theAlgorithm str (Optional). Which resampling algorithm to use.
            vallid options are 'nearest' (for nearest neighbour), 'invdist'
            (for inverse distance), 'average' (for moving average). Defaults
            to 'nearest' if not specified. Note that passing resampling alg
            parameters is currently not supported. If None is passed it will
            be replaced with 'nearest'.


        Return: str Path to the resulting tif file.

        .. note:: For interest you can also make quite beautiful smoothed
          rasters using this:

          gdal_grid -zfield "mmi" -a_srs EPSG:4326
          -a invdist:power=2.0:smoothing=1.0 -txe 122.45 126.45
          -tye -2.21 1.79 -outsize 400 400 -of GTiff
          -ot Float16 -l mmi mmi.vrt mmi-trippy.tif

        Raises: None
        """
        LOGGER.debug('mmiDataToRaster requested.')

        if theAlgorithm is None:
            theAlgorithm = 'nearest'

        myTifPath = os.path.join(shakemapExtractDir(),
                                 'mmi-%s.tif' % theAlgorithm)
        #short circuit if the tif is already created.
        if os.path.exists(myTifPath) and theForceFlag is not True:
            return myTifPath

        # Ensure the vrt mmi file exists (it will generate csv too if needed)
        myVrtPath = self.mmiDataToVrt(theForceFlag)

        # now generate the tif using default nearest neighbour interpoation
        # options. This gives us the same output as the mi.grd generated by
        # the earthquake server.

        if 'invdist' in theAlgorithm:
            myAlgorithm = 'invdist:power=2.0:smoothing=1.0'
        else:
            myAlgorithm = theAlgorithm

        myCommand = (('gdal_grid -a %(alg)s -zfield "mmi" -txe %(xMin)s '
                      '%(xMax)s -tye %(yMin)s %(yMax)s -outsize %(dimX)i '
                      '%(dimY)i -of GTiff -ot Float16 -a_srs EPSG:4326 -l mmi '
                      '%(vrt)s %(tif)s') % {
                         'alg': myAlgorithm,
                         'xMin': self.xMinimum,
                         'xMax': self.xMaximum,
                         'yMin': self.yMinimum,
                         'yMax': self.yMaximum,
                         'dimX': self.columns,
                         'dimY': self.rows,
                         'vrt': myVrtPath,
                         'tif': myTifPath
                     })

        LOGGER.info('Created this gdal command:\n%s' % myCommand)
        # Now run GDAL warp scottie...
        self._runCommand(myCommand)

        # copy the keywords file from fixtures for this layer
        myKeywordPath = os.path.join(shakemapExtractDir(),
                                     'mmi-%s.keywords' % theAlgorithm)
        mySourceKeywords = os.path.join(dataDir(), 'mmi.keywords')
        shutil.copyfile(mySourceKeywords, myKeywordPath)
        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 'mmi-%s.qml' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi.qml')
        shutil.copyfile(mySourceQml, myQmlPath)
        return myTifPath

    def mmiDataToContours(self, theForceFlag=True, theAlgorithm='nearest'):
        """Extract contours from the event's tif file.

        Contours are extracted at a 0.5 MMI interval. The resulting file will
        be saved in the extract directory. In the easiest use case you can
        simply do::

           myShakeEvent = myShakeData.shakeEvent()
           myContourPath = myShakeEvent.mmiToContours()

        which will return the contour dataset for the latest event on the
        ftp server.

        Args: theForceFlag bool - (Optional). Whether to force the regeneration
                  of contour product. Defaults to False.
              theAlgorithm str - (Optional) Which interpolation algorithm to
                  use to create the underlying raster. Defaults to 'nearest'.
              **Only enforced if theForceFlag is true!**

        Returns: An absolute filesystem path pointing to the generated
            contour dataset.

        Raises: ContourCreationError

        """
        LOGGER.debug('mmiDataToContours requested.')
        # TODO: Use sqlite rather?
        myOutputFileBase = os.path.join(shakemapExtractDir(),
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
                LOGGER.exception('Old contour files not deleted'
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
                                 'mmi-contours-%s.prj' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi-contours.prj')
        shutil.copyfile(mySourceQml, myQmlPath)

        # Lastly copy over the standard qml (QGIS Style file)
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 'mmi-contours-%s.qml' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi-contours.qml')
        shutil.copyfile(mySourceQml, myQmlPath)

        # Now update the additional columns - X,Y, ROMAN and RGB
        try:
            self.setContourProperties(myOutputFile)
        except InvalidLayerError:
            raise

        return myOutputFile

    def memoryLayerToShapefile(self,
                               theFileName,
                               theMemoryLayer,
                               theForceFlag=False):
        """Write a memory layer to a shapefile.

        .. note:: The file will be asved into the shakemap extract dir
           event id folder. If a qml matching theFileName.qml can be
           found it will automatically copied over to the output dir.
           Any existing shp by the same name will be overridden if
           theForceFlag is True, otherwise the existing file will be returned.

        Args:
            theFileName: str filename excluding path and ext. e.g. 'mmi-cities'
            theMemoryLayer: QGIS memory layer instance.
            theForceFlag: bool (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.

        Returns: str Path to the created shapefile

        Raises: ShapefileCreationError
        """
        LOGGER.debug('memoryLayerToShapefile requested.')

        LOGGER.debug(str(theMemoryLayer.dataProvider().attributeIndexes()))
        if theMemoryLayer.featureCount() < 1:
            raise ShapefileCreationError('Memory layer has no features')

        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        myOutputFileBase = os.path.join(shakemapExtractDir(),
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
                LOGGER.exception('Old shape files not deleted'
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
            myActualNewFileName
        )

        if myResult == QgsVectorFileWriter.NoError:
            LOGGER.debug('Wrote mem layer to shp: %s' % myOutputFile)
        else:
            raise ShapefileCreationError(
                'Failed with error: %s' % myResult)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 '%s.qml' % theFileName)
        mySourceQml = os.path.join(dataDir(), '%s.qml' % theFileName)
        shutil.copyfile(mySourceQml, myQmlPath)

        return myOutputFile


if __name__ == '__main__':
    a = ShakeEvent(gridXMLPath='/home/sunnii/Downloads/grid.xml')
    print a.mmiDataToRaster()
    print 'a'