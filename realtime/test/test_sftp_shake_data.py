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
import os
import unittest
import shutil

from safe.api import temp_dir
from realtime.sftp_client import SFtpClient
from realtime.test.test_sftp_client import run_monkey_patching_sftp_client
from realtime.sftp_shake_data import SftpShakeData
from realtime.utilities import shakemap_cache_dir

# Shake event ID for this test
SHAKE_ID = '20131105060809'


class SFtpShakeDataTest(unittest.TestCase):
    def setUp(self):
        """Setup before each test."""
        # Call sftp client monkey patching before running each tests
        run_monkey_patching_sftp_client()

        # Download files (which are local files) to realtime-test temp folder
        # AG:
        # So since we're using local data, in instantiating SFTPShakeData,
        # please pass the working dir to the local dir
        sftp_client = SFtpClient(working_dir=temp_dir('realtime-test'))
        local_path = temp_dir('realtime-test')
        remote_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                SHAKE_ID))
        sftp_client.download_path(remote_path, local_path)

    def tearDown(self):
        """Action after each test is called."""
        # Delete the files that we make in the init for the shake data
        shutil.rmtree(temp_dir('realtime-test'))

    def test_constructor(self):
        """Test create shake data."""
        try:
            event_one = SftpShakeData(working_dir=temp_dir('realtime-test'))
            event_two = SftpShakeData(
                event=SHAKE_ID,
                working_dir=temp_dir('realtime-test'))

            self.assertIsNotNone(event_one)
            self.assertIsNotNone(event_two)
        except:
            raise

    def test_reconnect_sftp(self):
        """Test to reconnect SFTP."""
        sftp_shake_data = SftpShakeData(working_dir=temp_dir('realtime-test'))
        sftp_client = sftp_shake_data.sftp_client
        sftp_shake_data.reconnect_sftp()
        new_sftp_client = sftp_shake_data.sftp_client

        message = 'Oh no, we got the same sftp client after reconnecting!'
        self.assertNotEqual(sftp_client, new_sftp_client, message)
        message = 'Oh dear, the new sftp object is None after reconnecting'
        self.assertIsNotNone(new_sftp_client, message)

    def test_get_list_event_ids(self):
        """Test get list event id."""
        sftp_shake_data = SftpShakeData(working_dir=temp_dir('realtime-test'))
        list_id = sftp_shake_data.get_list_event_ids()
        expected_list_id = [SHAKE_ID]
        message = 'I got %s for the event ID in the server, Expectation %s' % (
            list_id, expected_list_id)
        self.assertEqual(list_id, expected_list_id, message)

    def test_get_latest_event_id(self):
        """Test get latest event id."""
        sftp_shake_data = SftpShakeData(working_dir=temp_dir('realtime-test'))
        latest_id = sftp_shake_data.get_latest_event_id()
        # The latest event ID should be = SHAKE_ID since there's only one
        expected_event_id = SHAKE_ID
        message = 'I got %s for this latest event id, Expectation %s' % (
            latest_id, expected_event_id)
        self.assertEqual(expected_event_id, latest_id, message)

    def test_fetch_file(self):
        """Test fetch data."""
        sftp_shake_data = SftpShakeData(working_dir=temp_dir('realtime-test'))
        local_path = sftp_shake_data.fetch_file()
        expected_path = os.path.join(shakemap_cache_dir(), SHAKE_ID)
        message = 'File should be fetched to %s, I got %s' % (
            expected_path, local_path)
        self.assertEqual(local_path, expected_path, message)

    def test_is_on_server(self):
        """Test to check if a event is in server."""
        sftp_shake_data = SftpShakeData(working_dir=temp_dir('realtime-test'))
        message = 'Event does not exist in the server.'
        self.assertTrue(sftp_shake_data.is_on_server(), message)

    def test_extract(self):
        """Test extracting data to be used in earth quake realtime."""
        sftp_shake_data = SftpShakeData(working_dir=temp_dir('realtime-test'))
        sftp_shake_data.extract()
        final_grid_xml_file = os.path.join(
            sftp_shake_data.extract_dir(), 'grid.xml')
        self.assertTrue(
            os.path.exists(final_grid_xml_file), 'grid.xml not found')

if __name__ == '__main__':
    suite = unittest.makeSuite(SFtpShakeDataTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
