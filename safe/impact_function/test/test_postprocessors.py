# coding=utf-8
"""Test for Post Processors."""


import unittest

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitions.exposure import exposure_population
from safe.definitions.hazard import hazard_generic
from safe.definitions.hazard_classifications import generic_hazard_classes
from safe.definitions.fields import (
    male_displaced_count_field,
    female_displaced_count_field,
    youth_displaced_count_field,
    adult_displaced_count_field,
    elderly_displaced_count_field,
    feature_value_field,
    size_field,
    affected_field,
    exposure_count_field,
    displaced_field,
    hygiene_packs_count_field,
    additional_rice_count_field,
    productivity_field,
    production_cost_field,
    production_value_field,
    productivity_rate_field,
    production_cost_rate_field,
    production_value_rate_field,
)
from safe.processors import (
    post_processor_size_rate,
    post_processor_size,
    post_processor_affected,
    field_input_type,
    post_processor_additional_rice)
from safe.processors import (
    dynamic_field_input_type,
    needs_profile_input_type)
from safe.processors.population_post_processors import (
    post_processor_male,
    post_processor_female,
    post_processor_hygiene_packs,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly)
from safe.processors.productivity_post_processors import (
    post_processor_productivity,
    post_processor_production_cost,
    post_processor_production_value
)
from safe.test.utilities import load_test_vector_layer
from safe.impact_function.postprocessors import (
    run_single_post_processor,
    evaluate_formula,
    enough_input)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPostProcessors(unittest.TestCase):

    """Test Post Processors."""

    class FakeMonkeyPatch():

        """Patch class for testings."""

        pass

    def test_gender_post_processor(self):
        """Test gender post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_male)
        self.assertTrue(result, message)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_female)
        self.assertTrue(result, message)

        # Check if new fields were added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(
            female_displaced_count_field['field_name'], impact_fields)
        self.assertIn(
            male_displaced_count_field['field_name'], impact_fields)

    def test_youth_post_processor(self):
        """Test youth post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_youth)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(youth_displaced_count_field['field_name'], impact_fields)

    def test_adult_post_processor(self):
        """Test adult post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_adult)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(adult_displaced_count_field['field_name'], impact_fields)

    def test_elderly_post_processor(self):
        """Test elderly post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_elderly)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(
            elderly_displaced_count_field['field_name'], impact_fields)

    def test_weekly_hygiene_post_processor(self):
        """Test weekly hygiene post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        # Need to run gender post processor first
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_female)
        self.assertTrue(result, message)

        # run female hygiene post processor
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_hygiene_packs)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(hygiene_packs_count_field['field_name'], impact_fields)

    def test_additional_rice_post_processor(self):
        """Test weekly hygiene post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)

        # Need to run gender post processor first
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_female)
        self.assertTrue(result, message)

        # run female hygiene post processor
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_additional_rice)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(
            additional_rice_count_field['field_name'], impact_fields)

    def test_size_post_processor(self):
        """Test size, size rate, productivity post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        impact_layer.keywords['exposure_keywords'] = {
            'exposure': 'population'
        }
        self.assertIsNotNone(impact_layer)

        # Test the size post processor.
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_size)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(size_field['field_name'], impact_fields)

        # Test the size rate post processor.
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_size_rate)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(feature_value_field['field_name'], impact_fields)

    def test_productivity_post_processors(self):
        """Test for productivity, prod cost, and prod value"""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)
        impact_layer.keywords['exposure_keywords'] = {
            'exposure': 'population'
        }
        self.assertIsNotNone(impact_layer)

        # Test the size post processor.
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_size)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(size_field['field_name'], impact_fields)

        # Test for productivity rate
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_productivity)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(productivity_field['field_name'], impact_fields)

        # Test for production cost rate
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_production_cost)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(production_cost_field['field_name'], impact_fields)

        # Test for production value rate
        result, message = run_single_post_processor(
            impact_layer,
            post_processor_production_value)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(production_value_field['field_name'], impact_fields)

        # Checking the values.
        for feature in impact_layer.getFeatures():
            size_value = feature.attribute(size_field['field_name'])

            # Inputs
            productivity_rate = feature.attribute(
                productivity_rate_field['field_name'])
            production_cost_rate = feature.attribute(
                production_cost_rate_field['field_name'])
            production_value_rate = feature.attribute(
                production_value_rate_field['field_name'])

            # result
            productivity = feature.attribute(
                productivity_field['field_name'])
            production_cost = feature.attribute(
                production_cost_field['field_name'])
            production_value = feature.attribute(
                production_value_field['field_name'])

            # Checking
            self.assertAlmostEqual(
                productivity, size_value * productivity_rate)
            self.assertAlmostEqual(
                production_cost, size_value * production_cost_rate)
            self.assertAlmostEqual(
                production_value, size_value * production_value_rate)


    def test_affected_post_processor(self):
        """Test affected  post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)

        # Need to add keywords on the fly.
        impact_layer.keywords['hazard_keywords'] = {
            'hazard': 'flood',
            'classification': 'flood_hazard_classes'
        }
        impact_layer.keywords['exposure_keywords'] = {
            'exposure': 'structure'
        }

        result, message = run_single_post_processor(
            impact_layer,
            post_processor_affected)
        self.assertTrue(result, message)

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(affected_field['field_name'], impact_fields)

    def test_enough_input(self):
        """Test to check the post processor input checker."""

        # We need to monkey patch some keywords to the impact layer.
        layer = self.FakeMonkeyPatch()

        # # # Test postprocessor which needs field type input

        # Gender postprocessor with female ratio missing.
        layer.keywords = {
            'inasafe_fields': {
                'displaced_field': 'displaced'
            }
        }
        # noinspection PyTypeChecker
        result = enough_input(layer, post_processor_female['input'])
        self.assertFalse(result[0])

        # Gender postprocessor with female ratio presents.
        layer.keywords = {
            'inasafe_fields': {
                'displaced_field': 'displaced',
                'female_ratio_field': 'female_r'
            },
            'exposure_keywords': {
                'exposure': exposure_population['key']
            }
        }
        # noinspection PyTypeChecker
        result = enough_input(layer, post_processor_female['input'])
        self.assertTrue(result[0])

        # # # Test postprocessor with alternative source for a given input

        post_processor_input_alternatives = {
            'key': 'post_processor_alternative_input_sample',
            'name': 'Alternative Input Type Sample',
            'input': {
                # input as a list means, try to get the input from the
                # listed source. Pick the first available
                'population': [
                    {
                        'value': displaced_field,
                        'type': field_input_type,
                    },
                    {
                        'value': affected_field,
                        'type': field_input_type,
                    }]
            }
        }

        # population and affected count missing
        layer.keywords = {
            'inasafe_fields': {

            }
        }

        result, _ = enough_input(
            layer, post_processor_input_alternatives['input'])
        self.assertFalse(result)

        # Minimum needs postprocesseor with displaced_field present
        layer.keywords = {
            'inasafe_fields': {
                'displaced_field': 'displaced'
            }
        }

        result, _ = enough_input(
            layer, post_processor_input_alternatives['input'])
        self.assertTrue(result)

        # Minimum needs postprocessor with alternative dynamic field
        # population present

        # Also to test dynamic_field input type
        layer.keywords = {
            'inasafe_fields': {
                'affected_field': 'affected_population'
            }
        }

        result, _ = enough_input(
            layer, post_processor_input_alternatives['input'])
        self.assertTrue(result)

        # # # Test postprocessor with dynamic field input type

        layer.keywords = {
            'inasafe_fields': {
                'population_exposure_count_field': 'exposure_population'
            }
        }

        # sample postprocessor with dynamic field input type
        post_processor_dynamic_field = {
            'input': {
                'population':
                    {
                        'value': exposure_count_field,
                        'field_param': exposure_population['key'],
                        'type': dynamic_field_input_type,
                    }
            }
        }

        result, _ = enough_input(layer, post_processor_dynamic_field['input'])
        self.assertTrue(result)

        # # # Test postprocessor with needs profile input type

        # sample postprocessor with needs profile input type
        post_processor_needs_profile = {
            'input': {
                'amount': {
                    'type': needs_profile_input_type,
                    'value': 'Fruits'
                }
            }
        }

        # Minimum needs postprocessor with minimum needs profile not found
        # No Fruits needs parameter

        layer.keywords = {
            'inasafe_fields': {
                'population_count_field': 'population'
            }
        }

        result, _ = enough_input(layer, post_processor_needs_profile['input'])
        self.assertFalse(result)

        # Minimum needs postprocessor with correct profile found
        # There is Rice needs parameter
        post_processor_needs_profile['input']['amount']['value'] = 'Rice'

        result, _ = enough_input(layer, post_processor_needs_profile['input'])
        self.assertTrue(result)

        # # # Test postprocessor with keyword input
        layer.keywords = {
            'inasafe_fields': {
                'hazard_class_field': 'hazard_class'
            }
        }

        result, _ = enough_input(layer, post_processor_affected['input'])
        self.assertFalse(result)

        layer.keywords = {
            'inasafe_fields': {
                'hazard_class_field': 'hazard_class'
            },
            'hazard_keywords': {
                'hazard': hazard_generic['key'],
                'classification': generic_hazard_classes['key']
            },
            'exposure_keywords': {
                'exposure': exposure_population['key']
            }
        }

        result, _ = enough_input(layer, post_processor_affected['input'])
        self.assertTrue(result)

    def test_evaluate_formula(self):
        """Test for evaluating formula."""
        formula = 'population * gender_ratio'
        variables = {
            'population': 100,
            'gender_ratio': 0.45
        }
        self.assertEqual(45, evaluate_formula(formula, variables))

        variables = {
            'population': None,
            'gender_ratio': 0.45
        }
        self.assertIsNone(evaluate_formula(formula, variables))


if __name__ == '__main__':
    unittest.main()
