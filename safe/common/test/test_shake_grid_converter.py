# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Converter Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__date__ = '27/03/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
from safe.common.shake_grid_converter import (
    ShakeGridConverter,
    convert_mmi_data)
from safe.common.utilities import unique_filename, temp_dir

from safe.common.testing import TESTDATA

# Parse the grid once and use it for all tests to fasten the tests
GRID_PATH = os.path.join(TESTDATA, 'grid.xml')
SHAKE_GRID_CONVERTER = ShakeGridConverter(GRID_PATH)


class ConverterTest(unittest.TestCase):
    def test_extract_date_time(self):
        """Test extract_date_time giving the correct output."""
        # Test on SHAKE_GRID_CONVERTER
        expected_year = 2014
        message = 'Expected year should be %s, I got %s' % (
            expected_year, SHAKE_GRID_CONVERTER.year)
        self.assertEqual(SHAKE_GRID_CONVERTER.year, expected_year, message)

        expected_month = 5
        message = 'Expected month should be %s, I got %s' % (
            expected_month, SHAKE_GRID_CONVERTER.month)
        self.assertEqual(SHAKE_GRID_CONVERTER.month, expected_month, message)

        expected_day = 10
        message = 'Expected day should be %s, I got %s' % (
            expected_day, SHAKE_GRID_CONVERTER.day)
        self.assertEqual(SHAKE_GRID_CONVERTER.day, expected_day, message)

        expected_hour = 1
        message = 'Expected hour should be %s, I got %s' % (
            expected_hour, SHAKE_GRID_CONVERTER.hour)
        self.assertEqual(SHAKE_GRID_CONVERTER.hour, expected_hour, message)

        expected_minute = 2
        message = 'Expected minute should be %s, I got %s' % (
            expected_minute, SHAKE_GRID_CONVERTER.minute)
        self.assertEqual(SHAKE_GRID_CONVERTER.minute, expected_minute, message)

        expected_second = 49
        message = 'Expected second should be %s, I got %s' % (
            expected_second, SHAKE_GRID_CONVERTER.second)
        self.assertEqual(SHAKE_GRID_CONVERTER.second, expected_second, message)

    def test_parse_grid_xml(self):
        """Test parse_grid_xml works."""
        self.assertEquals(10, SHAKE_GRID_CONVERTER.day)
        self.assertEquals(5, SHAKE_GRID_CONVERTER.month)
        self.assertEquals(2014, SHAKE_GRID_CONVERTER.year)
        self.assertEquals(1, SHAKE_GRID_CONVERTER.hour)
        self.assertEquals(2, SHAKE_GRID_CONVERTER.minute)
        self.assertEquals(49, SHAKE_GRID_CONVERTER.second)
        self.assertEquals('GMT', SHAKE_GRID_CONVERTER.time_zone)
        self.assertEquals(-155.6317, SHAKE_GRID_CONVERTER.longitude)
        self.assertEquals(19.4212, SHAKE_GRID_CONVERTER.latitude)
        self.assertEquals(3.8, SHAKE_GRID_CONVERTER.depth)
        self.assertEquals(
            'ISLAND OF HAWAII, HAWAII', SHAKE_GRID_CONVERTER.location)
        self.assertEquals(-156.8817, SHAKE_GRID_CONVERTER.x_minimum)
        self.assertEquals(-154.3817, SHAKE_GRID_CONVERTER.x_maximum)
        self.assertEquals(18.24245, SHAKE_GRID_CONVERTER.y_minimum)
        self.assertEquals(20.59995, SHAKE_GRID_CONVERTER.y_maximum)

        grid_xml_data = SHAKE_GRID_CONVERTER.mmi_data
        self.assertEquals(21442, len(grid_xml_data))

    def test_grid_file_path(self):
        """Test grid_file_path works properly."""
        grid_path = SHAKE_GRID_CONVERTER.grid_file_path()
        expected_path = GRID_PATH
        message = 'Grid path should be %s, but I got %s' % (
            expected_path, grid_path)
        self.assertEqual(grid_path, expected_path, message)

    def test_mmi_to_delimited_text(self):
        """Test mmi_to_delimited_text works."""
        delimited_string = SHAKE_GRID_CONVERTER.mmi_to_delimited_text()
        self.assertEqual(435413, len(delimited_string))

    def test_mmi_to_delimited_file(self):
        """Test mmi_to_delimited_file works."""
        file_path = SHAKE_GRID_CONVERTER.mmi_to_delimited_file(
            force_flag=True)
        delimited_file = file(file_path)
        delimited_string = delimited_file.readlines()
        delimited_file.close()
        self.assertEqual(21443, len(delimited_string))

    def test_mmi_to_raster(self):
        """Check we can convert the shake event to a raster."""
        # Check the tif file
        raster_path = SHAKE_GRID_CONVERTER.mmi_to_raster(
            'title', 'source', force_flag=True)
        self.assertTrue(os.path.exists(raster_path))
        # Check the qml file
        expected_qml = raster_path.replace('tif', 'qml')
        self.assertTrue(os.path.exists(expected_qml))
        # Check the keywords file
        expected_keywords = raster_path.replace('tif', 'keywords')
        self.assertTrue(os.path.exists(expected_keywords))

    def test_mmi_to_shapefile(self):
        """Check we can convert the shake event to a shapefile."""
        # Check the shp file
        file_path = SHAKE_GRID_CONVERTER.mmi_to_shapefile(force_flag=True)
        self.assertTrue(os.path.exists(file_path))
        # Check the qml file
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        self.assertTrue(os.path.exists(expected_qml), message)

    def test_convert_grid_to_raster(self):
        """Test converting grid.xml to raster (tif file)"""
        grid_path = os.path.join(TESTDATA, 'grid.xml')
        grid_title = 'Earthquake'
        grid_source = 'USGS'
        output_raster = unique_filename(
            prefix='result_grid',
            suffix='.tif',
            dir=temp_dir('test'))
        result = convert_mmi_data(
            grid_path, grid_title, grid_source, output_raster)
        expected_result = output_raster.replace('.tif', '-nearest.tif')
        self.assertEqual(
            result, expected_result,
            'Result path not as expected')
        exists = os.path.exists(result)
        self.assertTrue(exists, 'File result : %s does not exist' % result)
        exists = os.path.exists(result[:-3] + 'keywords')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % result[:-3] + 'keywords')
        exists = os.path.exists(result[:-3] + 'qml')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % result[:-3] + 'qml')
    test_convert_grid_to_raster.slow = True


if __name__ == '__main__':
    suite = unittest.makeSuite(ConverterTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
