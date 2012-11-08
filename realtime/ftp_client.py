"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Ftp Client for Retrieving ftp data.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '19/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import urllib2
import logging

# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE-Realtime')


class FtpClient:
    """A utility class that contains methods to fetch a listings and files
        from an FTP server"""
    def __init__(self,
                 theBaseUrl='118.97.83.243',
                 thePasvMode=True):
        """Constructor for the FtpClient class

        Args:
            * theBaseUrl - (Optional) an ftp server to connect to. If ommitted
              it will default to ftp://118.97.83.243/
            * thePasvMode - (Optional) whether passive connections should be
              made. Defaults to True.

        Returns:
            None

        Raises:
            None

        """
        self.baseUrl = theBaseUrl
        self.pasv = thePasvMode

    def getListing(self, theExtention='zip'):
        """Get a listing of the available files.

        Adapted from Ole's original shake library.

        Args:
          theExtension - (Optional) Filename suffix to filter the listing by.
            Defaults to zip.

        Returns:
          A list containing the unique filenames (if any) that match the
          supplied extension suffix.

        Raises:
          None
        """
        LOGGER.debug('Getting ftp listing for %s', self.baseUrl)
        myUrl = 'ftp://%s' % self.baseUrl
        myRequest = urllib2.Request(myUrl)
        try:
            myFileId = urllib2.urlopen(myRequest, timeout=60)
        except urllib2.URLError, e:
            print e.reason
            raise

        myList = []
        for myLine in myFileId.readlines():
            myFields = myLine.strip().split()
            if myFields[-1].endswith('.%s' % theExtention):
                myList.append(myUrl + '/' + myFields[-1])

        return myList

    def ftpUrlForFile(self, theUrlPath):
        """Get a file from the ftp server.

        Args:
            * theUrlPath - (Mandatory) The path (relative to the ftp root)
              from which the file should be retrieved.
        Returns:
            str - An ftp url e.g. ftp://118.97.83.243/20120726022003.inp.zip
        Raises:
            None
        """
        return 'ftp://%s/%s' % (self.baseUrl, theUrlPath)

    def getFile(self, theUrlPath, theFilePath):
        """Get a file from the ftp server.

         Args:
            * theUrlPath - (Mandatory) The path (relative to the ftp root)
              from which the file should be retrieved.
            * theFilePath - (Mandatory). The path on the filesystem to which
              the file should be saved.
         Returns:
             The path to the downloaded file.

         Raises:
             None
        """
        LOGGER.debug('Getting ftp file: %s', theFilePath)
        myUrl = self.ftpUrlForFile(theUrlPath)
        myRequest = urllib2.Request(myUrl)
        try:
            myUrlHandle = urllib2.urlopen(myRequest, timeout=60)
            myFile = file(theFilePath, 'wb')
            myFile.write(myUrlHandle.read())
            myFile.close()
        except urllib2.URLError, e:
            LOGGER.exception('Bad Url or Timeout')
            raise

    def hasFile(self, theFile):
        """Check if a file is on the ftp server.

         Args:
            * theFile - (Mandatory) The paths (relative to the ftp
                root) to be checked. e.g. '20120726022003.inp.zip',
         Returns:
             bool True if the file exists on the server, otherwise False.

         Raises:
             None
        """
        LOGGER.debug('Checking for ftp file: %s', theFile)
        myList = self.getListing()
        myUrl = self.ftpUrlForFile(theFile)
        return myUrl in myList

    def hasFiles(self, theFiles):
        """Check if a list files is on the ftp server.

        .. seealso: func:`hasFile`

        Args:
            * theFiles: [str, ...] (Mandatory) The paths (relative to the ftp
                root) to be checked. e.g. ['20120726022003.inp.zip',
                '20120726022003.inp.zip']
        Returns:
            bool True if **all** files exists on the server, otherwise False.

        Raises:
            None
        """
        LOGGER.debug('Checking for ftp file: %s', theFiles)
        # Note we don't delegate to hasFile as we want to limit network IO
        myList = self.getListing()
        for myFile in theFiles:
            myUrl = self.ftpUrlForFile(myFile)
            if not myUrl in myList:
                LOGGER.debug('** %s NOT found on server**' % myUrl)
                return False
            LOGGER.debug('%s found on server' % myUrl)
        return True
