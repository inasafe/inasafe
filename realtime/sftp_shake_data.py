"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Ftp Client for Retrieving ftp data.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '14/01/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
from rt_exceptions import (FileNotFoundError,
                           EventIdError,
                           NetworkError,
                           EventValidationError,
                           CopyError
                           )
from sftp_client import SFtpClient
from utils import is_event_id
import logging
LOGGER = logging.getLogger('InaSAFE')
from utils import shakemapCacheDir, shakemapExtractDir, mkDir, is_event_id


defaultHost = '118.97.83.243'
defUserName = 'geospasial'
defPassword = os.environ['QUAKE_SERVER_PASSWORD']
defWorkDir = 'shakemaps'


class SftpShakeData:
    """A class for retrieving, reading data from shakefiles.
    Shake files are provide on server and can be accessed using SSH protocol.

    The shape files currently located under shakemaps directory in a folder
    named by the event id (which represent the timestamp of the event of the
    shake)

    There are numerous files in that directory but there is only really one
    that we are interested in:

        * grid.xml - which contains all the metadata pertaining to the event

    It's located in under output/grid.xml under each event directory

    The remaining files are fetched for completeness and possibly use in the
    future.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it

    Note :
        * inspired by shake_data.py but modified according to SSH protocol

    """

    def __init__(self, theEvent=None, theHost=defaultHost,
                 theUserName=defUserName, thePassword=defPassword,
                 theWorkingDir=defWorkDir, theForceFlag=False):
        """Constructor for the SftpShakeData class
            Args:
                * theEvent - (Optional) a string representing the event id
                  that this raster is associated with. e.g. 20110413170148.
                  **If no event id is supplied, a query will be made to the
                  ftp server, and the latest event id assigned.**
                * theHost - (Optional) a string representing the ip address
                  or host name of the server from which the data should be
                  retrieved. It assumes that the data is in the root directory.

            Returns:
                None

            Raises:
                None

        """
        self.eventId = theEvent
        self.host = theHost
        self.username = theUserName
        self.password = thePassword
        self.workdir = theWorkingDir
        self.forceFlag = theForceFlag
        self.sftpclient = SFtpClient(self.host, self.username,
                                        self.password, self.workdir)

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

    def reconnectSFTP(self):
        """Reconnect to the server
        """
        self.sftpclient = SFtpClient(self.host, self.username,
            self.password, self.workdir)

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

    def isCached(self):
        """Check the event associated with this instance exists in cache.

        Args: None

        Returns: True if locally cached, False if not

        Raises: None
        """
        myXMLFilePath = self.cachePaths()
        if os.path.exists(myXMLFilePath):
            return True
        else:
            LOGGER.debug('%s is not cached' % myXMLFilePath)
            return False

    def cachePaths(self):
        """Return the paths to the inp and out files as expected locally.

        Args: None

        Returns:
            str: grid.xml local cache paths.

        Raises:
            None
        """

        myXMLFileName = self.fileName()
        myXMLFilePath = os.path.join(shakemapCacheDir(), self.eventId,
                            myXMLFileName)
        return myXMLFilePath

    def fileName(self):
        """Return file names for the inp and out files based on the event id.

        for this class, only the grid.xml only

        Args: None

        Returns:
            str: grid.xml

        Raises:
            None
        """
        return 'grid.xml'

    def isOnServer(self):
        """Check the event associated with this instance exists on the server.

        Args: None

        Returns: True if valid, False if not

        Raises: NetworkError
        """
        myRemoteXMLPath = os.path.join(self.sftpclient.workdir_path,
                        self.eventId)
        return self.sftpclient.is_path_exist(myRemoteXMLPath)

    def get_list_event_ids(self):
        """Get all event id indicated by folder in remote_path
        """
        dirs = self.sftpclient.getListing(my_func=is_event_id)
        if len(dirs) == 0:
            raise Exception('List event is empty')
        return dirs

    def getLatestEventId(self):
        """Return latest event id
        """
        event_ids = self.get_list_event_ids()
        latest_event_id = None
        if event_ids is not None:
            event_ids.sort()
            latest_event_id = event_ids[-1]
        if latest_event_id is None:
            raise EventIdError('Latest Event Id could not be obtained')
        self.eventId = latest_event_id
        return self.eventId

    def fetchFile(self, theRetries=3):
        """Private helper to fetch a file from the sftp site.

          e.g. for event 20110413170148 this file would be fetched::
                20110413170148 directory

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
        myLocalPath = os.path.join(shakemapCacheDir(), self.eventId)
        myXMLFile = os.path.join(myLocalPath, 'output', self.fileName())
        if os.path.exists(myXMLFile):
            return myLocalPath

        # fetch from sftp
        trials = [i + 1 for i in xrange(theRetries)]
        remote_path = os.path.join(self.sftpclient.workdir_path, self.eventId)
        for my_counter in trials:
            myLastError = None
            try:
                self.sftpclient.download_path(remote_path, shakemapCacheDir())
            except NetworkError, e:
                myLastError = e
            except:
                LOGGER.exception('Could not fetch shake event from server %s'
                                 % remote_path)
                raise
            if myLastError is None:
                return myLocalPath
            else:
                self.reconnectSFTP()

            LOGGER.info('Fetching failed, attempt %s' % my_counter)
        LOGGER.exception('Could not fetch shake event from server %s'
                             % remote_path)
        raise Exception('Could not fetch shake event from server %s'
                        % remote_path)

    def extractDir(self):
        """A helper method to get the path to the extracted datasets.

        Args: None

        Returns: A string representing the absolute local filesystem path to
            the unzipped shake event dir. e.g.
            :file:`/tmp/inasafe/realtime/shakemaps-extracted/20120726022003`

        Raises: Any exceptions will be propogated
        """
        return os.path.join(shakemapExtractDir(), self.eventId)

    def extract(self, theForceFlag=False):
        """Checking the grid.xml file in the machine, if found use it.
        Else, download from the server
        """
        myFinalGridXmlFile = os.path.join(self.extractDir(), 'grid.xml')
        if not os.path.exists(self.extractDir()):
            mkDir(self.extractDir())
        if theForceFlag or self.forceFlag:
            self.removeExtractedFiles()
        elif os.path.exists(myFinalGridXmlFile):
            return myFinalGridXmlFile

        # download data
        myLocalPath = self.fetchFile()
        # move grid.xml to the correct directory
        myExpectedGridXmlFile = os.path.join(myLocalPath, 'output', 'grid.xml')
        if not os.path.exists(myExpectedGridXmlFile):
            raise FileNotFoundError('The output does not contain an '
                                       '%s file.' % myExpectedGridXmlFile)

        # move the file we care about to the top of the extract dir
        shutil.copyfile(os.path.join(self.extractDir(), myExpectedGridXmlFile),
            myFinalGridXmlFile)
        if (not os.path.exists(myFinalGridXmlFile)):
            raise CopyError('Error copying grid.xml')
        return myFinalGridXmlFile

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
