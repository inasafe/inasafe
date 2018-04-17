# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

from safe.gis.vector.clip import clip

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestClipVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clip_vector(self):
        """Test we can clip two layers, like buildings and aggregation."""

        aggregation = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        exposure = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')

        layer = clip(exposure, aggregation)
        self.assertEqual(layer.featureCount(), 9)

        # Add test about keywords
        # todo
