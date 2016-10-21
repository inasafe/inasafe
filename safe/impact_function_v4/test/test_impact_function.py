# coding=utf-8
"""Test for Impact Function."""

import unittest
import json
import os

from safe.test.utilities import get_control_text
from safe.test.utilities import get_qgis_app, standard_data_path
from safe.test.debug_helper import print_attribute_table

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitionsv4.fields import (
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    feature_value_field,
    population_count_field,
    exposure_type_field,
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
from safe.utilities.unicode import byteify
from safe.test.utilities import load_test_vector_layer
from safe.impact_function_v4.impact_function import ImpactFunction
from safe.impact_function_v4.impact_function import evaluate_formula

from qgis.core import QgsVectorLayer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def read_json_flow(json_path):
    """Helper method to read json file that contains a scenario

    :param json_path: Path to json file.
    :type json_path: unicode, str

    :returns: Tuple of dictionary contains a scenario and expected result
    :rtype: (dict, dict)
    """
    with open(json_path) as json_data:
        data = byteify(json.load(json_data))
    return data['scenario'], data['expected']


def run_scenario(scenario, use_debug=False):
    """Run scenario

    :param scenario: Dictionary of hazard, exposure, and aggregation.
    :type scenario: dict

    :param use_debug: If we should use debug when we run the scenario.
    :type use_debug: bool

    :returns: Flow dictionary.
    :rtype: dict
    """
    if os.path.exists(scenario['exposure']):
        exposure_path = scenario['exposure']
    elif os.path.exists(standard_data_path('exposure', scenario['exposure'])):
        exposure_path = standard_data_path('exposure', scenario['exposure'])
    else:
        raise IOError('No exposure file')
    if os.path.exists(scenario['hazard']):
        hazard_path = scenario['hazard']
    elif os.path.exists(standard_data_path('hazard', scenario['hazard'])):
        hazard_path = standard_data_path('hazard', scenario['hazard'])
    else:
        raise IOError('No hazard file')

    if not scenario['aggregation']:
        aggregation_path = None
    else:
        if os.path.exists(scenario['aggregation']):
            aggregation_path = scenario['aggregation']
        elif os.path.exists(standard_data_path(
                'aggregation', scenario['aggregation'])):
            aggregation_path = standard_data_path(
                'aggregation', scenario['aggregation'])
        else:
            aggregation_path = None

    impact_function = ImpactFunction()
    if use_debug:
        impact_function.debug = True
    impact_function.hazard = QgsVectorLayer(hazard_path, 'Hazard', 'ogr')
    impact_function.exposure = QgsVectorLayer(exposure_path, 'Exposure', 'ogr')
    if aggregation_path:
        impact_function.aggregation = QgsVectorLayer(
            aggregation_path, 'Aggregation', 'ogr')

    result = impact_function.run()
    if use_debug:
        print impact_function.datastore.uri.absolutePath()

    return result


class TestImpactFunction(unittest.TestCase):
    """Test Impact Function."""

    def test_keyword_monkey_patch(self):
        """Test behaviour of generating keywords"""
        exposure_path = standard_data_path('exposure', 'building-points.shp')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Building', 'ogr')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer

        expected_inasafe_fields = {
            exposure_type_field['key']: 'TYPE',
            population_count_field['key']: 'pop_count'
        }
        self.assertDictEqual(
            exposure_layer.keywords['inasafe_fields'], expected_inasafe_fields)

        fields = impact_function.exposure.dataProvider().fieldNameMap().keys()
        self.assertIn(
            exposure_layer.keywords['inasafe_fields']['exposure_type_field'],
            fields
        )
        inasafe_fields = exposure_layer.keywords['inasafe_fields']
        self.assertIn(inasafe_fields['population_count_field'], fields)

    def test_impact_function_behaviour(self):
        """Test behaviour of impact function"""
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer('exposure', 'roads.shp')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        self.assertEqual(impact_function.name, 'Flood Polygon On Road Line')
        self.assertEqual(impact_function.title, 'be affected')

    def test_profiling(self):
        """Test running impact function on test data."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.run()
        message = impact_function.performance_log_message().to_text()
        expected_result = get_control_text(
            'test-profiling-logs.txt')

        for line in expected_result:
            line = line.replace('\n', '')
            if line == '' or line == '-':
                continue
            self.assertIn(line, message)

    def test_run_impact_function(self):
        """Test running impact function on test data."""
        use_debug = True
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Set up impact function
        impact_function = ImpactFunction()
        if use_debug:
            impact_function.debug = True
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.run()
        if use_debug:
            print impact_function.datastore.uri.absolutePath()
            print impact_function.datastore.layers()
        self.assertIsNotNone(impact_function.impact)

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Duplicate test of test_scenario_directory.')
    def test_scenario(self):
        """Run test single scenario."""
        self.maxDiff = None
        use_debug = True

        scenario_path = standard_data_path(
            'scenario', 'polygon_hazard_point_exposure.json')
        scenario, expected = read_json_flow(scenario_path)
        result = run_scenario(scenario, use_debug)
        self.assertDictEqual(expected, result)

    def test_scenario_directory(self):
        """Run test scenario in directory."""
        self.maxDiff = None
        use_debug = False

        def test_scenario(scenario_path):
            scenario, expected = read_json_flow(scenario_path)
            result = run_scenario(scenario, use_debug)
            self.assertDictEqual(expected, result)

        path = standard_data_path('scenario')
        json_files = [
            os.path.join(path, f) for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))]
        for json_file in json_files:
            print json_file
            test_scenario(json_file)

    def test_gender_post_processor(self):
        """Test gender post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        result, message = impact_function.run_single_post_processor(
            post_processor_gender)
        self.assertTrue(result, message)

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

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
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        result, message = impact_function.run_single_post_processor(
            post_processor_youth)
        self.assertTrue(result, message)

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

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
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        result, message = impact_function.run_single_post_processor(
            post_processor_adult)
        self.assertTrue(result, message)

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

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
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        result, message = impact_function.run_single_post_processor(
            post_processor_elderly)
        self.assertTrue(result, message)

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

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
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        result, message = impact_function.run_single_post_processor(
            post_processor_size)
        self.assertTrue(result, message)

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

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
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        result, message = impact_function.run_single_post_processor(
            post_processor_size_rate)
        self.assertTrue(result, message)

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        self.assertIn(feature_value_field['field_name'], impact_fields)
        self.assertNotIn('size', impact_fields)

    def test_post_processor(self):
        """Test for running post processor."""

        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)
        impact_function = ImpactFunction()
        impact_function.impact = impact_layer

        impact_function.post_process()

        impact_layer = impact_function.impact
        self.assertIsNotNone(impact_layer)

        used_post_processors = [
            post_processor_size,
            post_processor_gender,
            post_processor_youth,
            post_processor_adult,
            post_processor_elderly,
        ]

        # Check if new field is added
        impact_fields = impact_layer.dataProvider().fieldNameMap().keys()
        for post_processor in used_post_processors:
            # noinspection PyTypeChecker
            for output_value in post_processor['output'].values():
                field_name = output_value['value']['field_name']
                self.assertIn(field_name, impact_fields)
        print_attribute_table(impact_layer, 1)

    def test_enough_input(self):
        """Test to check the post processor input checker."""
        impact_function = ImpactFunction()

        class FakeMonkeyPatch(object):
            pass

        # We need to monkey patch some keywords to the impact layer.
        impact_function.impact = FakeMonkeyPatch()

        # Gender postprocessor with female ratio missing.
        impact_function.impact.keywords = {
            'inasafe_fields': {
                'population_count_field': 'population'
            }
        }
        result = impact_function.enough_input(
           post_processor_gender['input'])
        self.assertFalse(result[0])

        # Gender postprocessor with female ratio missing.
        impact_function.impact.keywords = {
            'inasafe_fields': {
                'population_count_field': 'population',
                'female_ratio_field': 'female_r'
            }
        }
        result = impact_function.enough_input(
           post_processor_gender['input'])
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
