# coding=utf-8
"""Test Contour."""

import os
from safe.test.utilities import load_test_raster_layer, qgis_app
import unittest
from safe.gis.raster.contour import create_contour
from safe.common.utilities import temp_dir, unique_filename

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


if __name__ == '__main__':
    unittest.main()
