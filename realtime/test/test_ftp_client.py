# coding=utf-8
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
from realtime.ftp_client import FtpClient


class FtpClientTest(unittest.TestCase):
    """Test the ftp client used to fetch shake listings"""
    # TODO update tests so url host is not hard coded
    _expectedMatches = (
        '20110413170148.inp.zip', '20110413170148.out.zip')

    def test_get_directory_listing(self):
        """Check if we can get a nice directory listing"""
        client = FtpClient()
        file_list = client.get_listing()
        #Make it a single string
        file_list = '\n'.join(file_list)
        message = (
            'Expected this list:\n%s\nTo contain these items:\n%s' %
            (file_list, self._expectedMatches))
        for expected_file in self._expectedMatches:
            assert re.search(expected_file, file_list), message

    def test_get_file(self):
        """Test that the ftp client can fetch a file ok"""
        client = FtpClient()
        file_list = client.get_listing()
        #Make it a single string
        file_list = '\n'.join(file_list)
        message = (
            'Expected outcome:\n%s\nActual outcome:\n%s' %
            (file_list, self._expectedMatches))
        for expected_file in self._expectedMatches:
            assert re.search(expected_file, file_list), message

    def test_has_file(self):
        """Test that the ftp client can check if a file exists"""
        client = FtpClient()
        input_file = '20120726022003.inp.zip'
        message = ('Expected that %s exists on the server' % input_file)
        self.assertTrue(client.has_file(input_file), message)

    def test_has_files(self):
        """Test that the ftp client can check if a list of file exists"""
        client = FtpClient()
        input_files = ['20120726022003.inp.zip', '20120726022003.out.zip']
        message = ('Expected that %s exist on the server' % input_files)
        self.assertTrue(client.has_files(input_files), message)

if __name__ == '__main__':
    suite = unittest.makeSuite(FtpClientTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
