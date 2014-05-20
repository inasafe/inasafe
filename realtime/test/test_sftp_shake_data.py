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

from realtime.sftp_shake_data import SftpShakeData

# Shake event ID for this test
SHAKE_ID = '20120726022003'

# Create sftp client once
SFTP_CLIENT = SftpShakeData()


class SFtpShakeDataTest(unittest.TestCase):

    #noinspection PyMethodMayBeStatic
    def test_create_event(self):
        """Test create shake data."""
        try:
            event_one = SftpShakeData()
            event_two = SftpShakeData(event=SHAKE_ID)
            event_three = SftpShakeData(
                event=SHAKE_ID,
                force_flag=True)
            self.assertIsNotNone(event_one)
            self.assertIsNotNone(event_two)
            self.assertIsNotNone(event_three)
        except:
            raise

    #noinspection PyMethodMayBeStatic
    def test_download_data(self):
        """Test downloading data from server."""
        print SFTP_CLIENT.fetch_file()

    #noinspection PyMethodMayBeStatic
    def test_get_latest_event_id(self):
        """Test get latest event id
        """
        latest_id = SFTP_CLIENT.get_latest_event_id()
        print latest_id
        self.assertIsNotNone(
            latest_id, 'There is not latest event, please check')

    #noinspection PyMethodMayBeStatic
    def test_get_list_event_ids(self):
        """Test get list event id."""
        list_id = SFTP_CLIENT.get_list_event_ids()
        print list_id
        self.assertTrue(
            len(list_id) > 0, 'num of list event is zero, please check')

    #noinspection PyMethodMayBeStatic
    def test_reconnect_sftp(self):
        """Test to reconnect SFTP."""
        sftp_client = SFTP_CLIENT.sftp_client
        SFTP_CLIENT.reconnect_sftp()
        new_sftp_client = SFTP_CLIENT.sftp_client
        self.assertNotEqual(sftp_client, new_sftp_client, 'message')
        self.assertIsNotNone(new_sftp_client, 'new sftp is none')

    #noinspection PyMethodMayBeStatic
    def test_is_on_server(self):
        """Test to check if a event is in server."""
        self.assertTrue(SFTP_CLIENT.is_on_server(), 'Event is not in server')

    #noinspection PyMethodMayBeStatic
    def test_extract(self):
        """Test extracting data to be used in earth quake realtime."""
        SFTP_CLIENT.extract()
        final_grid_xml_file = os.path.join(
            SFTP_CLIENT.extract_dir(), 'grid.xml')
        self.assertTrue(
            os.path.exists(final_grid_xml_file), 'grid.xml not found')

if __name__ == '__main__':
    suite = unittest.makeSuite(SFtpShakeDataTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
