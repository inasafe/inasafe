# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsFeatureRequest

from safe.definitionsv4.fields import hazard_class_field
from safe.gisv4.vector.assign_highest_value import assign_highest_value

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAssignHighestValueVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_assign_highest_value_vector(self):
        """Test we can assign the highest value to a feature."""

        exposure = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')

        aggregate_hazard = load_test_vector_layer(
            'gisv4', 'intermediate', 'aggregate_classified_hazard.geojson')

        # Monkey patching classification. We should remove this line
        # when we will have aggregate_hazard definitions.
        aggregate_hazard.keywords['classification'] = 'generic_hazard_classes'

        layer = assign_highest_value(exposure, aggregate_hazard)

        self.assertEqual(layer.featureCount(), 5)
        self.assertEqual(
            exposure.fields().count() + aggregate_hazard.fields().count(),
            layer.fields().count()
        )

        expected_count = {
            'high': 4,
            'medium': 1,
        }

        inasafe_fields = layer.keywords['inasafe_fields']
        expected_field = inasafe_fields[hazard_class_field['key']]

        for value, count in expected_count.iteritems():
            expression = '"%s" = \'%s\'' % (expected_field, value)
            request = QgsFeatureRequest().setFilterExpression(expression)
            self.assertEqual(
                sum(1 for _ in layer.getFeatures(request)), count)
