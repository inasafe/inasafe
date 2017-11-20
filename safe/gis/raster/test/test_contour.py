# coding=utf-8
"""Test Contour."""

import os
import hashlib
from safe.test.utilities import load_test_raster_layer, qgis_app
import unittest
from safe.gis.raster.contour import (
    create_contour, smooth_shake_map, shakemap_contour)
from safe.common.utilities import temp_dir, unique_filename

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
        # shake_map_layer = load_test_raster_layer(
        #     '/Users/ismailsunni/Downloads/')
        print shake_map_layer.source()
        print output_file_path
        create_contour(
            shake_map_layer,
            output_file_path=output_file_path
        )

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

        smoothed_shakemap_path =  smooth_shake_map(shakemap_layer)

        print smoothed_shakemap_path

        hash_smoothed = hashlib.md5(
            open(smoothed_shakemap_path, 'rb').read()).hexdigest()
        expected_hash = hashlib.md5(
            open(expected_shakemap_path, 'rb').read()).hexdigest()
        self.assertEqual(hash_smoothed, expected_hash)

    def test_contour_shakemap(self):
        """Test for contour creation."""
        # Original
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-nearest.tif')
        contour_path = shakemap_contour(shakemap_layer, active_band=1)
        print contour_path

        # Smoothed
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-smoothing-nearest.tif')
        contour_path = shakemap_contour(shakemap_layer, active_band=1)
        print contour_path


if __name__ == '__main__':
    unittest.main()
