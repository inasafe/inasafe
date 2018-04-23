# coding=utf-8

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from qgis.core import QgsFeatureRequest

from safe.definitions.fields import hazard_class_field
from safe.gis.vector.assign_highest_value import assign_highest_value

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
            'gisv4', 'exposure', 'buildings.geojson', clone_to_memory=True)

        aggregate_hazard = load_test_vector_layer(
            'gisv4', 'intermediate', 'aggregate_classified_hazard.geojson')

        # Monkey patching classification. We should remove this line
        # when we will have aggregate_hazard definitions.
        aggregate_hazard.keywords['classification'] = 'generic_hazard_classes'

        aggregate_hazard.keywords['aggregation_keywords'] = {}
        aggregate_hazard.keywords['hazard_keywords'] = {}

        count = exposure.fields().count()
        layer = assign_highest_value(exposure, aggregate_hazard)

        self.assertEqual(layer.featureCount(), 12)
        self.assertEqual(
            count + aggregate_hazard.fields().count(), layer.fields().count())

        expected_count = {
            'high': 4,
            'medium': 2,
            '': 6
        }

        inasafe_fields = layer.keywords['inasafe_fields']
        expected_field = inasafe_fields[hazard_class_field['key']]

        for value, count in list(expected_count.items()):
            if value:
                expression = '"%s" = \'%s\'' % (expected_field, value)
            else:
                expression = '"%s" is NULL' % expected_field
            request = QgsFeatureRequest().setFilterExpression(expression)
            self.assertEqual(
                sum(1 for _ in layer.getFeatures(request)), count)
