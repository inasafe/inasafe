# coding=utf-8
"""Tests for reclassify implementation."""
import unittest
from collections import OrderedDict

from qgis.core import QgsVectorLayer, QgsFeatureRequest

from safe.gis.reclassify_gdal import (
    reclassify_polygonize, _classes_to_string)
from safe.test.utilities import test_data_path, get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ReclassifyTest(unittest.TestCase):
    """Tests for reclassify a raster."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_classes(self):
        """Test we can create classes correctly."""

        ranges = OrderedDict()
        ranges[0] = [None, 0]
        ranges[1] = [0.0, 0.0]
        ranges[2] = [0.0, 1]
        ranges[4] = [1, 1]
        ranges[6] = [2, None]

        output_classes, input_classes = _classes_to_string(ranges)
        self.assertEqual(output_classes, [0, 1, 2, 4, 6])
        self.assertEqual(input_classes, ['<0', '==0.0', '<=1', '==1', '>2'])

    def test_reclassify_polygonize(self):
        """Test if we can reclassify a raster according to some thresholds."""

        raster_path = test_data_path('hazard', 'continuous_flood_20_20.asc')

        ranges = OrderedDict()

        # value < 0.2
        ranges[1] = [None, 0.2]
        # value == 0.2
        ranges[2] = [0.2, 0.2]
        # 0.2 < value <= 1
        ranges[3] = [0.2, 1]
        # 1 < value <= 1.3 and gap in output classes
        ranges[10] = [1, 1.3]
        # no data for 1.3 < value <= 1.8
        # 1.6 < value <= 1.9
        ranges[11] = [1.8, 1.8]
        # no data for 1.8 < value

        output = reclassify_polygonize(raster_path, ranges)

        layer = QgsVectorLayer(output, 'test layer', 'ogr')
        self.assertEqual(layer.featureCount(), 121)

        request = QgsFeatureRequest().setFilterExpression('"DN" = \'%s\'' % 0)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 40)

        request = QgsFeatureRequest().setFilterExpression('"DN" = \'%s\'' % 1)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)

        request = QgsFeatureRequest().setFilterExpression('"DN" = \'%s\'' % 2)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)

        request = QgsFeatureRequest().setFilterExpression('"DN" = \'%s\'' % 3)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 1)

        request = QgsFeatureRequest().setFilterExpression('"DN" = \'%s\'' % 10)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)

        request = QgsFeatureRequest().setFilterExpression('"DN" = \'%s\'' % 11)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 20)
