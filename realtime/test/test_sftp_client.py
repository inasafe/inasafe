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

__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '10/01/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os

from realtime.sftp_client import SFtpClient


class SFtpClientTest(unittest.TestCase):
    #noinspection PyMethodMayBeStatic
    def test_get_list_events(self):
        """Test to get all event ids."""
        sftp_client = SFtpClient()
        self.assertIsNotNone(sftp_client)

    #noinspection PyMethodMayBeStatic
    def test_download_path(self):
        """Test to download all directories and files under a path."""
        sftp_client = SFtpClient(working_dir='shakemaps')
        self.assertIsNotNone(sftp_client)

        remote_path = os.path.join(
            sftp_client.sftp.getcwd(), '20130113003746/output/grid.xml')
        local_path = '/tmp/inasafe/'

        sftp_client.download_path(remote_path, local_path)

if __name__ == '__main__':
    suite = unittest.makeSuite(SFtpClientTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
