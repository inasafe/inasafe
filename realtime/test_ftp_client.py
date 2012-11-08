"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Ftp Client Test Cases.**

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

import unittest
import re
from ftp_client import FtpClient


class FtpClientTest(unittest.TestCase):
    """Test the ftp client used to fetch shake listings"""
    # TODO update tests so url host is not hard coded
    _expectedMatches = ('20110413170148.inp.zip',
                             '20110413170148.out.zip')

    def testGetDirectoryListing(self):
        """Check if we can get a nice directory listing"""
        myClient = FtpClient()
        myListing = myClient.getListing()
        #Make it a single string
        myListing = '\n'.join(myListing)
        myMessage = ('Expected this list:\n%s\nTo contain these items:\n%s' %
                      (myListing, self._expectedMatches))
        for myExpectedFile in self._expectedMatches:
            assert re.search(myExpectedFile, myListing), myMessage

    def testGetFile(self):
        """Test that the ftp client can fetch a file ok"""
        myClient = FtpClient()
        myListing = myClient.getListing()
        #Make it a single string
        myListing = '\n'.join(myListing)
        myMessage = ('Expected outcome:\n%s\nActual outcome:\n%s' %
                      (myListing, self._expectedMatches))
        for myExpectedFile in self._expectedMatches:
            assert re.search(myExpectedFile, myListing), myMessage

    def testHasFile(self):
        """Test that the ftp client can check if a file exists"""
        myClient = FtpClient()
        myFile = '20120726022003.inp.zip'
        myMessage = ('Expected that %s exists on the server' % myFile)
        self.assertTrue(myClient.hasFile(myFile), myMessage)

    def testHasFiles(self):
        """Test that the ftp client can check if a list of file exists"""
        myClient = FtpClient()
        myFiles = ['20120726022003.inp.zip', '20120726022003.out.zip']
        myMessage = ('Expected that %s exist on the server' % myFiles)
        self.assertTrue(myClient.hasFiles(myFiles), myMessage)

if __name__ == '__main__':
    suite = unittest.makeSuite(FtpClientTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
