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
from datetime import datetime

from safe.api import temp_dir
from realtime.sftp_client import SFtpClient
from realtime.test.test_sftp_client import run_monkey_patching_sftp_client
from realtime.sftp_shake_data import SftpShakeData
from realtime.server_config import (
    BASE_URL,
    USERNAME,
    PASSWORD,
    BASE_PATH)
from realtime.utilities import (
    is_event_id,
    mk_dir,
    shakemap_cache_dir,
    shakemap_extract_dir)
from realtime.exceptions import (
    EventIdError,
    NetworkError)

# Shake event ID for this test
SHAKE_ID = '20120726022003'


class MockSFtpShakeData(object):
    """A fake class to mock SFtpShakeData behavior.

        .. versionadded:: 2.1
    """

    def __init__(self,
                 event=None,
                 host=BASE_URL,
                 user_name=USERNAME,
                 password=PASSWORD,
                 working_dir=BASE_PATH,
                 force_flag=False):
        """Constructor for the MockSftpShakeData class."""
        self.event_id = event
        self.host = host
        self.username = user_name
        self.password = password
        self.working_dir = working_dir
        self.force_flag = force_flag
        self.input_file_name = 'grid.xml'

        run_monkey_patching_sftp_client()
        self.sftp_client = SFtpClient(
            self.host, self.username, self.password, self.working_dir)

        # Make working dir point to the local directory
        # Make temp dir
        temp_dir('realtime-test')
        # Download data from test to that temp dir
        remote_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                SHAKE_ID))
        local_path = temp_dir('realtime-test')
        self.sftp_client.download_path(remote_path, local_path)
        self.sftp_client.working_dir = local_path
        self.sftp_client.working_dir_path = local_path

        # AG: For now just assume that if self.event_id is not None (which
        # means provided in the constructor), that event_id is always valid.
        # Just be sure that when calling MockSFtpShakeData with event_id
        # being provided, that event_id exists in the local file.
        if self.event_id is None:
            try:
                self.get_latest_event_id()
            except NetworkError:
                raise

        # If event_id is still None after all the above, moan....
        if self.event_id is None:
            message = ('No id was passed to the constructor and the  latest '
                       'id could not be retrieved from the server.')
            raise EventIdError(message)

    def __del__(self):
        """Destructor of the class."""
        # Delete the files that we make in the init for the shake data
        shutil.rmtree(temp_dir('realtime-test'))

    def reconnect_sftp(self):
        """Mock to reconnect_sftp of SFtpShakeData class"""
        self.sftp_client = MockSFtpShakeData(
            self.host, self.username, self.password, self.working_dir)

    def is_on_server(self):
        """Mock to is_on_server."""
        remote_xml_path = os.path.join(
            self.sftp_client.working_dir_path, self.event_id)
        return os.path.exists(remote_xml_path)

    def get_list_event_ids(self):
        """Mock get_list_event_ids
        """
        dirs = self.sftp_client.get_listing(function=is_event_id)
        if len(dirs) == 0:
            raise Exception('List event is empty')
        return dirs

    def get_latest_event_id(self):
        """Mock get_latest event_id from SFtpShakeData class."""
        event_ids = self.get_list_event_ids()

        now = datetime.now()
        now = int(
            '%04d%02d%02d%02d%02d%02d' % (
                now.year, now.month, now.day, now.hour, now.minute, now.second))

        if event_ids is not None:
            event_ids.sort()

        latest_event_id = now + 1
        while int(latest_event_id) > now:
            if len(event_ids) < 1:
                raise EventIdError('Latest Event Id could not be obtained')
            latest_event_id = event_ids.pop()

        self.event_id = latest_event_id
        return self.event_id

    def fetch_file(self, retries=3):
        """Mock fetch_file from SFTPShakeData class."""
        local_path = os.path.join(shakemap_cache_dir(), self.event_id)
        local_parent_path = os.path.join(local_path, 'output')
        xml_file = os.path.join(local_parent_path, self.input_file_name)
        if os.path.exists(xml_file):
            return local_path

        # fetch from sftp
        trials = [i + 1 for i in xrange(retries)]
        remote_path = os.path.join(
            self.sftp_client.working_dir_path, self.event_id)
        xml_remote_path = os.path.join(
            remote_path, 'output', self.input_file_name)

        for counter in trials:
            last_error = None
            try:
                mk_dir(local_path)
                mk_dir(os.path.join(local_path, 'output'))
                self.sftp_client.download_path(
                    xml_remote_path, local_parent_path)
            except NetworkError, e:
                last_error = e
            except:
                raise
            if last_error is None:
                return local_path
            else:
                self.reconnect_sftp()
        raise Exception('Could not fetch shake event from server %s'
                        % remote_path)

    def extract_dir(self):
        """A helper method to get the path to the extracted datasets.

        :return: A string representing the absolute local filesystem path to
            the unzipped shake event dir. e.g.
            :file:`/tmp/inasafe/realtime/shakemaps-extracted/20120726022003`
        :rtype: str

        :raises: Any exceptions will be propagated.
        """
        return os.path.join(shakemap_extract_dir(), self.event_id)

    def extract(self, force_flag=False):
        """Checking the grid.xml file in the machine, if found use it.
        Else, download from the server.

        :param force_flag: force flag to extract.
        :type force_flag: bool

        :return: a string containing the grid.xml paths e.g.::
            grid_xml = myShakeData.extract()
            print grid_xml
            /tmp/inasafe/realtime/shakemaps-extracted/20120726022003/grid.xml
        """
        final_grid_xml_file = os.path.join(self.extract_dir(), 'grid.xml')
        if not os.path.exists(self.extract_dir()):
            mk_dir(self.extract_dir())
        if force_flag or self.force_flag:
            self.remove_extracted_files()
        elif os.path.exists(final_grid_xml_file):
            return final_grid_xml_file

        # download data
        local_path = self.fetch_file()
        # move grid.xml to the correct directory
        expected_grid_xml_file = os.path.join(local_path, 'output', 'grid.xml')
        if not os.path.exists(expected_grid_xml_file):
            raise FileNotFoundError(
                'The output does not contain an ''%s file.' %
                expected_grid_xml_file)

        # move the file we care about to the top of the extract dir
        shutil.copyfile(os.path.join(
            self.extract_dir(), expected_grid_xml_file), final_grid_xml_file)
        if not os.path.exists(final_grid_xml_file):
            raise CopyError('Error copying grid.xml')
        return final_grid_xml_file

    def remove_extracted_files(self):
        """Tidy up the filesystem by removing all extracted files
        for the given event instance.

        :raises: Any error e.g. file permission error will be raised.
        """
        extracted_dir = self.extract_dir()
        if os.path.isdir(extracted_dir):
            shutil.rmtree(extracted_dir)


class SFtpShakeDataTest(unittest.TestCase):
    def test_constructor(self):
        """Test create shake data."""
        try:
            event_one = MockSFtpShakeData()
            event_two = MockSFtpShakeData(event=SHAKE_ID)

            self.assertIsNotNone(event_one)
            self.assertIsNotNone(event_two)
        except:
            raise

    def test_reconnect_sftp(self):
        """Test to reconnect SFTP."""
        sftp_shake_data = MockSFtpShakeData()
        sftp_client = sftp_shake_data.sftp_client
        sftp_shake_data.reconnect_sftp()
        new_sftp_client = sftp_shake_data.sftp_client

        message = 'Oh no, we got the same sftp client after reconnecting!'
        self.assertNotEqual(sftp_client, new_sftp_client, message)
        message = 'Oh dear, the new sftp object is None after reconnecting'
        self.assertIsNotNone(new_sftp_client, message)

    def test_get_list_event_ids(self):
        """Test get list event id."""
        sftp_shake_data = MockSFtpShakeData()
        list_id = sftp_shake_data.get_list_event_ids()
        expected_list_id = [SHAKE_ID]
        message = 'I got %s for the event ID in the server, Expectation %s' % (
            list_id, expected_list_id)
        self.assertEqual(list_id, expected_list_id, message)

    def test_get_latest_event_id(self):
        """Test get latest event id."""
        sftp_shake_data = MockSFtpShakeData()
        latest_id = sftp_shake_data.get_latest_event_id()
        # The latest event ID should be = SHAKE_ID since there's only one
        expected_event_id = SHAKE_ID
        message = 'I got %s for this latest event id, Expectation %s' % (
            latest_id, expected_event_id)
        self.assertEqual(expected_event_id, latest_id, message)

    def test_fetch_file(self):
        """Test fetch data."""
        sftp_shake_data = MockSFtpShakeData()
        local_path = sftp_shake_data.fetch_file()
        expected_path = os.path.join(shakemap_cache_dir(), SHAKE_ID)
        message = 'File should be fetched to %s, I got %s' % (
            expected_path,  local_path)
        self.assertEqual(local_path, expected_path, message)

    def test_is_on_server(self):
        """Test to check if a event is in server."""
        sftp_shake_data = MockSFtpShakeData()
        message = 'Event does not exist in the server.'
        self.assertTrue(sftp_shake_data.is_on_server(), message)

    def test_extract(self):
        """Test extracting data to be used in earth quake realtime."""
        sftp_shake_data = MockSFtpShakeData()
        sftp_shake_data.extract()
        final_grid_xml_file = os.path.join(
            sftp_shake_data.extract_dir(), 'grid.xml')
        self.assertTrue(
            os.path.exists(final_grid_xml_file), 'grid.xml not found')

if __name__ == '__main__':
    suite = unittest.makeSuite(SFtpShakeDataTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
