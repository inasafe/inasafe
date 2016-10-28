# coding=utf-8

import unittest
from collections import OrderedDict

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QGis
from safe.gisv4.vector.buffering import buffering
from safe.definitionsv4.fields import hazard_class_field

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestBuffering(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_buffer_points(self):
        """Test we can buffer points."""
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
        result = buffering(
            layer=layer,
            radii=radii)

        self.assertDictEqual(result.keywords, expected_keywords)
        self.assertEqual(result.geometryType(), QGis.Polygon)
        expected_feature_count = layer.featureCount() * len(radii)
        self.assertEqual(result.featureCount(), expected_feature_count)

        # We can check the new field added about the hazard class name.
        expected_fields_count = layer.fields().count() + 1

        self.assertEqual(result.fields().count(), expected_fields_count)

        # Check if the field name is correct.
        self.assertEqual(
            result.fields().at(expected_fields_count - 1).name(),
            expected_name_field)
