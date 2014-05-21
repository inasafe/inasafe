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
from realtime.server_config import (
    BASE_URL,
    USERNAME,
    PASSWORD,
    BASE_PATH)
from realtime.utilities import get_path_tail, mk_dir, is_event_id

# Shake ID for this test
SHAKE_ID = '20120726022003'


class MockSFtpClient(object):
    """A fake class to mock SFtpClient behavior.

    .. versionadded:: 2.1
    """
    def __init__(self,
                 host=BASE_URL,
                 username=USERNAME,
                 password=PASSWORD,
                 working_dir=BASE_PATH):
        """Constructor of the class."""
        self.host = host
        self.username = username
        self.password = password
        self.working_dir = working_dir
        self.working_dir_path = working_dir

    def download_path(self, remote_path, local_path):
        """Mock SftpClient.download_path.

        :param remote_path: Remote path that will be downloaded. Remember
            that since this is a mock, it will actually refer to the local path.
        :type remote_path: str

        :param local_path: The local path that will contain the downloaded
            file.
        :type local_path: str
        """
        # Check if remote_path is exist
        if not os.path.exists(remote_path):
            print 'Remote path %s does not exist.' % remote_path
            return False

        # If the remote_path is a dir, download all files on that dir
        if os.path.isdir(remote_path):
            # get directory name
            dir_name = get_path_tail(remote_path)
            # create directory in local machine
            local_dir_path = os.path.join(local_path, dir_name)
            mk_dir(local_dir_path)
            # list all directories in remote path
            directories = os.listdir(remote_path)
            # iterate recursive
            for directory in directories:
                directory_path = os.path.join(remote_path, directory)
                self.download_path(directory_path, local_dir_path)
        else:
            # download file to local_path
            file_name = get_path_tail(remote_path)
            local_file_path = os.path.join(local_path, file_name)

            shutil.copyfile(remote_path, local_file_path)

    def get_listing(self, remote_dir=None, function=None):
        """Return list of files and directories name under a remote_dir if
        the directory/file is valid for a function.

        :param remote_dir: The remote directory that we want to get the list
            of directory inside it. Remember again it's a mock. So, it will
            refer to local path.
        :type remote_dir: str

        :param function: The function that use the directory.
        :type function: object
        """
        if remote_dir is None:
            remote_dir = self.working_dir_path
        if os.path.exists(remote_dir):
            directories = os.listdir(remote_dir)
        else:
            return None
        valid_list = []
        for directory in directories:
            if function(directory):
                valid_list.append(directory)
        return valid_list


class SFtpClientTest(unittest.TestCase):
    """Class to test SFtpClient.

    .. versionchanged:: 2.1
        Use MockSFtpClient to work with local data instead of using
        production server.
    """
    def setUp(self):
        """Setup before each test call."""
        # Make temp dir
        temp_dir('realtime-test')

    def tearDown(self):
        """Action after each test call."""
        # Delete temp dir
        shutil.rmtree(temp_dir('realtime-test'))

    def test_download_path(self):
        """Test to download all directories and files under a path."""
        sftp_client = MockSFtpClient(working_dir=temp_dir('realtime-test'))
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
        sftp_client = MockSFtpClient(working_dir=temp_dir('realtime-test'))
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
