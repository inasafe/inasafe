"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Ftp Client for Retrieving shake data.**

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

class FtpClient:
    """A utility class that contains methods to fetch a listing of shakemaps
        from an FTP server"""
    def __init__(self, theBaseUrl = 'ftp://118.97.83.243/'):
        """Constructor for the FtpClient class

        Args:
            theBaseUrl - (Optional) an ftp server to connect to. If ommitted
            it will default to ftp://118.97.83.243/

        Returns:
            None

        Raises:
            None

        """
        self.baseUrl = theBaseUrl

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
        myFileId = urllib2.urlopen(self.baseUrl)
        myList = []
        for myLine in myFileId.readlines():
            myFields = myLine.strip().split()
            if myFields[-1].endswith('.zip'):
                myList.append(url + '/' + myFields[-1])

        return myList



