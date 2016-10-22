# coding=utf-8
import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsRasterBandStats
from collections import OrderedDict

from safe.gisv4.raster.reclassify import reclassify

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestReclassifyRaster(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reclassify_raster(self):
        """Test we can reclassify a raster layer."""
        layer = load_test_raster_layer('hazard', 'continuous_flood_20_20.asc')

        ranges = OrderedDict()
        # value <= 0.2
        ranges[1] = [None, 0.2]
        # 0.2 < value <= 1
        ranges[2] = [0.2, 1]
        # 1 < value <= 1.3 and gap in output classes
        ranges[10] = [1, 1.3]
        # value > 1.3
        ranges[11] = [1.3, None]

        expected_keywords = layer.keywords.copy()
        expected_keywords['layer_mode'] = 'classified'
        expected_keywords['value_map'] = {'dry': [1], 'wet': [2]}

        reclassified = reclassify(layer, ranges)

        self.assertEqual(reclassified.name(), 'reclassified')
        self.assertDictEqual(reclassified.keywords, expected_keywords)

        stats = reclassified.dataProvider().bandStatistics(
            1, QgsRasterBandStats.Min | QgsRasterBandStats.Max)
        self.assertEqual(stats.minimumValue, 1.0)
        self.assertEqual(stats.maximumValue, 11.0)
