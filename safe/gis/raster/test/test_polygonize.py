# coding=utf-8

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from qgis.core import QgsFeatureRequest

from safe.gis.raster.polygonize import polygonize
from safe.definitions.layer_geometry import (
    layer_geometry, layer_geometry_polygon)
from safe.definitions.processing_steps import polygonize_steps
from safe.definitions.fields import hazard_value_field

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPolygonizeRaster(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_polygonize_raster(self):
        """Test we can polygonize a raster layer."""
        layer = load_test_raster_layer('hazard', 'classified_flood_20_20.asc')

        expected_keywords = layer.keywords.copy()
        title = polygonize_steps['output_layer_name'] % (
            layer.keywords['layer_purpose'])
        expected_keywords[
            layer_geometry['key']] = layer_geometry_polygon['key']
        expected_keywords['title'] = title

        expected_keywords['inasafe_fields'] = {
            hazard_value_field['key']: hazard_value_field['field_name'][0:10]}

        polygonized = polygonize(layer)

        self.assertDictEqual(polygonized.keywords, expected_keywords)

        self.assertEqual(polygonized.featureCount(), 400)

        expected_count = {
            '1': 133,
            '2': 134,
            '3': 133,
        }

        inasafe_fields = polygonized.keywords.get('inasafe_fields')
        field_name = inasafe_fields.get(hazard_value_field['key'])

        for value, count in expected_count.items():
            expression = '"%s" = \'%s\'' % (field_name, value)
            request = QgsFeatureRequest().setFilterExpression(expression)
            self.assertEqual(
                sum(1 for _ in polygonized.getFeatures(request)), count)
