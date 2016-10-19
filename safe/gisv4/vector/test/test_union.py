# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gisv4.vector.union import union

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
        """Test we can union two layers like hazard and aggregation."""

        union_a = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        union_b = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')

        layer = union(union_a, union_b)

        self.assertEqual(layer.featureCount(), 14)
        self.assertEqual(
            union_a.fields().count() + union_b.fields().count(),
            layer.fields().count()
        )

        from safe.test.debug_helper import save_layer_to_file
        print save_layer_to_file(layer)

        # Add test about keywords
        # todo
