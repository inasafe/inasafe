# coding=utf-8

import unittest
from collections import OrderedDict

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from qgis.core import QgsWkbTypes
from safe.gis.vector.multi_buffering import multi_buffering
from safe.definitions.fields import hazard_class_field, buffer_distance_field

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestMultiBuffering(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multi_buffer_points(self):
        """Test we can multi buffer points such as volcano points."""
        radii = OrderedDict()
        radii[500] = 'high'
        radii[1000] = 'medium'
        radii[2000] = 'low'

        # Let's add a vector layer.
        layer = load_test_vector_layer('hazard', 'volcano_point.geojson')
        keywords = layer.keywords
        self.assertEqual(layer.keywords['layer_geometry'], 'point')

        expected_keywords = keywords.copy()
        expected_keywords['layer_geometry'] = 'polygon'
        expected_name_field = hazard_class_field['field_name']
        expected_keywords['inasafe_fields'][hazard_class_field['key']] = (
            expected_name_field)
        result = multi_buffering(
            layer=layer,
            radii=radii)

        self.assertDictEqual(result.keywords, expected_keywords)
        self.assertEqual(result.geometryType(), QgsWkbTypes.PolygonGeometry)
        expected_feature_count = layer.featureCount() * len(radii)
        self.assertEqual(result.featureCount(), expected_feature_count)

        # We can check the new fields added about the hazard class name
        # and the buffer distances.
        expected_fields_count = layer.fields().count() + 2

        self.assertEqual(result.fields().count(), expected_fields_count)

        # Check if the field name is correct.
        expected_fields_name = [
            hazard_class_field['field_name'],
            buffer_distance_field['field_name']]

        actual_field_names = [field.name() for field in result.pendingFields()]
        new_field_names = actual_field_names[-2:]

        self.assertEqual(expected_fields_name, new_field_names)
