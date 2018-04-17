# coding=utf-8
"""Test Reclassify Raster."""

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

from qgis.core import QgsRasterBandStats

from safe.definitions.processing_steps import reclassify_raster_steps
from safe.gis.raster.reclassify import reclassify
from safe.definitions.exposure import exposure_structure
from safe.definitions.hazard_classifications import generic_hazard_classes

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestReclassifyRaster(unittest.TestCase):

    """Test Reclassify Raster."""

    maxDiff = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reclassify_raster(self):
        """Test we can reclassify a raster layer."""
        layer = load_test_raster_layer('hazard', 'continuous_flood_20_20.asc')

        classes = {
            'low': [None, 0.2],  # value <= 0.2
            'medium': [0.2, 1],  # 0.2 < value <= 1
            'high': [1, None],  # 1 < value
        }

        ranges = {
            exposure_structure['key']: {
                generic_hazard_classes['key']: {
                    'active': True,
                    'classes': classes
                }
            }
        }

        layer.keywords['thresholds'] = ranges

        expected_keywords = layer.keywords.copy()
        title = reclassify_raster_steps['output_layer_name'] % (
            layer.keywords['layer_purpose'])
        expected_keywords['layer_mode'] = 'classified'
        expected_keywords['value_map'] = {
            'high': [3],
            'low': [1],
            'medium': [2]
        }
        expected_keywords['title'] = title
        expected_keywords['classification'] = generic_hazard_classes['key']
        expected_keywords['thresholds'] = classes

        reclassified = reclassify(layer, exposure_structure['key'])

        self.assertDictEqual(reclassified.keywords, expected_keywords)

        stats = reclassified.dataProvider().bandStatistics(
            1, QgsRasterBandStats.Min | QgsRasterBandStats.Max)
        self.assertEqual(stats.minimumValue, 1.0)
        self.assertEqual(stats.maximumValue, 3.0)
