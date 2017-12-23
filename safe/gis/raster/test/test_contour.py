# coding=utf-8
"""Test Contour."""

import os
from safe.test.utilities import (
    load_test_raster_layer, standard_data_path)
from safe.test.qgis_app import qgis_app
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

    def test_contour(self):
        """Test create contour"""
        output_file_path = unique_filename(suffix='-contour.geojson')
        # Load shake map layer
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-use_ascii.tif')
        print output_file_path
        create_contour(
            shakemap_layer.source(),
            output_file_path=output_file_path
        )
        self.assertTrue(os.path.exists(output_file_path))

    def test_smoothing(self):
        """Test smoothing method."""
        # Load shake map layer
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-use_ascii.tif')
        smoothed_shakemap_path = smooth_shake_map(shakemap_layer.source())
        self.assertTrue(os.path.exists(smoothed_shakemap_path))

    def test_contour_shakemap(self):
        """Test for contour creation (with smoothing)."""
        # Original
        shakemap_layer_path = standard_data_path(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-use_ascii.tif')
        normal_contour_path = shakemap_contour(shakemap_layer_path)
        self.assertTrue(os.path.exists(normal_contour_path))


if __name__ == '__main__':
    unittest.main()
