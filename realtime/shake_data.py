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
# The logger is intiailsed in utils.py by init
import logging
LOGGER = logging.getLogger('InaSAFE')

from rt_exceptions import (EventUndefinedError,
                           EventIdError,
                           NetworkError,
                           EventValidationError,
                           InvalidInputZipError,
                           ExtractionError)
from ftp_client import FtpClient
from utils import shakemapZipDir, shakemapExtractDir


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
    is only really one that we are interested in:

        * grid.xml - which contains all the metadata pertaining to the event

    The remaining files are fetched for completeness and possibly use in the
    future.

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
                * theHost - (Optional) a string representing the ip address
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
                         'latest id could not be retrieved from the server.')
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

    def isOnServer(self):
        """Check the event associated with this instance exists on the server.

        Args: None

        Returns: True if valid, False if not

        Raises: NetworkError
        """
        myInpFileName, myOutFileName = self.fileNames()
        myList = [myInpFileName, myOutFileName]
        myFtpClient = FtpClient()
        return myFtpClient.hasFiles(myList)

    def fileNames(self):
        """Return file names for the inp and out files based on the event id.

        e.g. 20120726022003.inp.zip, 20120726022003.out.zip

        Args: None

        Returns:
            two tuple: str, str Consisting of inp and out local cache paths.

        Raises:
            None
        """
        myInpFileName = self.eventId + '.inp.zip'
        myOutFileName = self.eventId + '.out.zip'
        return myInpFileName, myOutFileName

    def cachePaths(self):
        """Return the paths to the inp and out files as expected locally.

        Args: None

        Returns:
            two tuple: str, str Consisting of inp and out local cache paths.

        Raises:
            None
        """

        myInpFileName, myOutFileName = self.fileNames()
        myInpFilePath = os.path.join(shakemapZipDir(),
                                     myInpFileName)
        myOutFilePath = os.path.join(shakemapZipDir(),
                                     myOutFileName)
        return myInpFilePath, myOutFilePath

    def isCached(self):
        """Check the event associated with this instance exists in cache.

        Args: None

        Returns: True if locally cached, False if not

        Raises: None
        """
        myInpFilePath, myOutFilePath = self.cachePaths()
        if os.path.exists(myInpFilePath) and os.path.exists(myOutFilePath):
            # TODO: we should actually try to unpack them for deeper validation
            return True
        else:
            LOGGER.debug('%s is not cached' % myInpFilePath)
            LOGGER.debug('%s is not cached' % myOutFilePath)
            return False

    def validateEvent(self):
        """Check that the event associated with this instance exists either
        in the local event cache, or on the remote ftp site.

        Args: None

        Returns: True if valid, False if not

        Raises: NetworkError
        """
        # First check local cache
        if self.isCached():
            return True
        else:
            return self.isOnServer()

    def _fetchFile(self, theEventFile, theRetries=3):
        """Private helper to fetch a file from the ftp site.

          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip

        .. note:: If a cached copy of the file exits, the path to the cache
           copy will simply be returned without invoking any network requests.

        Args:
            * theEventFile: str - filename on server e.g.20110413170148.inp.zip
            * theRetries: int - number of reattempts that should be made in
                in case of network error etc.

        Returns:
            str: A string for the dataset path on the local storage system.

        Raises:
            EventUndefinedError, NetworkError
        """
        # Return the cache copy if it exists
        myLocalPath = os.path.join(shakemapZipDir(), theEventFile)
        if os.path.exists(myLocalPath):
            return myLocalPath

        #Otherwise try to fetch it using ftp
        for myCounter in range(theRetries):
            myLastError = None
            try:
                myClient = FtpClient()
                myClient.getFile(theEventFile, myLocalPath)
            except NetworkError, e:
                myLastError = e
            except:
                LOGGER.exception(
                    'Could not fetch shake event from server %s'
                    % theEventFile)
                raise

            if myLastError is None:
                return myLocalPath

            LOGGER.info('Fetching failed, attempt %s' % myCounter)

        LOGGER.exception('Could not fetch shake event from server %s'
                         % theEventFile)
        raise Exception('Could not fetch shake event from server %s'
                        % theEventFile)

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
        return myInpFile, myOutFile

    def extract(self, theForceFlag=False):
        """Extract the zipped resources. The two zips associated with this
        shakemap will be extracted to e.g.

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/20120726022003`

        After extraction the complete path will appear something like this:

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/
               20120726022003/usr/local/smap/data/20120726022003`

        with input and output directories appearing beneath that.

        This method will then move the grid.xml file up to the root of
        the extract dir and recursively remove the extracted dirs.

        After this final step, the following file will be present:

        :file:`/tmp/inasafe/realtime/shakemaps-extracted/
               20120726022003/grid.xml`

        If the zips have not already been retrieved from the ftp server,
        they will be fetched first automatically.

        If the zips have previously been extracted, the extract dir will
        be completely removed and the dataset re-extracted.

        .. note:: You should not store any of your own working data in the
           extract dir - it should be treated as transient.

        .. note:: the grid.xml also contains MMI point data that
           we care about and will extract as a matrix (MMI in the 5th column).


        Args:
            theForceFlag - (Optional) Whether to force re-extraction. If the
                files were previously extracted, you can force them to be
                extracted again. If False, grid.xml local file is used if
                it is cached. Default False.

        Returns: a string containing the grid.xml paths e.g.::
            myGridXml = myShakeData.extract()
            print myGridXml
            /tmp/inasafe/realtime/shakemaps-extracted/20120726022003/grid.xml


        Raises: InvalidInputZipError, InvalidOutputZipError
        """

        myFinalGridXmlFile = os.path.join(self.extractDir(), 'grid.xml')

        if theForceFlag:
            self.removeExtractedFiles()
        elif os.path.exists(myFinalGridXmlFile):
            return myFinalGridXmlFile

        myInput, myOutput = self.fetchEvent()
        myInputZip = ZipFile(myInput)
        myOutputZip = ZipFile(myOutput)

        myExpectedGridXmlFile = (
            'usr/local/smap/data/%s/output/grid.xml' %
            self.eventId)

        myList = myOutputZip.namelist()
        if myExpectedGridXmlFile not in myList:
            raise InvalidInputZipError(
                'The output zip does not contain an '
                '%s file.' % myExpectedGridXmlFile)

        myExtractDir = self.extractDir()
        myInputZip.extractall(myExtractDir)
        myOutputZip.extractall(myExtractDir)

        # move the file we care about to the top of the extract dir
        shutil.copyfile(os.path.join(self.extractDir(), myExpectedGridXmlFile),
                        myFinalGridXmlFile)
        # Get rid of all the other extracted stuff
        myUserDir = os.path.join(self.extractDir(), 'usr')
        if os.path.isdir(myUserDir):
            shutil.rmtree(myUserDir)

        if not os.path.exists(myFinalGridXmlFile):
            raise ExtractionError('Error copying grid.xml')
        return myFinalGridXmlFile

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
