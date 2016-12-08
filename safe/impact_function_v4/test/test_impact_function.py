# coding=utf-8
"""Test for Impact Function."""

import unittest
import json
import os
import logging
from os.path import join, isfile
from os import listdir

from safe.test.utilities import get_control_text
from safe.test.utilities import get_qgis_app, standard_data_path
from safe.test.debug_helper import print_attribute_table

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitionsv4.fields import (
    population_count_field,
    exposure_type_field,
)
from safe.definitionsv4.post_processors import (
    post_processor_gender,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly,
    post_processor_size
)
from safe.utilities.unicode import byteify
from safe.test.utilities import load_test_vector_layer, check_inasafe_fields
from safe.impact_function_v4.impact_function import ImpactFunction

from qgis.core import QgsVectorLayer, QgsRasterLayer

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def read_json_flow(json_path):
    """Helper method to read json file that contains a scenario

    :param json_path: Path to json file.
    :type json_path: unicode, str

    :returns: Tuple of dictionary contains a scenario and expected result
    :rtype: (dict, dict, dict)
    """
    with open(json_path) as json_data:
        data = byteify(json.load(json_data))
    return data['scenario'], data['expected_steps'], data['expected_outputs']


def run_scenario(scenario, use_debug=False):
    """Run scenario

    :param scenario: Dictionary of hazard, exposure, and aggregation.
    :type scenario: dict

    :param use_debug: If we should use debug_mode when we run the scenario.
    :type use_debug: bool

    :returns: Tuple(status, Flow dictionary, outputs).
    :rtype: list
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
            raise IOError('No aggregation file')

    impact_function = ImpactFunction()
    impact_function.debug_mode = use_debug

    layer = QgsVectorLayer(hazard_path, 'Hazard', 'ogr')
    if not layer.isValid():
        layer = QgsRasterLayer(hazard_path, 'Hazard')
    impact_function.hazard = layer

    layer = QgsVectorLayer(exposure_path, 'Exposure', 'ogr')
    if not layer.isValid():
        layer = QgsRasterLayer(exposure_path, 'Exposure')
    impact_function.exposure = layer

    if aggregation_path:
        impact_function.aggregation = QgsVectorLayer(
            aggregation_path, 'Aggregation', 'ogr')

    status, _ = impact_function.run()

    for layer in impact_function.outputs:
        check_inasafe_fields(layer)

    return status, impact_function.state, impact_function.outputs


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

    def test_scenario(self, scenario_path=None):
        """Run test single scenario."""
        self.maxDiff = None
        use_debug = True

        if not scenario_path:
            scenario_path = standard_data_path(
                'scenario',
                'polygon_classified_on_line.json')

        LOGGER.info('Running the scenario : %s' % scenario_path)
        scenario, expected_steps, expected_outputs = read_json_flow(
            scenario_path)
        status, steps, outputs = run_scenario(scenario, use_debug)
        self.assertEqual(0, status)
        self.assertDictEqual(expected_steps, steps)
        # - 1 because I added the profiling table, and this table is not
        # counted in the JSON file.
        self.assertEqual(len(outputs) - 1, expected_outputs['count'])

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Duplicate test of test_scenario_directory.')
    def test_scenarii(self):
        """Test manually a directory.

        This function is like test_directory, but you can control manually
        which scenario you want to launch.
        """
        scenarii = {
            'polygon_classified_on_line': False,
            'polygon_classified_on_point': False,
            'polygon_classified_on_vector_population': True,
            'polygon_continuous_on_line': False,
            'raster_classified_on_classified_raster': False,
            'raster_classified_on_indivisible_polygons_with_grid': False,
            'raster_classified_on_line_with_grid': False,
            'raster_continuous_on_divisible_polygons_with_grid': False,
            'raster_continuous_on_line': False,
            'raster_continuous_on_raster_population': False,
        }

        path = standard_data_path('scenario')
        for scenario, enabled in scenarii.iteritems():
            if enabled:
                self.test_scenario(join(path, scenario + '.json'))

        json_files = [
            join(path, f) for f in listdir(path)
            if isfile(join(path, f)) and f.endswith('json')
        ]
        self.assertEqual(len(json_files), len(scenarii))

    def test_scenario_directory(self):
        """Run test scenario in directory."""
        path = standard_data_path('scenario')

        json_files = [
            join(path, f) for f in listdir(path)
            if isfile(join(path, f)) and f.endswith('json')
        ]

        count = 0
        for json_file in json_files:
            scenario, expected_steps, expected_outputs = read_json_flow(
                json_file)
            if scenario.get('enable', True):
                print "Test JSON scenario : "
                print json_file
                self.test_scenario(json_file)
                count += 1
        self.assertEqual(len(json_files), count)

    def test_post_processor(self):
        """Test for running post processor."""

        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)

        impact_layer.keywords['hazard_keywords'] = {
            'classification': 'flood_hazard_classes'
        }

        impact_function = ImpactFunction()

        impact_function.post_process(impact_layer)

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


if __name__ == '__main__':
    unittest.main()
