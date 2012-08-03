"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import os
import shutil
from zipfile import ZipFile
import gdal
import ogr
from gdalconst import GA_ReadOnly
# The logger is intiailsed in utils.py by init
import logging
LOGGER = logging.getLogger('InaSAFE-Realtime')

from rt_exceptions import (EventUndefinedError,
                        EventIdError,
                        NetworkError,
                        EventValidationError,
                        InvalidInputZipError,
                        InvalidOutputZipError,
                        ExtractionError,
                        GridConversionError,
                        EventParseError,
                        ContourCreationError
                        )
from ftp_client import FtpClient
from utils import (shakemapZipDir,
                            shakemapExtractDir,
                            shakemapDataDir,
                            gisDataDir)
from shake_event import ShakeEvent


class ShakeData:
    """A class for retrieving, reading, converting and extracting
       data from shakefiles.

    Shake files are provided on an ftp server. There are two files for every
    event:
       * an 'inp' file
       * an 'out' file

    These files are provided on the ftp server as zip files. For example:
        * `ftp://118.97.83.243/20110413170148.inp.zip`_
        * `ftp://118.97.83.243/20110413170148.out.zip`_

    There are numerous files provided within these two zip files, but there
    are only really two that we are interested in:

        * grid.xyz - which contains all the metadata pertaining to the event
        * mi.grd - which contains the GMT formatted raster shake MMI data.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it.
    """

    def __init__(self, theEvent=None, theHost='118.97.83.243'):
        """Constructor for the ShakeData class

            Args:
                * theEvent - (Optional) a string representing the event id
                  that this raster is associated with. e.g. 20110413170148.
                  **If no event id is supplied, a query will be made to the
                  ftp server, and the latest event id assigned.**
                * theData - (Optional) a string representing the ip address
                  or host name of the server from which the data should be
                  retrieved. It assumes that the data is in the root directory.
                  Defaults to 118.97.83.243

            Returns:
                None

            Raises:
                None

            """
        self.eventId = theEvent
        self.host = theHost
        # private Shake event instance associated with this shake dataset
        self._shakeEvent = None
        if self.eventId is None:
            try:
                self.getLatestEventId()
            except NetworkError:
                raise
        else:
            # If we fetched it above using getLatestEventId we assume it is
            # already validated.
            try:
                self.validateEvent()
            except EventValidationError:
                raise
        # If eventId is still None after all the above, moan....
        if self.eventId is None:
            myMessage = ('No id was passed to the constructor and the '
                               'latest id could not be retrieved from the'
                               'server.')
            LOGGER.exception('ShakeData initialisation failed')
            raise EventIdError(myMessage)

    def getLatestEventId(self):
        """Query the ftp server and determine the latest event id.

        Args: None

        Returns: A string containing a valid event id.

        Raises: NetworkError
        """
        myFtpClient = FtpClient()
        try:
            myList = myFtpClient.getListing()
        except NetworkError:
            raise
        myEventId = myList[-1].split('/')[-1].split('.')[0]
        if myEventId is None:
            raise EventIdError('Latest Event Id could not be obtained')
        self.eventId = myEventId

    def validateEvent(self):
        """Check that the event associated with this instance exists either
        in the local event cache, or on the remote ftp site.

        Args: None

        Returns: True if valid, False if not

        Raises: NetworkError
        """
        # First check local cache
        myInpFileName = self.eventId + '.inp.zip'
        myOutFileName = self.eventId + '.out.zip'
        myInpFilePath = os.path.join(shakemapZipDir(),
                                     myInpFileName)
        myOutFilePath = os.path.join(shakemapZipDir(),
                                     myOutFileName)
        if (os.path.exists(myInpFilePath) and
            os.path.exists(myOutFilePath)):
            # TODO: we should actually try to unpack them for deeper validation
            return True
        else:
            LOGGER.debug('%s is not cached' % myInpFileName)
            LOGGER.debug('%s is not cached' % myOutFileName)
        myFtpClient = FtpClient()
        myList = myFtpClient.getListing()
        if (myInpFileName in myList and myOutFileName in myList):
            return True

    def _fetchFile(self, theEventFile):
        """Private helper to fetch a file from the ftp site.

          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip

        .. note:: If a cached copy of the file exits, the path to the cache
           copy will simply be returned without invoking any network requests.

        Args: None

        Returns: A string for the dataset path on the local storage system.

        Raises: EventUndefinedError, NetworkError
        """
        # Return the cache copy if it exists
        myLocalPath = os.path.join(shakemapZipDir(), theEventFile)
        if os.path.exists(myLocalPath):
            return myLocalPath
        #Otherwise try to fetch it using ftp
        try:
            myClient = FtpClient()
            myClient.getFile(theEventFile, myLocalPath)
        except:
            # TODO: differentiate between file not found and networ errors.
            raise NetworkError('Message failed to retrieve '
                               'file. %s' % theEventFile)
        return myLocalPath

    def fetchInput(self):
        """Fetch the input file for the event id associated with this class
           e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip

        Args: None

        Returns: A string for the 'inp' dataset path on the local storage
            system.

        Raises: EventUndefinedError, NetworkError
        """
        if self.eventId is None:
            raise EventUndefinedError('Event is none')

        myEventFile = self.eventId + '.inp.zip'
        try:
            return self._fetchFile(myEventFile)
        except (EventUndefinedError, NetworkError):
            raise

    def fetchOutput(self):
        """Fetch the output file for the event id associated with this class.
          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.out.zip

          and this local file created::

              /tmp/realtime/20110413170148.out.zip

        Args: None

        Returns: A string for the 'out' dataset path on the local storage
            system.

        Raises: EventUndefinedError, NetworkError
        """
        if self.eventId is None:
            raise EventUndefinedError('Event is none')

        myEventFile = self.eventId + '.out.zip'
        try:
            return self._fetchFile(myEventFile)
        except (EventUndefinedError, NetworkError):
            raise

    def fetchEvent(self):
        """Fetch both the input and output shake data from the server for
        the event id associated with this class.

        Args: None

        Returns: A two tuple where the first item is the inp dataset path and
        the second the out dataset path on the local storage system.

        Raises: EventUndefinedError, NetworkError
        """
        if self.eventId is None:
            raise EventUndefinedError('Event is none')

        try:
            myInpFile = self.fetchInput()
            myOutFile = self.fetchOutput()
        except (EventUndefinedError, NetworkError):
            raise
        return (myInpFile, myOutFile)

    def extract(self, theForceFlag=False):
        """Extract the zipped resources. The two zips associated with this
        shakemap will be extracted to e.g.

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/20120726022003`

        After extraction the complete path will appear something like this:

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/
               20120726022003/usr/local/smap/data/20120726022003`

        with input and output directories appearing beneath that.

        This method will then move the event.xml and mi.grd files up to the
        root of the extract dir and recursively remove the extracted dirs.

        After this final step, the following files will be present:

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/
               20120726022003/event.xml`
        :file:`/tmp/inasafe/realtime/shakemaps-extracted/
               20120726022003/mi.grd`

        If the zips have not already been retrieved from the ftp server,
        they will be fetched first automatically.

        If the zips have previously been extracted, the extract dir will
        be completely removed and the dataset re-extracted.

        .. note:: You should not store any of your own working data in the
           extract dir - it should be treated as transient.

        Args:
            theForceFlag - (Optional) Whether to force re-extraction. If the
                files were previously extracted, you can force them to be
                extracted again. If False, the event.xml and mi.grd files are
                cached. Default False.

        Returns: a two-tuple containing the event.xml and mi.grd paths e.g.::
            myEventXml, myGrd = myShakeData.extract()
            print myEventXml, myGrd
            /tmp/inasafe/realtime/shakemaps-extracted/20120726022003/event.xml
            /tmp/inasafe/realtime/shakemaps-extracted/20120726022003/mi.grd

        Raises: InvalidInputZipError, InvalidOutputZipError
        """

        myFinalEventFile = os.path.join(self.extractDir(), 'event.xml')
        myFinalGridFile = os.path.join(self.extractDir(), 'mi.grd')

        if theForceFlag:
            self.removeExtractedFiles()
        elif (os.path.exists(myFinalEventFile) and
              os.path.exists(myFinalGridFile)):
            return myFinalEventFile, myFinalGridFile

        myInput, myOutput = self.fetchEvent()
        myInputZip = ZipFile(myInput)
        myOutputZip = ZipFile(myOutput)

        myExpectedEventFile = ('usr/local/smap/data/%s/input/event.xml' %
                  self.eventId)
        myExpectedGridFile = ('usr/local/smap/data/%s/output/mi.grd' %
                  self.eventId)

        myList = myInputZip.namelist()
        if myExpectedEventFile not in myList:
            raise InvalidInputZipError('The input zip does not contain an '
                '%s file.' % myExpectedEventFile)

        myList = myOutputZip.namelist()
        if myExpectedGridFile not in myList:
            raise InvalidOutputZipError('The output zip does not contain an '
                '%s file.' % myExpectedGridFile)

        myExtractDir = self.extractDir()
        myInputZip.extractall(myExtractDir)
        myOutputZip.extractall(myExtractDir)

        # move the two files we care about to the top of the event extract dir
        shutil.copyfile(os.path.join(self.extractDir(), myExpectedEventFile),
                        myFinalEventFile)
        shutil.copyfile(os.path.join(self.extractDir(), myExpectedGridFile),
                        myFinalGridFile)
        # Get rid of all the other extracted stuff
        myUserDir = os.path.join(self.extractDir(), 'usr')
        if os.path.isdir(myUserDir):
            shutil.rmtree(myUserDir)

        if (not os.path.exists(myFinalEventFile) or
            not os.path.exists(myFinalGridFile)):
            raise ExtractionError('Error copying event.xml or mi.grd')
        return myFinalEventFile, myFinalGridFile


    def extractDir(self):
        """A helper method to get the path to the extracted datasets.

        Args: None

        Returns: A string representing the absolute local filesystem path to
            the unzipped shake event dir. e.g.
            :file:`/tmp/inasafe/realtime/shakemaps-extracted/20120726022003`

        Raises: Any exceptions will be propogated
        """
        return os.path.join(shakemapExtractDir(), self.eventId)

    def removeExtractedFiles(self):
        """Tidy up the filesystem by removing all extracted files
        for the given event instance.

        Args: None

        Returns: None

        Raises: Any error e.g. file permission error will be raised.
        """
        myExtractedDir = self.extractDir()
        if os.path.isdir(myExtractedDir):
            shutil.rmtree(myExtractedDir)

    def postProcess(self, theForceFlag=True):
        """Process the event.xml and mi.grd files so that they can be used
        in our workflow. This entails deserialising the event.xml into
        a ShakeEvent object, and converting the mi.grd to a tif file.

        The ShakeEvent object will be pickled to the disk for persistent
        storage.

        .. note:: Delegates to convertGrid() and shakeEvent() methods.

        Args: theForceFlag - (Optional). Whether to force the regeneration
            of post processed products. Defaults to False.

        Returns: myShakeEvent, myGridPath
            * ShakeEvent - an instance of ShakeEvent populated with whatever
              data could be gleaned from the event.xml file.
            * myGridPath - a string representing the absolute path to the
              generated grid file.

        Raises: EventParseError, GridConversionError
        """
        myTifPath = self.convertGrid(theForceFlag)
        myShakeEvent = self.shakeEvent(theForceFlag)
        return myShakeEvent, myTifPath


    def convertGrid(self, theForceFlag=True):
        """Convert the grid for this shakemap to a tif.

        In the simplest use case you should be able to simply do::

           myShakeData = ShakeData('20120726022003')
           myTifPath = myShakeData.convertGrid()

        and the ShakeData class will take care of fetching (if not already
        cached), extracting a converting the file for you, returning a usable
        tif.

        .. seealso:: postProcess() which will perform both convertGrid and
           event deserialisation in one call.

        Args: theForceFlag - (Optional). Whether to force the regeneration
            of post processed tif product. Defaults to False.

        Returns: An absolute file system path pointing to the coverted tif file.

        Raises: GridConversionError
        """

        myTifPath = os.path.join(shakemapDataDir(), self.eventId + '.tif')
        #short circuit if the tif is already created.
        if os.path.exists(myTifPath) and theForceFlag is not True:
            return myTifPath

        #otherwise get the grid if needed
        myEventXml, myGridPath = self.extract()
        del myEventXml
        #now save it to Tif
        myFormat = 'GTiff'
        myDriver = gdal.GetDriverByName( myFormat )
        myGridDataset = gdal.Open(myGridPath, GA_ReadOnly)
        if myGridDataset is not None:
            myTifDataset = myDriver.CreateCopy(myTifPath, myGridDataset, 0)
            # Once we're done, close properly the dataset
            del myGridDataset
            del myTifDataset
        else:
            raise GridConversionError('Could not open source grid: %s',
                                      myGridPath)
        return myTifPath

    def shakeEvent(self, theForceFlag=True):
        """Parse the event.xml and return it as a ShakeEvent object.

        In the simplest use case you can simply do::

           myShakeData = ShakeData('20120726022003')
           myShakeEvent = myShakeData.shakeEvent()

        Args: theForceFlag - (Optional). Whether to force the regeneration
            of post processed ShakeEvent. Defaults to False.

        Returns: A ShakeEvent object.

        Raises: EventParseError
        """
        if self._shakeEvent is None or theForceFlag is True:
            self.extract(theForceFlag)
            self._shakeEvent = ShakeEvent(self.eventId)
        return self._shakeEvent

    def extractContours(self, theForceFlag=True):
        """Extract contours from the event's tif file.

        Contours are extracted at a 1MMI interval. The resulting file will
        be saved in gisDataDir(). In the easiest use case you can simlpy to::

           myShakeEvent = myShakeData.shakeEvent()
           myContourPath = myShakeData.extractContours()

        which will return the contour dataset for the latest event on the
        ftp server.

        Args: theForceFlag - (Optional). Whether to force the regeneration
            of contour product. Defaults to False.

        Returns: An absolute filesystem path pointing to the generated
            contour dataset.

        Raises: ContourCreationError

        """
        # TODO: Use sqlite rather?
        myOutputFileBase = os.path.join(gisDataDir(),
                                        self.eventId + '_contours.')
        myOutputFile = myOutputFileBase +  'shp'
        if os.path.exists(myOutputFile) and theForceFlag is not True:
            return myOutputFile
        elif os.path.exists(myOutputFile):
            os.remove(myOutputFileBase + 'shp')
            os.remove(myOutputFileBase + 'shx')
            os.remove(myOutputFileBase + 'dbf')
            os.remove(myOutputFileBase + 'prj')

        myTifPath = self.convertGrid(theForceFlag)
        # Based largely on
        # http://svn.osgeo.org/gdal/trunk/autotest/alg/contour.py
        myDriver = ogr.GetDriverByName('ESRI Shapefile')
        myOgrDataset = myDriver.CreateDataSource(myOutputFile)
        if myOgrDataset is None:
            # Probably the file existed and could not be overriden
            raise ContourCreationError('Could not create datasource for:\n%s'
                'Check that the file does not already exist and that you '
                'do not have file system permissions issues')
        myLayer = myOgrDataset.CreateLayer('contour')
        myFieldDefinition = ogr.FieldDefn('ID', ogr.OFTInteger)
        myLayer.CreateField(myFieldDefinition)
        myFieldDefinition = ogr.FieldDefn('MMI', ogr.OFTReal)
        myLayer.CreateField(myFieldDefinition)
        myTifDataset = gdal.Open(myTifPath, GA_ReadOnly)
        # see http://gdal.org/java/org/gdal/gdal/gdal.html for these options
        myBand = 1
        myContourInterval = 1  # MMI not M!
        myContourBase = 0
        myFixedLevelList = []
        myUseNoDataFlag = 0
        myNoDataValue = -9999
        myIdField = 0  # first field defined above
        myElevationField = 1 # second (MMI) field defined above

        gdal.ContourGenerate(myTifDataset.GetRasterBand(myBand),
                             myContourInterval,
                             myContourBase,
                             myFixedLevelList,
                             myUseNoDataFlag,
                             myNoDataValue,
                             myLayer,
                             myIdField,
                             myElevationField)
        del myTifDataset
        myOgrDataset.Release()
        return myOutputFile
