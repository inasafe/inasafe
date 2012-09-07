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
from xml.dom import minidom
from subprocess import call, CalledProcessError
import logging
import numpy

import ogr
import gdal
from gdalconst import GA_ReadOnly

from PyQt4.QtCore import QVariant, QFileInfo, QString, QStringList
from qgis.core import (QgsPoint,
                       QgsField,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsRectangle,
                       QgsDataSourceURI,
                       QgsVectorFileWriter,
                       QgsCoordinateReferenceSystem)

from safe.api import get_plugins as safe_get_plugins
from safe.api import read_layer as safe_read_layer
from safe.api import calculate_impact as safe_calculate_impact
from safe_qgis.safe_interface import getOptimalExtent, getBufferedExtent
from safe_qgis.utilities import getWGS84resolution
from safe_qgis.clipper import extentToGeoArray, clipLayer
from safe_qgis.exceptions import InsufficientOverlapException
from utils import shakemapExtractDir, dataDir
from rt_exceptions import (GridXmlFileNotFoundError,
                           GridXmlParseError,
                           ContourCreationError,
                           InvalidLayerError,
                           CityShapefileCreationError,
                           CityMemoryLayerCreationError,
                           FileNotFoundError)

# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE-Realtime')


class ShakeEvent:
    """The ShakeEvent class encapsulates behaviour and data relating to an
    earthquake, including epicenter, magnitude etc."""

    def __init__(self, theEventId, thePopulationRasterPath=None):
        """Constructor for the shake event class.

        Args:
            theEventId - (Mandatory) Id of the event. Will be used to
                determine the path to an grid.xml file that
                will be used to intialise the state of the ShakeEvent instance.
            thePopulationRasterPath - (Optional) - path to the population raster
                that will be used if you want to calculate the impact. This
                is optional because there are various ways this can be
                specified before calling :func:`calculateFatalities`.
            e.g.

            /tmp/inasafe/realtime/shakemaps-extracted/20120726022003/grid.xml

        Returns: Instance

        Raises: EventXmlParseError
        """
        self.latitude = None
        self.longitude = None
        self.eventId = theEventId
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
        self.impactFile = None
        self.fatalityCounts = None
        # After selecting affected cities near the event, the bbox of
        # shake map + cities
        self.extentWithCities = None
        # how much to iteratively zoom out by when searching for cities
        self.zoomFactor = 2
        self.parseGridXml()

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
            # now separate out its parts
            # >>> e = "2012-08-07T01:55:12WIB"
            #>>> e[0:10]
            #'2012-08-07'
            #>>> e[12:-3]
            #'1:55:12'
            #>>> e[-3:]
            #'WIB'   (WIB = Western Indonesian Time)

            myDateTokens = myTimeStamp[0:10].split('-')
            self.year = int(myDateTokens[0])
            self.month = int(myDateTokens[1])
            self.day = int(myDateTokens[2])
            myTimeTokens = myTimeStamp[12:-3].split(':')
            self.hour = int(myTimeTokens[0])
            self.minute = int(myTimeTokens[1])
            self.second = int(myTimeTokens[2])
            # Note teh timezone here is inconsistent with YZ from grid.xml
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
                              self.eventId,
                              'mmi.csv')
        #short circuit if the csv is already created.
        if os.path.exists(myPath) and theForceFlag is not True:
            return myPath
        myFile = file(myPath, 'wt')
        myFile.write(self.mmiDataToDelimitedText())
        myFile.close()

        # Also write the .csvt which contains metadata about field types
        myCsvtPath = os.path.join(shakemapExtractDir(),
                                  self.eventId,
                                  'mmi.csvt')
        myFile = file(myCsvtPath, 'wt')
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

        Raises: Any exceptions will be propogated.
        """

        myCommand = self._addExecutablePrefix(theCommand)

        try:
            myResult = call(myCommand, shell=True)
            del myResult
        except CalledProcessError, e:
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
        """Convert the grid.xml's mmi column to a vector shp file using ogr2ogr.

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
                                 self.eventId,
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
                                 self.eventId,
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
                      '%(dimX)i -of GTiff -ot Float16 -a_srs EPSG:4326 -l mmi '
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
                                        self.eventId,
                                        'mmi-contours-%s.' % theAlgorithm)
        myOutputFile = myOutputFileBase + 'shp'
        if os.path.exists(myOutputFile) and theForceFlag is not True:
            return myOutputFile
        elif os.path.exists(myOutputFile):
            os.remove(myOutputFileBase + 'shp')
            os.remove(myOutputFileBase + 'shx')
            os.remove(myOutputFileBase + 'dbf')
            os.remove(myOutputFileBase + 'prj')

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
        # So we can fix the x pos to the same x coord as epicenter so
        # labels line up nicely vertically
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

        myTifDataset = gdal.Open(myTifPath, GA_ReadOnly)
        # see http://gdal.org/java/org/gdal/gdal/gdal.html for these options
        myBand = 1
        myContourInterval = 0.5  # MMI not M!
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
            raise ContourCreationError(str(e))
        finally:
            del myTifDataset
            myOgrDataset.Release()
        # Now update the additional columns - X,Y, ROMAN and RGB
        self.setContourProperties(myOutputFile)
        # Lastly copy over the standard qml (QGIS Style file)
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-contours-%s.qml' % theAlgorithm)
        mySourceQml = os.path.join(dataDir(), 'mmi-contours.qml')
        shutil.copyfile(mySourceQml, myQmlPath)
        return myOutputFile

    def setContourProperties(self, theFile):
        """
        Set the X, Y, RGB, ROMAN attributes of the contour layer.

        Args: theFile str (Required) Name of the contour layer.

        Returns: None

        Raises: InvalidLayerError if anything is amiss with the layer.
        """
        LOGGER.debug('setContourProperties requested.')
        myLayer = QgsVectorLayer(theFile , 'mmi-contours', "ogr")
        if not myLayer.isValid():
            raise InvalidLayerError(theFile)

        myProvider = myLayer.dataProvider()
        myIndexes = myProvider.attributeIndexes()
        myLayer.select(myIndexes)
        # Setup field indexes of our input dataset
        myMMIIndex = myProvider.fieldNameIndex('MMI')
        myRGBIndex = myProvider.fieldNameIndex('RGB')
        myXIndex = myProvider.fieldNameIndex('X')
        myYIndex = myProvider.fieldNameIndex('Y')
        myRomanIndex = myProvider.fieldNameIndex('ROMAN')
        myAlignIndex = myProvider.fieldNameIndex('ALIGN')
        myFeature = QgsFeature()
        myLayer.startEditing()
        # Now loop through the db adding selected features to mem layer
        while myProvider.nextFeature(myFeature):
            if not myFeature.isValid():
                LOGGER.debug('Skipping feature')
                continue
            # Work out myX and myY
            myLine = myFeature.geometry().asPolyline()
            myY = myLine[0].y()
            for myPoint in myLine:
                if myPoint.y() < myY:
                    myY = myPoint.y()
            myX = self.longitude  # always align labels to epicenter longitude

            myRomanList = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII',
                           'IX', 'X', 'XI', 'XII']

            myAttributes = myFeature.attributeMap()
            myMMIValue = float(myAttributes[myMMIIndex].toString())
            print 'MMI: ----> %s' % myAttributes[myMMIIndex].toString()
	    # We only want labels on the half contours so test for that
            if myMMIValue != round(myMMIValue):
                myRoman = myRomanList[int(round(myMMIValue))]
            else:
                myRoman = ''
            # RGB from http://en.wikipedia.org/wiki/Mercalli_intensity_scale
            myRGBList = ['#FFFFFF', '#BFCCFF', '#99F', '#8FF', '#7df894',
                         '#FF0', '#FD0', '#ff9100', '#F00', '#D00', '#800',
                         '#400']
            myRGB = myRGBList[int(myMMIValue)]

            # Now update the feature
            myId = myFeature.id()
            myLayer.changeAttributeValue(myId, myXIndex, QVariant(myX))
            myLayer.changeAttributeValue(myId, myYIndex, QVariant(myY))
            myLayer.changeAttributeValue(myId, myRGBIndex, QVariant(myRGB))
            myLayer.changeAttributeValue(myId, myRomanIndex, QVariant(myRoman))
            myLayer.changeAttributeValue(myId, myAlignIndex, QVariant('Center'))

        myLayer.commitChanges()

    def boundsToRectangle(self):
        """Convert the event bounding box to a QgsRectangle.

        Args: None

        Returns: QgsRectangle

        Raises: None
        """
        LOGGER.debug('bounds to rectangle called.')
        myRectangle = QgsRectangle(self.xMinimum,
                                   self.yMinimum,
                                   self.xMaximum,
                                   self.yMaximum)
        return myRectangle

    def citiesToShape(self):
        """Write the local cities to a shapefile.

        .. note:: Delegates to localCitiesMemoryLayer then uses
           QgsVectorFileWriter to write it to a shp.

        Args: None

        Returns: str Path to the created shapefile

        Raises: CityShapefileCreationError
        """
        LOGGER.debug('citiesToShape requested.')
        myMemoryLayer = self.localCitiesMemoryLayer()

        LOGGER.debug(str(myMemoryLayer.dataProvider().attributeIndexes()))
        if myMemoryLayer.featureCount() < 1:
            raise CityShapefileCreationError('Memory layer has no features')

        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        myOutputFileBase = os.path.join(shakemapExtractDir(),
                                        self.eventId,
                                        'mmi-cities.')
        myOutputFile = myOutputFileBase + 'shp'
        if os.path.exists(myOutputFile) and theForceFlag is not True:
            return myOutputFile
        elif os.path.exists(myOutputFile):
            os.remove(myOutputFileBase + 'shp')
            os.remove(myOutputFileBase + 'shx')
            os.remove(myOutputFileBase + 'dbf')
            os.remove(myOutputFileBase + 'prj')


        # Next two lines a workaround for a QGIS bug (lte 1.8)
        # preventing mem layer attributes being saved to shp.
        myMemoryLayer.startEditing()
        myMemoryLayer.commitChanges()

        LOGGER.debug('Writing mem layer to shp: %s' % myOutputFile)
        # Explicitly giving all options, not really needed but nice for clarity
        myErrorMessage = QString()
        myOptions = QStringList()
        myLayerOptions = QStringList()
        mySelectedOnlyFlag = False
        mySkipAttributesFlag = False
        myResult = QgsVectorFileWriter.writeAsVectorFormat(
            myMemoryLayer,
            myOutputFile,
            'utf-8',
            myGeoCrs,
            "ESRI Shapefile",
            mySelectedOnlyFlag,
            myErrorMessage,
            myOptions,
            myLayerOptions,
            mySkipAttributesFlag)

        if myResult == QgsVectorFileWriter.NoError:
            LOGGER.debug('Wrote mem layer to shp: %s' % myOutputFile)
        else:
            raise CityShapefileCreationError('Failed with error: %s' % myResult)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        myQmlPath = os.path.join(shakemapExtractDir(),
                                 self.eventId,
                                 'mmi-cities.qml')
        mySourceQml = os.path.join(dataDir(), 'mmi-cities.qml')
        shutil.copyfile(mySourceQml, myQmlPath)

        return myOutputFile

    def localCityFeatures(self):
        """Create a list of features representing cities impacted.

        The following fields will be created for each city feature:

            QgsField("name", QVariant.String),
            QgsField("population",  QVariant.Int),
            QgsField("mmi", QVariant.Double),
            QgsField("distance_to", QVariant.Double),
            QgsField("direction_to", QVariant.Double),
            QgsField("direction_from", QVariant.Double)

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
        out by self.zoomFactor until we have some cities selected.

        After making a selection the extents used (taking into account the
        iterative scaling mentioned above) will be stored in the class
        attributes so that when producing a map it can be used to ensure
        the cities and the shake area are visible on the map. See
        :samp:`self.extentWithCities` in :func:`__init__`.

        .. note:: We separate the logic of creating features from writing a
          layer so that we can write to any format we like whilst reusing the
          core logic.

        Args: None

        Returns: A list of QgsFeature instances, each representing a place/city.

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
        myGeometryColumn = 'Geometry'
        mySchema = ''
        myUri.setDataSource(mySchema, myTable, myGeometryColumn)
        myLayer = QgsVectorLayer(myUri.uri(), 'Towns', 'spatialite')
        if not myLayer.isValid():
            raise InvalidLayerError(myDBPath)
        myLayerProvider = myLayer.dataProvider()
        myIndexes = myLayerProvider.attributeIndexes()
        myFetchGeometryFlag = True
        myUseIntersectionFlag = True
        myRectangle = self.boundsToRectangle()


        # Do iterative selection using expanding selection area
        # Until we have got some cities selected

        myAttemptsLimit = 5
        myMinimumCityCount = 3
        for _ in range(myAttemptsLimit):
            myLayer.select(myIndexes, myRectangle,
                           myFetchGeometryFlag, myUseIntersectionFlag)
            if myLayer.selectedFeatureCount() < myMinimumCityCount:
                myRectangle.scale(self.zoomFactor)
            else:
                break

        # Setup field indexes of our input and out datasets
        myCities = []
        myLayerPlaceNameIndex = myLayerProvider.fieldNameIndex('asciiname')
        myLayerPopulationIndex = myLayerProvider.fieldNameIndex('population')
        myPlaceNameIndex = 0
        myPopulationIndex = 1
        myMmiIndex = 2
        myDistanceIndex = 3
        myDirectionToIndex = 4
        myDirectionFromIndex = 5

        # For measuring distance and direction from each city to epicenter
        myEpicenter = QgsPoint(self.longitude, self.latitude)
        myFeature = QgsFeature()

        # Now loop through the db adding selected features to mem layer
        while myLayerProvider.nextFeature(myFeature):
            if not myFeature.isValid():
                LOGGER.debug('Skipping feature')
                continue
                #LOGGER.debug('Writing feature to mem layer')
            # calculate the distance and direction from this point
            # to and from the epicenter
            myAttributes = myFeature.attributeMap()
            myPoint = myFeature.geometry().asPoint()
            myDistance = myPoint.sqrDist(myEpicenter)
            myDirectionTo = myPoint.azimuth(myEpicenter)
            myDirectionFrom = myEpicenter.azimuth(myPoint)
            myPlaceName = str(myAttributes[myLayerPlaceNameIndex].toString())
            myPopulation = myAttributes[myLayerPopulationIndex]
            myNewFeature = QgsFeature()
            myNewFeature.setGeometry(myFeature.geometry())

            # Populate the mmi field by raster lookup
            myResult, myRasterValues = myRasterLayer.identify(myPoint)
            if not myResult:
                # position not found on raster
                continue
            myValue = myRasterValues[QString('Band 1')]
            if 'no data' not in myValue:
                myMmi = float(myValue)
            else:
                myMmi = 0

            LOGGER.debug('Looked up mmi of %s on raster for %ss' %
                         (myMmi, myPoint.toString()))

            myAttributeMap = {
                myPlaceNameIndex: myPlaceName,
                myPopulationIndex: myPopulation,
                myMmiIndex: QVariant(myMmi),
                myDistanceIndex: QVariant(myDistance),
                myDirectionToIndex: QVariant(myDirectionTo),
                myDirectionFromIndex: QVariant(myDirectionFrom)
            }
            #LOGGER.debug('Attribute Map: %s' % str(myAttributeMap))
            myNewFeature.setAttributeMap(myAttributeMap)
            myCities.append(myNewFeature)
        return myCities


    def localCitiesMemoryLayer(self):
        """Fetch a collection of the cities that are nearby.

        Args: None

        Returns: QgsVectorLayer - A QGIS memory layer

        Raises: an exceptions will be propogated
        """
        LOGGER.debug('mmiDataToContours requested.')
        # Now store the selection in a temporary memory layer
        myMemoryLayer = QgsVectorLayer('Point', 'affected_cities', 'memory')
        myMemoryProvider = myMemoryLayer.dataProvider()
        # add field defs
        myMemoryProvider.addAttributes([
            QgsField('name', QVariant.String),
            QgsField('population', QVariant.Int),
            QgsField('mmi', QVariant.Double),
            QgsField('distance_to', QVariant.Double),
            QgsField('direction_to', QVariant.Double),
            QgsField('direction_from', QVariant.Double)])
        myCities = self.localCityFeatures()
        myResult = myMemoryProvider.addFeatures(myCities)
        if not myResult:
            raise CityMemoryLayerCreationError('Add feature failed for:' %
                myAttributes[myLayerPopulationIndex].toString())
            #LOGGER.debug('Features: %s' % myMemoryLayer.featureCount())
        myMemoryLayer.commitChanges()
        myMemoryLayer.updateExtents()

        LOGGER.debug('Feature count of mem layer:  %s' %
                     myMemoryLayer.featureCount())

        return myMemoryLayer

    def calculateFatalities(self,
                            thePopulationRasterPath=None,
                            theForceFlag=False,
                            theAlgorithm=None):
        """Use the earthquake fatalities  function to calculate fatalities.

        Args:
            thePopulationRasterPath: str optional. see
                :func:`_getPopulationPath` for more details on how the path will
                be resolved if not explicitly given.
            theForceFlag bool - (Optional). Whether to force the regeneration
                of contour product. Defaults to False.
            theAlgorithm str - (Optional) Which interpolation algorithm to
                use to create the underlying raster. see
                :func:`mmiToRasterData` for information about default behaviour.
        Returns:
            str - the path to the computed impact file.
                The class members self.impactFile and self.fatalityCounts
                will be populated.
                self.fatalityCounts is a dict containing fatality counts for
                the shake events. Keys for the dict will be MMI classes (I-X)
                and values will be fatalities for that class.
        Raises:
            None
        """
        if thePopulationRasterPath is None or (
            not os.path.isfile(thePopulationRasterPath) and
            not os.path.islink(thePopulationRasterPath)):

            myExposurePath = self._getPopulationPath()
        else:
            myExposurePath = thePopulationRasterPath

        myHazardPath = self.mmiDataToRaster(
                theForceFlag=theForceFlag,
                theAlgorithm=theAlgorithm)

        myClippedHazardPath, myClippedExposurePath = self.clipLayers(
            theShakeRasterPath=myHazardPath,
            thePopulationRasterPath=myExposurePath)

        myClippedHazardLayer = safe_read_layer(myClippedHazardPath)
        myClippedExposureLayer = safe_read_layer(myClippedExposurePath)
        myLayers = [myClippedHazardLayer, myClippedExposureLayer]

        myFunctionId = 'I T B Fatality Function'
        myFunction = safe_get_plugins(myFunctionId)[0][myFunctionId]

        myResult = safe_calculate_impact(myLayers, myFunction)
        self.impactFile = result.filename
        self.fatalityCounts = result.keywords
        return myResult.filename

    def clipLayers(self, theShakeRasterPath, thePopulationRasterPath):
        """Clip population (exposure) layer to dimensions of shake data.

        It is possible (though unlikely) that the shake may be clipped too.

        Args:
            theShakeRasterPath: Path to the shake raster.
            thePopulationRasterPath: Path to the population raster.

        Returns:
            str, str: Path to the clipped datasets (clipped shake, clipped pop).

        Raises:
            FileNotFoundError
        """

        # _ is a syntactical trick to ignore second returned value
        myBaseName, _ = os.path.splitext(theShakeRasterPath)
        myHazardLayer = QgsRasterLayer(theShakeRasterPath, myBaseName)
        myBaseName, _ = os.path.splitext(thePopulationRasterPath)
        myExposureLayer = QgsRasterLayer(thePopulationRasterPath, myBaseName)

        # Reproject all extents to EPSG:4326 if needed
        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromEpsg(4326)

        # Get the Hazard extents as an array in EPSG:4326
        myHazardGeoExtent = extentToGeoArray(myHazardLayer.extent(),
                                                  myHazardLayer.crs())

        # Fake the viewport extent to be the same as hazard extent
        # since we are doing this headless without any vieport but I wanted
        # to re-use code from safe_qgis
        myViewportGeoExtent = myHazardGeoExtent

        # Get the Exposure extents as an array in EPSG:4326
        myExposureGeoExtent = extentToGeoArray(myExposureLayer.extent(),
                                                    myExposureLayer.crs())

        # Now work out the optimal extent between the two layers and
        # the current view extent. The optimal extent is the intersection
        # between the two layers and the viewport.
        try:
            # Extent is returned as an array [xmin,ymin,xmax,ymax]
            # We will convert it to a QgsRectangle afterwards.
            myGeoExtent = getOptimalExtent(myHazardGeoExtent,
                                           myExposureGeoExtent,
                                           myViewportGeoExtent)
        except InsufficientOverlapException, e:
            myMessage = ('There was insufficient overlap between the input'
                         ' layers')
            raise Exception(myMessage)
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

        myClippedHazardPath = clipLayer(
                                theLayer=myHazardLayer,
                                theExtent=myGeoExtent,
                                theCellSize=myCellSize)
        myClippedExposurePath = clipLayer(
                                    theLayer=myExposureLayer,
                                    theExtent=myGeoExtent,
                                    theCellSize=myCellSize,
                                    theExtraKeywords=extraExposureKeywords)

        return myClippedHazardPath, myClippedExposurePath

    def _getPopulationPath(self):
        """Helper to determine population raster spath.

        Args:
            thePopulationPath: str optional path to the population raster.
                If not passed as a parameter, the following priority will be
                used to determine the path:
                1) the class attribute self.populationRasterPath
                    will be checked and if not None it will be used.
                2) the environment variable 'SAFE_POPULATION_PATH' will be
                   checked if set it will be used.
                4) A hard coded path of
                   :file:`/fixtures/exposure/population.tif` will be appended
                   to os.path.abspath(os.path.curdir)
                5) A hard coded path of
                   :file:`/usr/local/share/inasafe/exposure/population.tif`
                   will be used.
        Returns:
            str - path to a population raster file.
        Raises:
            FileNotFoundError
        """
        myFixturePath = os.path.join(os.path.abspath(os.path.curdir),
                                     'fixtures', 'exposure', 'population.tif')
        myLocalPath = '/usr/local/share/inasafe/exposure/population.tif'
        if self.populationRasterPath is not None:
            return self.populationRasterPath
        elif 'SAFE_POPULATION_PATH' in os.environ:
            return os.environ['SAFE_POPULATION_PATH']
        elif os.path.exists(myFixturePath):
            return myFixturePath
        elif os.path.exists(os.path.exists(myLocalPath)):
            return myLocalPath
        else:
            raise FileNotFoundError('Population file could not be found')

    def __str__(self):
        """The unicode representation for an event object's state.

        Args: None

        Returns: str A string describing the ShakeEvent instance

        Raises: None
        """
        if self.mmiData:
            mmiData = 'Populated'
        else:
            mmiData = 'Not populated'
        myString = (('latitude: %(latitude)s\n'
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
                     'timeZone: %(timeZone)s\n'
                     'xMinimum: %(xMinimum)s\n'
                     'xMaximum: %(xMaximum)s\n'
                     'yMinimum: %(yMinimum)s\n'
                     'yMaximum: %(yMaximum)s\n'
                     'rows: %(rows)s\n'
                     'columns: %(columns)s\n'
                     'mmiData: %(mmiData)s\n'
                     'populationRasterPath: %(populationRasterPath)s\n'
                     'impactFile: %(impactFile)s\n'
                     'fatalityCounts: %(fatalityCounts)s') %
                    {
                        'latitude': self.latitude,
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
                        'timeZone': self.timeZone,
                        'xMinimum': self.xMinimum,
                        'xMaximum': self.xMaximum,
                        'yMinimum': self.yMinimum,
                        'yMaximum': self.yMaximum,
                        'rows': self.rows,
                        'columns': self.columns,
                        'mmiData': mmiData,
                        'populationRasterPath': self.populationRasterPath,
                        'impactFile': self.impactFile,
                        'fatalityCounts': self.fatalityCounts
                    })
        return myString
