# coding=utf-8
"""Test Contour."""

import hashlib
from safe.test.utilities import (
    load_test_raster_layer, qgis_app, standard_data_path)
import unittest
from safe.gis.raster.contour import (
    create_contour, smooth_shake_map, shakemap_contour)
from safe.common.utilities import unique_filename

APP, IFACE = qgis_app()


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestContour(unittest.TestCase):

    """Test Contour"""

    @unittest.skip('Fix me first')
    def test_contour(self):
        """Test create contour"""
        output_file_path = unique_filename(suffix='-contour.geojson')
        # Load shake map layer
        shake_map_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20150918201057',
            'output',
            'grid-nearest.tif')
        print shake_map_layer.source()
        print output_file_path
        create_contour(
            shake_map_layer,
            output_file_path=output_file_path
        )

    @unittest.skip('Fix me first')
    def test_smoothing(self):
        """Test smoothing method."""
        # Load shake map layer
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-nearest.tif')
        expected_shakemap_path = shakemap_layer.source()
        expected_shakemap_path = expected_shakemap_path.replace(
            'grid-nearest.tif', 'grid-smoothing-nearest.tif')

        print shakemap_layer.source()
        print expected_shakemap_path

        smoothed_shakemap_path = smooth_shake_map(shakemap_layer.source())

        print smoothed_shakemap_path

        hash_smoothed = hashlib.md5(
            open(smoothed_shakemap_path, 'rb').read()).hexdigest()
        expected_hash = hashlib.md5(
            open(expected_shakemap_path, 'rb').read()).hexdigest()
        self.assertEqual(hash_smoothed, expected_hash)

    @unittest.skip('Fix me first')
    def test_contour_shakemap(self):
        """Test for contour creation."""
        # Original
        normal_shakemap_layer_path = standard_data_path(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-nearest.tif')
        normal_contour_path = shakemap_contour(normal_shakemap_layer_path)
        print 'Normal: ', normal_contour_path

        # Smoothed
        smoothed_shakemap_layer_path = standard_data_path(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-smoothing-nearest.tif')
        smoothed_contour_path = shakemap_contour(smoothed_shakemap_layer_path)
        print 'Smoothed', smoothed_contour_path

        # Together
        smoothed_contour_path_2 = create_contour(normal_shakemap_layer_path)
        print 'Smoothed (2)', smoothed_contour_path_2

        hash_smoothed = hashlib.md5(
            open(smoothed_contour_path, 'rb').read()).hexdigest()
        hash_smoothed_2 = hashlib.md5(
            open(smoothed_contour_path_2, 'rb').read()).hexdigest()
        self.assertEqual(hash_smoothed, hash_smoothed_2)


if __name__ == '__main__':
    unittest.main()
