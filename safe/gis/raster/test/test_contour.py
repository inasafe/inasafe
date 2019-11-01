# coding=utf-8
"""Test Contour."""


import os

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    load_test_raster_layer, standard_data_path)
import unittest
from safe.gis.raster.contour import (
    create_smooth_contour, smooth_shakemap, shakemap_contour)
from safe.common.utilities import unique_filename

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestContour(unittest.TestCase):

    """Test Contour"""

    def test_contour(self):
        """Test create contour"""
        output_file_path = unique_filename(suffix='-contour.gpkg')
        # Load shake map layer
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-use_ascii.tif')
        create_smooth_contour(
            shakemap_layer,
            output_file_path=output_file_path
        )
        self.assertTrue(os.path.exists(output_file_path))
        ext = os.path.splitext(output_file_path)[1]
        metadata_path = output_file_path.replace(ext, '.xml')
        self.assertTrue(os.path.exists(metadata_path))
        self.assertTrue(metadata_path.endswith('.xml'))

    def test_smoothing(self):
        """Test smoothing method."""
        # Load shake map layer
        shakemap_layer = load_test_raster_layer(
            'hazard',
            'shake_data',
            '20131105060809',
            'output',
            'grid-use_ascii.tif')
        smoothed_shakemap_path = smooth_shakemap(shakemap_layer.source())
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
        contour_path = shakemap_contour(shakemap_layer_path)
        self.assertTrue(os.path.exists(contour_path))


if __name__ == '__main__':
    unittest.main()
