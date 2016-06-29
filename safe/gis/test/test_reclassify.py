# coding=utf-8
"""Tests for reclassify implementation."""
import unittest
from collections import OrderedDict

from qgis.core import QgsVectorLayer, QgsFeatureRequest

from safe.gis.reclassify_gdal import reclassify_polygonize
from safe.test.utilities import standard_data_path, get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ReclassifyTest(unittest.TestCase):
    """Tests for reclassify a raster."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reclassify_polygonize(self):
        """Test if we can reclassify a raster according to some thresholds."""

        raster_path = standard_data_path(
            'hazard', 'continuous_flood_20_20.asc')

        ranges = OrderedDict()

        # value <= 0.2
        ranges[1] = [None, 0.2]
        # 0.2 < value <= 1
        ranges[2] = [0.2, 1]
        # 1 < value <= 1.3 and gap in output classes
        ranges[10] = [1, 1.3]
        # value > 1.3
        ranges[11] = [1.3, None]

        output = reclassify_polygonize(raster_path, ranges)

        layer = QgsVectorLayer(output, 'test layer', 'ogr')
        self.assertEqual(layer.featureCount(), 61)

        expression = '"DN" = \'%s\'' % 1
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)

        expression = '"DN" = \'%s\'' % 2
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 1)

        expression = '"DN" = \'%s\'' % 10
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)

        expression = '"DN" = \'%s\'' % 11
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)
