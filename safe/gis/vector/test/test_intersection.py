# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gis.vector.intersection import intersection

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
        """Test we can intersect two layers, like exposure and aggregation."""

        hazard = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')

        aggregation = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation.keywords = {
            'aggregation_keywords': {},
            'hazard_keywords': {},
            'inasafe_fields': {}
        }

        layer = intersection(hazard, aggregation)

        self.assertEqual(layer.featureCount(), 6)
        self.assertEqual(
            aggregation.fields().count() + hazard.fields().count(),
            layer.fields().count()
        )
