# coding=utf-8
"""Test Shake Grid."""

import os
import unittest
import shutil

from qgis.core import QgsVectorLayer

from safe.definitions.hazard import hazard_earthquake
from safe.definitions.hazard_classifications import earthquake_mmi_scale
from safe.definitions.exposure import exposure_population

from safe.common.utilities import unique_filename, temp_dir
from safe.test.utilities import standard_data_path, get_qgis_app, load_layer
from safe.gui.tools.shake_grid.shake_grid import (
    ShakeGrid, convert_mmi_data, USE_ASCII, NEAREST_NEIGHBOUR, INVDIST)
from safe.utilities.metadata import read_iso19115_metadata
from safe.definitions.constants import NUMPY_SMOOTHING, INASAFE_TEST

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Parse the grid once and use it for all tests to fasten the tests
# Use temp directory to do the testing
SOURCE_PATH = standard_data_path(
    'hazard',
    'shake_data',
    '20131105060809',
    'output',
    'grid.xml')
GRID_PATH = os.path.join(temp_dir(__name__), 'grid.xml')
shutil.copyfile(SOURCE_PATH, GRID_PATH)

NORMAL_SHAKE_GRID = ShakeGrid(
    'Normal Shake Map',
    'Normal',
    GRID_PATH,
    output_dir=temp_dir(sub_dir='normal')
)

SMOOTHED_SHAKE_GRID = ShakeGrid(
    'Smoothed Shake Map',
    'Smoothed',
    GRID_PATH,
    output_dir=temp_dir(sub_dir='smoothed'),
    smoothing_method=NUMPY_SMOOTHING
)


class TestShakeGrid(unittest.TestCase):

    """Class to test ShakeGrid."""

    @classmethod
    def tearDownClass(cls):
        """Class method called after tests on this class have run."""
        shutil.rmtree(temp_dir(__name__))

    @staticmethod
    def check_feature_count(path, count):
        """Method to check the features number of a vector layer.

        :param path: Path to vector layer.
        :type path: str

        :param count: The base number to check against.
        :type count: int
        """
        # Needed for windows
        path = os.path.normcase(os.path.abspath(path))
        layer = QgsVectorLayer(path, 'Test Layer', 'ogr')
        feature_count = layer.featureCount()
        flag = feature_count == count
        message = ''
        if not flag:
            message = 'Expected %s features, got %s' % (count, feature_count)
        return flag, message

    def test_conversion(self):
        """Test conversion for getting the raster."""
        normal_shakemap_tif = NORMAL_SHAKE_GRID.mmi_to_raster()
        normal_contour_shp = NORMAL_SHAKE_GRID.mmi_to_contours()

        smoothed_shakemap_tif = SMOOTHED_SHAKE_GRID.mmi_to_raster()
        smoothed_contour_shp = SMOOTHED_SHAKE_GRID.mmi_to_contours()

    def test_extract_date_time(self):
        """Test extract_date_time giving the correct output."""
        # Test on SHAKE_GRID
        expected_year = 2013
        message = 'Expected year should be %s, I got %s' % (
            expected_year, SMOOTHED_SHAKE_GRID.year)
        self.assertEqual(SMOOTHED_SHAKE_GRID.year, expected_year, message)

        expected_month = 11
        message = 'Expected month should be %s, I got %s' % (
            expected_month, SMOOTHED_SHAKE_GRID.month)
        self.assertEqual(SMOOTHED_SHAKE_GRID.month, expected_month, message)

        expected_day = 5
        message = 'Expected day should be %s, I got %s' % (
            expected_day, SMOOTHED_SHAKE_GRID.day)
        self.assertEqual(SMOOTHED_SHAKE_GRID.day, expected_day, message)

        expected_hour = 6
        message = 'Expected hour should be %s, I got %s' % (
            expected_hour, SMOOTHED_SHAKE_GRID.hour)
        self.assertEqual(SMOOTHED_SHAKE_GRID.hour, expected_hour, message)

        expected_minute = 8
        message = 'Expected minute should be %s, I got %s' % (
            expected_minute, SMOOTHED_SHAKE_GRID.minute)
        self.assertEqual(SMOOTHED_SHAKE_GRID.minute, expected_minute, message)

        expected_second = 9
        message = 'Expected second should be %s, I got %s' % (
            expected_second, SMOOTHED_SHAKE_GRID.second)
        self.assertEqual(SMOOTHED_SHAKE_GRID.second, expected_second, message)

    def test_parse_grid_xml(self):
        """Test parse_grid_xml works."""
        self.assertEqual(5, SMOOTHED_SHAKE_GRID.day)
        self.assertEqual(11, SMOOTHED_SHAKE_GRID.month)
        self.assertEqual(2013, SMOOTHED_SHAKE_GRID.year)
        self.assertEqual(6, SMOOTHED_SHAKE_GRID.hour)
        self.assertEqual(8, SMOOTHED_SHAKE_GRID.minute)
        self.assertEqual(9, SMOOTHED_SHAKE_GRID.second)
        self.assertEqual('Asia/Jakarta', SMOOTHED_SHAKE_GRID.time_zone)
        self.assertEqual(140.62, SMOOTHED_SHAKE_GRID.longitude)
        self.assertEqual(-2.43, SMOOTHED_SHAKE_GRID.latitude)
        self.assertEqual(10.0, SMOOTHED_SHAKE_GRID.depth)
        self.assertEqual('Papua', SMOOTHED_SHAKE_GRID.location)
        self.assertEqual(139.37, SMOOTHED_SHAKE_GRID.x_minimum)
        self.assertEqual(141.87, SMOOTHED_SHAKE_GRID.x_maximum)
        self.assertEqual(-3.67875, SMOOTHED_SHAKE_GRID.y_minimum)
        self.assertEqual(-1.18125, SMOOTHED_SHAKE_GRID.y_maximum)

        grid_xml_data = SMOOTHED_SHAKE_GRID.mmi_data
        self.assertEqual(10201, len(grid_xml_data))

        # Check SHAKE_GRID.grid_bounding_box
        bounds = SMOOTHED_SHAKE_GRID.grid_bounding_box.toString()
        expected_result = (
            '139.3700000000000045,-3.6787500000000000 : '
            '141.8700000000000045,-1.1812499999999999')
        message = 'Got:\n%s\nExpected:\n%s\n' % (bounds, expected_result)
        self.assertEqual(bounds, expected_result, message)

    def test_grid_file_path(self):
        """Test grid_file_path works properly."""
        grid_path = SMOOTHED_SHAKE_GRID.grid_file_path()
        expected_path = GRID_PATH
        message = 'Grid path should be %s, but I got %s' % (
            expected_path, grid_path)
        self.assertEqual(grid_path, expected_path, message)

    def test_mmi_to_delimited_text(self):
        """Test mmi_to_delimited_text works."""
        delimited_string = SMOOTHED_SHAKE_GRID.mmi_to_delimited_text()
        # Add 1 for header
        number_of_line = len(SMOOTHED_SHAKE_GRID.mmi_data) + 1
        substring = (
            'lon,lat,mmi\n'
            '139.37,-1.1813,1.0\n'
            '139.395,-1.1813,1.0\n'
            '139.42,-1.1813,1.0\n'
            '139.445,-1.1813,1.0\n'
        )
        self.assertTrue(delimited_string.startswith(substring))
        self.assertEqual(delimited_string.count(','), number_of_line * 2)
        self.assertEqual(delimited_string.count('\n'), number_of_line)

    def test_mmi_to_delimited_file(self):
        """Test mmi_to_delimited_file works."""
        # Check CSV File
        file_path = SMOOTHED_SHAKE_GRID.mmi_to_delimited_file(
            force_flag=True)
        delimited_file = file(file_path)
        delimited_string = delimited_file.readlines()
        delimited_file.close()
        self.assertEqual(10202, len(delimited_string))

        # Check CSVT File
        csvt_file_path = file_path.replace('csv', 'csvt')
        csvt_file = file(csvt_file_path)
        csvt_string = csvt_file.readlines()
        csvt_file.close()
        self.assertEqual(1, len(csvt_string))

    def test_mmi_to_raster(self):
        """Check we can convert the shake event to a raster."""
        # Check the tif file
        raster_path = SMOOTHED_SHAKE_GRID.mmi_to_raster(force_flag=True)
        self.assertTrue(os.path.exists(raster_path))
        # Check the qml file
        expected_qml = raster_path.replace('tif', 'qml')
        self.assertTrue(os.path.exists(expected_qml))
        # Check the keywords file
        expected_keywords = raster_path.replace('tif', 'xml')
        self.assertTrue(os.path.exists(expected_keywords))
        # Check that extra_keywords exists
        keywords = read_iso19115_metadata(raster_path)
        self.assertIn('extra_keywords', list(keywords.keys()))

    def test_mmi_to_shapefile(self):
        """Check we can convert the shake event to a shapefile."""
        # Check the shp file
        file_path = SMOOTHED_SHAKE_GRID.mmi_to_shapefile(force_flag=True)
        self.assertTrue(os.path.exists(file_path))
        # Check the qml file
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        self.assertTrue(os.path.exists(expected_qml), message)

    # This test is failing on some QGIS docker image used for testing.
    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False), 'This test is failing in docker.')
    def test_event_to_contours(self):
        """Check we can extract contours from the event."""
        file_path = SMOOTHED_SHAKE_GRID.mmi_to_contours(
            force_flag=True, algorithm=INVDIST)
        self.assertTrue(self.check_feature_count(file_path, 16))
        self.assertTrue(os.path.exists(file_path))
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        self.assertTrue(os.path.exists(expected_qml), message)

        file_path = SMOOTHED_SHAKE_GRID.mmi_to_contours(
            force_flag=True, algorithm=NEAREST_NEIGHBOUR)
        self.assertTrue(self.check_feature_count(file_path, 132))
        file_path = SMOOTHED_SHAKE_GRID.mmi_to_contours(
            force_flag=True, algorithm='average')
        self.assertTrue(self.check_feature_count(file_path, 132))

    def test_convert_grid_to_raster(self):
        """Test converting grid.xml to raster (tif file)"""
        grid_title = 'Earthquake'
        grid_source = 'USGS'
        output_raster = unique_filename(
            prefix='result_grid',
            suffix='.tif',
            dir=temp_dir('test'))
        result = convert_mmi_data(
            GRID_PATH, grid_title, grid_source, output_path=output_raster,
            algorithm=NEAREST_NEIGHBOUR)
        expected_result = output_raster.replace(
            '.tif', '-%s.tif' % NEAREST_NEIGHBOUR)
        self.assertEqual(
            result, expected_result,
            'Result path not as expected')
        exists = os.path.exists(result)
        self.assertTrue(exists, 'File result : %s does not exist' % result)
        exists = os.path.exists(result[:-3] + 'xml')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % result[:-3] + 'xml')
        exists = os.path.exists(result[:-3] + 'qml')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % result[:-3] + 'qml')

    def test_convert_grid_to_raster_with_ascii(self):
        """Test converting grid.xml to raster (tif file)"""
        grid_title = 'Earthquake'
        grid_source = 'USGS'
        output_raster = unique_filename(
            prefix='result_grid',
            suffix='.tif',
            dir=temp_dir('test'))
        result = convert_mmi_data(
            GRID_PATH,
            grid_title,
            grid_source,
            algorithm=USE_ASCII,
            output_path=output_raster)
        expected_result = output_raster.replace('.tif', '-%s.tif' % USE_ASCII)
        self.assertEqual(
            result, expected_result,
            'Result path not as expected')
        exists = os.path.exists(result)
        self.assertTrue(exists, 'File result : %s does not exist' % result)
        exists = os.path.exists(result[:-3] + 'xml')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % result[:-3] + 'xml')
        exists = os.path.exists(result[:-3] + 'qml')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % result[:-3] + 'qml')
        tif_file = load_layer(result)[0]
        keywords = tif_file.keywords
        self.assertEqual(keywords['hazard'], hazard_earthquake['key'])
        population_classification = list(keywords['thresholds'][
            exposure_population['key']].keys())[0]
        self.assertEqual(
            population_classification, earthquake_mmi_scale['key'])

    def test_convert_grid_to_ascii(self):
        """Test converting grid.xml to raster (asc file)."""
        output_path = os.path.join(
                NORMAL_SHAKE_GRID.output_dir,
                '%s.asc' % NORMAL_SHAKE_GRID.output_basename)
        self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    suite = unittest.makeSuite(TestShakeGrid)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
