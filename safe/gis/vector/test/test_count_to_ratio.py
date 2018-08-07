# coding=utf-8

"""Test file for transform counts to ratios."""

import unittest

from safe.test.utilities import qgis_iface, load_test_vector_layer
from safe.definitions.fields import (
    female_count_field, female_ratio_field, size_field, population_count_field)

from safe.gis.vector.from_counts_to_ratios import from_counts_to_ratios
from safe.gis.vector.prepare_vector_layer import prepare_vector_layer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

iface = qgis_iface()


class TestRecomputeCounts(unittest.TestCase):

    """Test class."""

    def test_recompute_counts(self):
        """Test we can recompute counts in a layer."""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson',
            clone=True)

        self.assertIn(
            female_count_field['key'], layer.keywords['inasafe_fields'])

        layer = prepare_vector_layer(layer)
        layer = from_counts_to_ratios(layer)

        self.assertIn(
            female_count_field['key'], layer.keywords['inasafe_fields'])
        self.assertIn(
            female_ratio_field['key'], layer.keywords['inasafe_fields'])

        # Check that each feature has correct ratio
        for feature in layer.getFeatures():
            female_count = feature[female_count_field['field_name']]
            population_count = feature[population_count_field['field_name']]
            manual_ratio = female_count / float(population_count)

            computing_ratio = feature[female_ratio_field['field_name']]
            diff = abs(manual_ratio - computing_ratio)

            message = 'The ratio difference is too big, diff = %s' % diff
            self.assertTrue(diff < 10 ** -2, message)
