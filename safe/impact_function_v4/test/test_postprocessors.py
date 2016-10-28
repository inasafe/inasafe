# coding=utf-8
"""Test for Impact Function."""

import unittest

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitionsv4.fields import (
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    feature_value_field,
    size_field
)
from safe.definitionsv4.post_processors import (
    post_processor_gender,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly,
    post_processor_size_rate,
    post_processor_size
)
from safe.test.utilities import load_test_vector_layer
from safe.impact_function_v4.postprocessors import (
    evaluate_formula,
    run_single_post_processor,
    enough_input
)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPostProcessors(unittest.TestCase):
    """Test Post Processors."""

    def test_gender_post_processor(self):
        """Test gender post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_gender)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(women_count_field['field_name'], impact_fields)

    def test_youth_post_processor(self):
        """Test youth post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_youth)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(youth_count_field['field_name'], impact_fields)

    def test_adult_post_processor(self):
        """Test adult post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_adult)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(adult_count_field['field_name'], impact_fields)

    def test_elderly_post_processor(self):
        """Test elderly post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_elderly)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(elderly_count_field['field_name'], impact_fields)

    def test_size_post_processor(self):
        """Test size  post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_size)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(size_field['field_name'], impact_fields)

    def test_size_rate_post_processor(self):
        """Test size rate post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_size_rate)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(feature_value_field['field_name'], impact_fields)
        self.assertNotIn('size', impact_fields)

    def test_enough_input(self):
        """Test to check the post processor input checker."""

        class FakeMonkeyPatch(object):
            pass

        # We need to monkey patch some keywords to the impact layer.
        layer = FakeMonkeyPatch()

        # Gender postprocessor with female ratio missing.
        layer.keywords = {
            'inasafe_fields': {
                'population_count_field': 'population'
            }
        }
        # noinspection PyTypeChecker
        result = enough_input(layer, post_processor_gender['input'])
        self.assertFalse(result[0])

        # Gender postprocessor with female ratio missing.
        layer.keywords = {
            'inasafe_fields': {
                'population_count_field': 'population',
                'female_ratio_field': 'female_r'
            }
        }
        # noinspection PyTypeChecker
        result = enough_input(layer, post_processor_gender['input'])
        self.assertTrue(result[0])

    def test_evaluate_formula(self):
        """Test for evaluating formula."""
        formula = 'population * gender_ratio'
        variables = {
            'population': 100,
            'gender_ratio': 0.45
        }
        self.assertEquals(45, evaluate_formula(formula, variables))


if __name__ == '__main__':
    unittest.main()
