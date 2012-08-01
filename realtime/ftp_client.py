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

from ftplib import FTP
import urllib2
from utils import shakemapZipDir

class FtpClient:
    """A utility class that contains methods to fetch a listings and files
        from an FTP server"""
    def __init__(self,
                 theBaseUrl = '118.97.83.243',
                 thePasvMode = True,
                 theBackend = 'urllib2'):
        """Constructor for the FtpClient class

        Args:
            * theBaseUrl - (Optional) an ftp server to connect to. If ommitted
              it will default to ftp://118.97.83.243/
            * thePasvMode - (Optional) whether passive connections should be
              made. Defaults to True.
            * theBackend - (Optional). Which ftp backend to use. Defaults to
              urllib2

        Returns:
            None

        Raises:
            None

        """
        self.baseUrl = theBaseUrl
        self.pasv = thePasvMode
        self.backend = theBackend

    def availableBackends(self):
        """Return a tuple of the available ftp backends that can be used.

        Args: None

        Returns: A list of strings, each representing the name of a usable
           backend.

        Raises: None
        """
        return ('urllib2', 'ftplib')

    def getListing(self):
        """
        Get a listing of available files from the ftp server
        Adapted from Ole's original shake library.

        Args:
            None

        Returns:
            A sorted list of files urls, with the newest files occurring at the
            end of the list.
        Raises:
        """

        if 'ftplib' in self.backend:
            return self._getListingUsingFtpLib()
        else:
            return self._getListingUsingUrlLib2()

    def _getListingUsingUrlLib2(self, theExtension='zip'):
        """Get a listing of the available files using the urllib2 library.

        Args:
          theExtension - (Optional) Filename suffix to filter the listing by.
            Defaults to zip.

        Returns:
          A list containing the unique filenames (if any) that match the
          supplied extension suffix.

        Raises:
          None
        """
        myUrl = 'ftp://%s' % self.baseUrl
        myRequest = urllib2.Request(myUrl)
        try:
            myFileId = urllib2.urlopen(myRequest, timeout=60)
        except Exception, e:
            print e.reason
            raise

        myList = []
        for myLine in myFileId.readlines():
            myFields = myLine.strip().split()
            if myFields[-1].endswith('.%s' % theExtension):
                myList.append(myUrl + '/' + myFields[-1])

        return myList

    def _getListingUsingFtpLib(self):
        """Get a listing of the available files using the ftp library.

        Args: None

        Returns: A string containing the list of files available in the
        root directory of the baseUrl.

        Raises: None
        """

        ftp = FTP(self.baseUrl)
        ftp.set_pasv(self.pasv)
        ftp.login()
        ftp.retrlines('LIST')
        ftp.quit()

    def getFile(self, theUrlPath, theFilePath):
        """
        Get a file from the ftp server using the active backend.

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
        if 'ftplib' in self.backend:
            return self._getFileUsingFtpLib(theUrlPath, theFilePath)
        else:
            return self._getFileUsingUrlLib2(theUrlPath, theFilePath)

    def _getFileUsingUrlLib2(self, theUrlPath, theFilePath):
        """Get a file from the ftp server using the urllib2 backend.

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
        myUrl = 'ftp://%s/%s' % (self.baseUrl, theUrlPath)
        myRequest = urllib2.Request(myUrl)
        try:
            myUrlHandle = urllib2.urlopen(myRequest, timeout=60)
            myFile = file(theFilePath, 'wb')
            myFile.write(myUrlHandle.read())
            myFile.close()
        except Exception, e:
            print e.reason
            raise


    def _getFileUsingFtpLib(self, theUrlPath, theFilePath):
        """Get a file from the ftp server using the ftplib backend.

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
        myUrl = 'ftp://%s/%s' % (self.baseUrl, theUrlPath)
        myFtp = FTP(myUrl)
        myFtp.set_pasv(self.pasv)
        myFtp.login()
        myFtp.retrbinary('RETR %s' % theUrlPath, open(theFilePath, 'wb').write)
        myFtp.quit()


