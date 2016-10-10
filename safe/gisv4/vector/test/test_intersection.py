# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gisv4.vector.intersection import intersection

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestIntersectionVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_intersection_mask_vector(self):
        """Test we can intersect two layers, like hazard and aggregation."""

        aggregation = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        hazard = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')

        layer = intersection(hazard, aggregation)

        self.assertEqual(layer.featureCount(), 8)
        self.assertEqual(
            aggregation.fields().count() + hazard.fields().count(),
            layer.fields().count()
        )

        from safe.test.debug_helper import save_layer_to_file
        print save_layer_to_file(layer)

        # Add test about keywords
        # todo
