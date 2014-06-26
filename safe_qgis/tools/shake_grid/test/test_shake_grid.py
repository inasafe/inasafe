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
import shutil

import ogr

from safe.common.utilities import unique_filename, temp_dir
from safe.common.testing import get_qgis_app, TESTDATA
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.tools.shake_grid.shake_grid import (
    ShakeGrid,
    convert_mmi_data)

# Parse the grid once and use it for all tests to fasten the tests
# Use temp directory to do the testing
SOURCE_PATH = os.path.join(TESTDATA, 'grid.xml')
GRID_PATH = os.path.join(temp_dir(__name__), 'grid.xml')
shutil.copyfile(SOURCE_PATH, GRID_PATH)

SHAKE_GRID = ShakeGrid('Test Title', 'Test Source', GRID_PATH)


class ShakeGridTest(unittest.TestCase):
    """Class to test ShakeGrid."""

    @classmethod
    def tearDownClass(cls):
        """Class method called after tests on this class have run."""
        shutil.rmtree(temp_dir(__name__))

    def check_feature_count(self, path, count):
        """Method to check the features number of a vector layer.

        :param path: Path to vector layer.
        :type path: str

        :param count: The base number to check against.
        :type count: int
        """
        data_source = ogr.Open(path)
        base_name = os.path.splitext(os.path.basename(path))[0]
        # do a little query to make sure we got some results...
        sql_statement = 'select * from \'%s\' order by MMI asc' % base_name
        #print sql_statement
        layer = data_source.ExecuteSQL(sql_statement)
        feature_count = layer.GetFeatureCount()
        flag = feature_count == count
        message = ''
        if not flag:
            message = 'Expected %s features, got %s' % (count, feature_count)
        data_source.ReleaseResultSet(layer)
        data_source.Destroy()
        return flag, message

    def test_extract_date_time(self):
        """Test extract_date_time giving the correct output."""
        # Test on SHAKE_GRID
        expected_year = 2014
        message = 'Expected year should be %s, I got %s' % (
            expected_year, SHAKE_GRID.year)
        self.assertEqual(SHAKE_GRID.year, expected_year, message)

        expected_month = 1
        message = 'Expected month should be %s, I got %s' % (
            expected_month, SHAKE_GRID.month)
        self.assertEqual(SHAKE_GRID.month, expected_month, message)

        expected_day = 29
        message = 'Expected day should be %s, I got %s' % (
            expected_day, SHAKE_GRID.day)
        self.assertEqual(SHAKE_GRID.day, expected_day, message)

        expected_hour = 1
        message = 'Expected hour should be %s, I got %s' % (
            expected_hour, SHAKE_GRID.hour)
        self.assertEqual(SHAKE_GRID.hour, expected_hour, message)

        expected_minute = 39
        message = 'Expected minute should be %s, I got %s' % (
            expected_minute, SHAKE_GRID.minute)
        self.assertEqual(SHAKE_GRID.minute, expected_minute, message)

        expected_second = 0
        message = 'Expected second should be %s, I got %s' % (
            expected_second, SHAKE_GRID.second)
        self.assertEqual(SHAKE_GRID.second, expected_second, message)

    def test_parse_grid_xml(self):
        """Test parse_grid_xml works."""
        self.assertEquals(29, SHAKE_GRID.day)
        self.assertEquals(1, SHAKE_GRID.month)
        self.assertEquals(2014, SHAKE_GRID.year)
        self.assertEquals(1, SHAKE_GRID.hour)
        self.assertEquals(39, SHAKE_GRID.minute)
        self.assertEquals(0, SHAKE_GRID.second)
        self.assertEquals('UTC', SHAKE_GRID.time_zone)
        self.assertEquals(-114.1056, SHAKE_GRID.longitude)
        self.assertEquals(37.3411, SHAKE_GRID.latitude)
        self.assertEquals(4.9954, SHAKE_GRID.depth)
        self.assertEquals('29.3 miles SE of Caliente', SHAKE_GRID.location)
        self.assertEquals(-115.1056, SHAKE_GRID.x_minimum)
        self.assertEquals(-113.1056, SHAKE_GRID.x_maximum)
        self.assertEquals(36.5411, SHAKE_GRID.y_minimum)
        self.assertEquals(38.1411, SHAKE_GRID.y_maximum)

        grid_xml_data = SHAKE_GRID.mmi_data
        self.assertEquals(11737, len(grid_xml_data))

        # Check SHAKE_GRID.grid_bounding_box
        bounds = SHAKE_GRID.grid_bounding_box.toString()
        expected_result = (
            '-115.1055999999999955,36.5411000000000001 : '
            '-113.1055999999999955,38.1411000000000016')
        message = 'Got:\n%s\nExpected:\n%s\n' % (bounds, expected_result)
        self.assertEqual(bounds, expected_result, message)

    def test_grid_file_path(self):
        """Test grid_file_path works properly."""
        grid_path = SHAKE_GRID.grid_file_path()
        expected_path = GRID_PATH
        message = 'Grid path should be %s, but I got %s' % (
            expected_path, grid_path)
        self.assertEqual(grid_path, expected_path, message)

    def test_mmi_to_delimited_text(self):
        """Test mmi_to_delimited_text works."""
        delimited_string = SHAKE_GRID.mmi_to_delimited_text()
        self.assertEqual(190842, len(delimited_string))

    def test_mmi_to_delimited_file(self):
        """Test mmi_to_delimited_file works."""
        # Check CSV File
        file_path = SHAKE_GRID.mmi_to_delimited_file(
            force_flag=True)
        delimited_file = file(file_path)
        delimited_string = delimited_file.readlines()
        delimited_file.close()
        self.assertEqual(11738, len(delimited_string))

        # Check CSVT File
        csvt_file_path = file_path.replace('csv', 'csvt')
        csvt_file = file(csvt_file_path)
        csvt_string = csvt_file.readlines()
        csvt_file.close()
        self.assertEqual(1, len(csvt_string))

    def test_mmi_to_raster(self):
        """Check we can convert the shake event to a raster."""
        # Check the tif file
        raster_path = SHAKE_GRID.mmi_to_raster(force_flag=True)
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
        file_path = SHAKE_GRID.mmi_to_shapefile(force_flag=True)
        self.assertTrue(os.path.exists(file_path))
        # Check the qml file
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        self.assertTrue(os.path.exists(expected_qml), message)

    def test_event_to_contours(self):
        """Check we can extract contours from the event"""
        file_path = SHAKE_GRID.mmi_to_contours(
            force_flag=True, algorithm='invdist')
        self.assertTrue(self.check_feature_count(file_path, 16))
        self.assertTrue(os.path.exists(file_path))
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        self.assertTrue(os.path.exists(expected_qml), message)

        file_path = SHAKE_GRID.mmi_to_contours(
            force_flag=True, algorithm='nearest')
        self.assertTrue(self.check_feature_count(file_path, 132))
        file_path = SHAKE_GRID.mmi_to_contours(
            force_flag=True, algorithm='average')
        self.assertTrue(self.check_feature_count(file_path, 132))

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
    suite = unittest.makeSuite(ShakeGridTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
