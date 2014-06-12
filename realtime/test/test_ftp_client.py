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
import os
import shutil

from safe.api import temp_dir
from realtime.ftp_client import FtpClient


# pylint: disable=W0613
def mock_get_listing(self, extension='zip'):
    """Mock get_listing of ftp_client.

    It is pointed to local folder we have.

    :param extension: (Optional) Filename suffix to filter the listing by.
        Defaults to zip.

    :returns: A list containing the unique filenames (if any) that match
        the supplied extension suffix.
    """
    base_url = 'ftp://%s' % self.base_url
    local_shake_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../fixtures/shake_data'))
    file_list = []
    for filename in os.listdir(local_shake_dir):
        if filename.endswith('.%s' % extension):
            file_list.append(base_url + '/' + filename)
    return file_list
# pylint: enable=W0613


# noinspection PyUnusedLocal
# pylint: disable=W0613
def mock_get_file(self, url_path, file_path):
    """Mock get_file of ftp_client.

     :param url_path: (Mandatory) The path (relative to the ftp root)
          from which the file should be retrieved.

     :param file_path: (Mandatory). The path on the filesystem to which
          the file should be saved.

     :return: The path to the downloaded file.
    """
    local_shake_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../fixtures/shake_data'))
    source_file_path = os.path.join(local_shake_dir, url_path)
    shutil.copy(source_file_path, file_path)
# pylint: enable=W0613


def run_monkey_patching_ftp_client():
    """The monkey patching to a method of FTPClient."""
    FtpClient.get_listing = mock_get_listing
    FtpClient.get_file = mock_get_file


class FtpClientTest(unittest.TestCase):
    """Test the ftp client used to fetch shake listings"""
    # TODO update tests so url host is not hard coded
    def setUp(self):
        """Run before calling each test."""
        run_monkey_patching_ftp_client()
        temp_dir('realtime-test')

    def tearDown(self):
        """Action after each test is called."""
        # Delete temp dir
        shutil.rmtree(temp_dir('realtime-test'))

    def test_get_directory_listing(self):
        """Check if we can get a nice directory listing"""
        client = FtpClient()
        file_list = client.get_listing()
        #Make it a single string
        file_list = '\n'.join(file_list)
        expected_output = ['20120726022003.inp.zip', '20120726022003.out.zip']
        message = (
            'Expected this list:\n%s\nTo contain these items:\n%s' %
            (file_list, expected_output))
        for expected_file in expected_output:
            assert re.search(expected_file, file_list), message

    def test_get_file(self):
        """Test that the ftp client can fetch a file ok"""
        client = FtpClient()

        local_path = os.path.join(
            temp_dir('realtime-test'),
            '20120726022003.inp.zip')
        client.get_file('20120726022003.inp.zip', local_path)
        message = 'Function get_file is not working correctly.'
        self.assertTrue(os.path.exists(local_path), message)

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
