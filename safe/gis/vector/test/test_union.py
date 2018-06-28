# coding=utf-8

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
from safe.gis.vector.clean_geometry import clean_layer
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gis.vector.union import union
from safe.definitions.fields import hazard_class_field, hazard_value_field

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestUnionVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_union(self):
        """Test we can union two layers like hazard and aggregation (1)."""

        union_a = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        union_a.keywords['inasafe_fields'][hazard_class_field['key']] = (
            union_a.keywords['inasafe_fields'][hazard_value_field['key']])

        union_b = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        layer = union(union_a, union_b)

        self.assertEqual(layer.featureCount(), 14)
        self.assertEqual(
            union_a.fields().count() + union_b.fields().count(),
            layer.fields().count()
        )

    @unittest.expectedFailure
    def test_union_error(self):
        """Test we can union two layers like hazard and aggregation (2)."""

        union_a = clean_layer(load_test_vector_layer(
            'gisv4', 'hazard', 'union_check_hazard.geojson'))
        union_a.keywords['inasafe_fields'][hazard_class_field['key']] = (
            union_a.keywords['inasafe_fields'][hazard_value_field['key']])

        union_b = clean_layer(load_test_vector_layer(
            'gisv4', 'aggregation', 'union_check_aggregation.geojson'))

        layer = union(union_a, union_b)

        self.assertEqual(layer.featureCount(), 11)
        self.assertEqual(
            union_a.fields().count() + union_b.fields().count(),
            layer.fields().count()
        )
