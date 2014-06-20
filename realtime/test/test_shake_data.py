# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Tests Shake Data functionality related to shakemaps.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
import unittest

from realtime.shake_data import ShakeData
from realtime.utilities import (
    shakemap_zip_dir,
    purge_working_data,
    shakemap_extract_dir,
    base_data_dir)
from realtime.test.test_ftp_client import run_monkey_patching_ftp_client

# Clear away working dirs so we can be sure they are
# actually created
purge_working_data()

# The InaSAFE Working Directory
INASAFE_WORK_DIR = base_data_dir()

# Shake ID for this test
SHAKE_ID = '20120726022003'


class TestShakeMap(unittest.TestCase):
    """Testing for the shakemap class"""

    #noinspection PyPep8Naming
    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir."""
        # Run monkey patching to ftp_client
        run_monkey_patching_ftp_client()

        output_file = '20120726022003.out.zip'
        input_file = '20120726022003.inp.zip'
        output_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                output_file))
        input_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                input_file))
        shutil.copyfile(
            output_path,
            os.path.join(shakemap_zip_dir(),
                         output_file))
        shutil.copyfile(
            input_path,
            os.path.join(shakemap_zip_dir(),
                         input_file))

        #TODO Downloaded data should be removed before each test

    def test_get_shake_map_input(self):
        """Check that we can retrieve a shakemap 'inp' input file."""
        shake_data = ShakeData(SHAKE_ID)
        shakemap_file = shake_data.fetch_input()
        expected_file = os.path.join(
            shakemap_zip_dir(), SHAKE_ID + '.inp.zip')
        message = 'Expected path for downloaded shakemap INP not received'
        self.assertEqual(shakemap_file, expected_file, message)

    def test_get_shake_map_output(self):
        """Check that we can retrieve a shakemap 'out' input file."""
        shake_data = ShakeData(SHAKE_ID)
        shakemap_file = shake_data.fetch_output()
        expected_file = os.path.join(
            shakemap_zip_dir(), SHAKE_ID + '.out.zip')
        message = 'Expected path for downloaded shakemap OUT not received'
        self.assertEqual(shakemap_file, expected_file, message)

    def test_get_remote_shake_map(self):
        """Check that we can retrieve both input and output from ftp at once.
        """
        shake_data = ShakeData(SHAKE_ID)

        expected_input_file = os.path.join(
            shakemap_zip_dir(), SHAKE_ID + '.inp.zip')
        expected_output_file = os.path.join(
            shakemap_zip_dir(), SHAKE_ID + '.out.zip')

        if os.path.exists(expected_input_file):
            os.remove(expected_input_file)
        if os.path.exists(expected_output_file):
            os.remove(expected_output_file)

        input_file, output_file = shake_data.fetch_event()
        message = ('Expected path for downloaded shakemap INP not received'
                   '\nExpected: %s\nGot: %s' %
                   (expected_output_file, output_file))
        self.assertEqual(input_file, expected_input_file, message)
        message = ('Expected path for downloaded shakemap OUT not received'
                   '\nExpected: %s\nGot: %s' %
                   (expected_output_file, output_file))
        self.assertEqual(output_file, expected_output_file, message)

        self.assertTrue(os.path.exists(expected_input_file))
        self.assertTrue(os.path.exists(expected_output_file))

    def test_get_cached_shake_map(self):
        """Check that we can retrieve both input and output from ftp at once.
        """
        shake_data = ShakeData(SHAKE_ID)
        input_file, output_file = shake_data.fetch_event()

        expected_input_file = os.path.join(
            shakemap_zip_dir(), SHAKE_ID + '.inp.zip')
        expected_output_file = os.path.join(
            shakemap_zip_dir(), SHAKE_ID + '.out.zip')

        message = ('Expected path for downloaded shakemap INP not received'
                   '\nExpected: %s\nGot: %s' %
                   (expected_output_file, output_file))
        self.assertEqual(input_file, expected_input_file, message)
        message = ('Expected path for downloaded shakemap OUT not received'
                   '\nExpected: %s\nGot: %s' %
                   (expected_output_file, output_file))
        self.assertEqual(output_file, expected_output_file, message)

    def test_get_latest_shake_map(self):
        """Check that we can retrieve the latest shake event."""
        # Simply dont set the event id in the ctor to get the latest
        shake_data = ShakeData()
        input_file, output_file = shake_data.fetch_event()
        event_id = shake_data.event_id
        expected_input_file = os.path.join(shakemap_zip_dir(),
                                           event_id + '.inp.zip')
        expected_output_file = os.path.join(shakemap_zip_dir(),
                                            event_id + '.out.zip')
        message = ('Expected path for downloaded shakemap INP not received'
                   '\nExpected: %s\nGot: %s' %
                   (expected_output_file, output_file))
        self.assertEqual(input_file, expected_input_file, message)
        message = ('Expected path for downloaded shakemap OUT not received'
                   '\nExpected: %s\nGot: %s' %
                   (expected_output_file, output_file))
        self.assertEqual(output_file, expected_output_file, message)

    def test_extract_shake_map(self):
        """Test that we can extract the shakemap inp and out files."""
        shake_data = ShakeData(SHAKE_ID)
        grid_xml = shake_data.extract(force_flag=True)

        extract_dir = shakemap_extract_dir()

        expected_grid_xml = os.path.join(
            extract_dir, '20120726022003/grid.xml')
        message = 'Expected: %s\nGot: %s\n' % (
            str(expected_grid_xml), str(grid_xml))
        self.assertEqual(expected_grid_xml, grid_xml, message)
        self.assertTrue(os.path.exists(grid_xml))

    def test_check_event_is_on_server(self):
        """Test that we can check if an event is on the server."""
        shake_data = ShakeData(SHAKE_ID)
        self.assertTrue(shake_data.is_on_server(),
                        ('Data for %s is on server' % SHAKE_ID))

    #noinspection PyMethodMayBeStatic
    def test_cache_paths(self):
        """Check we compute local cache paths properly."""
        shake_data = ShakeData(SHAKE_ID)
        expected_input_path = ('%s/shakemaps-zipped/20120726022003.inp.zip' %
                               INASAFE_WORK_DIR)
        expected_output_path = ('%s/shakemaps-zipped/20120726022003.out.zip' %
                                INASAFE_WORK_DIR)
        input_path, output_path = shake_data.cache_paths()

        message = 'Expected: %s\nGot: %s' % (expected_input_path, input_path)
        self.assertEqual(input_path, expected_input_path, message)

        message = 'Expected: %s\nGot: %s' % (expected_output_path, output_path)
        self.assertEqual(output_path, expected_output_path, message)

    #noinspection PyMethodMayBeStatic
    def test_file_names(self):
        """Check we compute file names properly."""
        shake_data = ShakeData(SHAKE_ID)
        expected_input_file_name = '20120726022003.inp.zip'
        expected_output_file_name = '20120726022003.out.zip'
        input_file_name, output_file_name = shake_data.file_names()

        message = 'Expected: %s\nGot: %s' % (
            expected_input_file_name, input_file_name)
        self.assertEqual(input_file_name, expected_input_file_name, message)

        message = 'Expected: %s\nGot: %s' % (
            expected_output_file_name, output_file_name)
        self.assertEqual(output_file_name, expected_output_file_name, message)

if __name__ == '__main__':
    unittest.main()
