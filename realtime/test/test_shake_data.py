# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Shake Data Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
import unittest

from realtime.earthquake.shake_data import ShakeData
from safe.common.utilities import temp_dir
from safe.test.utilities import standard_data_path

# Shake ID for this test
SHAKE_ID = '20131105060809'


class ShakeDataTest(unittest.TestCase):
    def setUp(self):
        """Setup before each test."""
        # Download files (which are local files) to realtime-test temp folder
        local_path = os.path.join(temp_dir('realtime-test'))
        shake_data = standard_data_path('hazard', 'shake_data', SHAKE_ID)
        shutil.copytree(
            shake_data, os.path.join(local_path, 'shakemaps', SHAKE_ID))

    def tearDown(self):
        """Action after each test is called."""
        # Delete the files that we make in the init for the shake data
        shutil.rmtree(temp_dir('realtime-test'))

    def test_constructor(self):
        """Test create shake data."""
        local_path = os.path.join(temp_dir('realtime-test'), 'shakemaps')
        try:
            event_one = ShakeData(working_dir=local_path)
            event_two = ShakeData(
                working_dir=temp_dir('realtime-test'),
                event=SHAKE_ID)

            self.assertEqual(event_one.event_id, SHAKE_ID)
            self.assertEqual(event_two.event_id, SHAKE_ID)
        except:
            raise

    def test_validate_event(self):
        """Test validate_event works."""
        local_path = os.path.join(temp_dir('realtime-test'), 'shakemaps')
        event = ShakeData(working_dir=local_path)
        self.assertTrue(event.validate_event())

    def test_get_list_event_ids(self):
        """Test get_list_event_ids."""
        local_path = os.path.join(temp_dir('realtime-test'), 'shakemaps')
        shake_data = ShakeData(working_dir=local_path)
        list_id = shake_data.get_list_event_ids()
        expected_list_id = [SHAKE_ID]
        message = 'I got %s for the event ID in the server, Expectation %s' % (
            list_id, expected_list_id)
        self.assertEqual(list_id, expected_list_id, message)

    def test_get_latest_event_id(self):
        """Test get latest event id."""
        local_path = os.path.join(temp_dir('realtime-test'), 'shakemaps')
        shake_data = ShakeData(working_dir=local_path)

        latest_id = shake_data.get_latest_event_id()
        # The latest event ID should be = SHAKE_ID since there's only one
        expected_event_id = SHAKE_ID
        message = 'I got %s for this latest event id, Expectation %s' % (
            latest_id, expected_event_id)
        self.assertEqual(expected_event_id, latest_id, message)

    def test_extract(self):
        """Test extracting data to be used in earth quake realtime."""
        local_path = os.path.join(temp_dir('realtime-test'), 'shakemaps')
        shake_data = ShakeData(working_dir=local_path)

        shake_data.extract()
        final_grid_xml_file = os.path.join(
            shake_data.extract_dir(), 'grid.xml')
        self.assertTrue(
            os.path.exists(final_grid_xml_file), 'grid.xml not found')

if __name__ == '__main__':
    suite = unittest.makeSuite(ShakeDataTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
