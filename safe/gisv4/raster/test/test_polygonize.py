# coding=utf-8
"""Tests for reclassify implementation."""
import unittest
from qgis.core import QgsVectorLayer, QgsFeatureRequest
from safe.gisv4.raster.polygonize import polygonize
from safe.test.utilities import standard_data_path, get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class PolygonizeTest(unittest.TestCase):
    """Tests for polygonizing a raster."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_polygonize(self):
        """Test if we can polygonize a raster."""

        raster_path = standard_data_path(
            'hazard', 'classified_flood_20_20.asc')

        output = polygonize(raster_path)
        print output

        layer = QgsVectorLayer(output, 'test layer', 'ogr')
        self.assertEqual(layer.featureCount(), 400)

        expression = '"DN" = \'%s\'' % 1
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 133)

        expression = '"dn" = \'%s\'' % 2
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 134)

        expression = '"dn" = \'%s\'' % 2
        request = QgsFeatureRequest().setFilterExpression(expression)
        self.assertEqual(sum(1 for _ in layer.getFeatures(request)), 134)
