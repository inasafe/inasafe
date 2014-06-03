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
import shutil

from safe.api import temp_dir
from realtime.sftp_client import SFtpClient
from realtime.server_config import (
    BASE_URL,
    USERNAME,
    PASSWORD,
    BASE_PATH)
from realtime.utilities import is_event_id

# Shake ID for this test
SHAKE_ID = '20131105060809'


def mock_init(self,
              host=BASE_URL,
              username=USERNAME,
              password=PASSWORD,
              working_dir=BASE_PATH):
    """Mock method init of SFTPClient class.

    :param host: The remote host.
    :type host: str

    :param username: The username for the host.
    :type username: str

    :param password: The password for given username.
    :type password: str

    :param working_dir: The base path to fetch the files.
    :type working_dir: str
    """
    self.host = host
    self.username = username
    self.password = password
    self.working_dir = working_dir
    self.working_dir_path = working_dir
    self.sftp = shutil
    self.sftp.get = shutil.copy
    self.sftp.listdir = os.listdir


# noinspection PyUnusedLocal
def mock_is_dir(self, path):
    """Mock method is_dir of SFTPClient class.

    :param path: The target path that will be tested.
    :type path: str
    """
    return os.path.isdir(path)


# noinspection PyUnusedLocal
def mock_path_exists(self, path):
    """Mock method path_exists of SFTPClient class.

    :param path: The target path that will be tested.
    :type path: str
    """
    return os.path.exists(path)


def run_monkey_patching_sftp_client():
    """The monkey patching to some methods of SFTPClient."""
    SFtpClient.__init__ = mock_init
    SFtpClient.is_dir = mock_is_dir
    SFtpClient.path_exists = mock_path_exists


class SFtpClientTest(unittest.TestCase):
    """Class to test SFtpClient.

    .. versionchanged:: 2.1
        Use MockSFtpClient to work with local data instead of using
        production server.
    """
    def setUp(self):
        """Setup before each test call."""
        run_monkey_patching_sftp_client()
        # Make temp dir
        temp_dir('realtime-test')

    def tearDown(self):
        """Action after each test call."""
        # Delete temp dir
        shutil.rmtree(temp_dir('realtime-test'))

    def test_download_path(self):
        """Test to download all directories and files under a path."""
        sftp_client = SFtpClient(working_dir=temp_dir('realtime-test'))
        self.assertIsNotNone(sftp_client)

        # Download directories
        remote_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                SHAKE_ID))
        local_path = temp_dir('realtime-test')
        sftp_client.download_path(remote_path, local_path)

        # Check the local_path consist of SHAKE_ID folder
        expected_dir = [SHAKE_ID]
        actual_dir = os.listdir(local_path)
        message = "In the local path, I got: %s dir, Expectation: %s dir" % (
            actual_dir, expected_dir)
        self.assertEqual(expected_dir, actual_dir, message)

        # Inside that SHAKE_ID folder, there should be 'output' folder
        expected_dir = ['output']
        actual_dir = os.listdir(os.path.join(local_path, SHAKE_ID))
        message = "In the local path, I got: %s dir, Expectation: %s dir" % (
            actual_dir, expected_dir)
        self.assertEqual(expected_dir, actual_dir, message)

        # Inside that output folder, there should be 'grid.xml' file
        expected_dir = ['grid.xml']
        actual_dir = os.listdir(os.path.join(local_path, SHAKE_ID, 'output'))
        message = "In the local path, I got: %s dir, Expectation: %s dir" % (
            actual_dir, expected_dir)
        self.assertEqual(expected_dir, actual_dir, message)

    def test_get_listing(self):
        """Test get_listing if it's working correctly."""
        sftp_client = SFtpClient(working_dir=temp_dir('realtime-test'))
        self.assertIsNotNone(sftp_client)

        # Download directories
        remote_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                SHAKE_ID))
        local_path = temp_dir('realtime-test')
        sftp_client.download_path(remote_path, local_path)

        event_ids = sftp_client.get_listing(function=is_event_id)
        expected_event_ids = [SHAKE_ID]
        message = 'In the local path I got %s dir, Expectation %s dir'
        self.assertEqual(event_ids, expected_event_ids, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(SFtpClientTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
