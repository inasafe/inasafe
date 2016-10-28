# coding=utf-8
"""Test for Impact Function."""

import unittest
import json
import os
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
from safe.test.utilities import load_test_vector_layer
from safe.impact_function_v4.impact_function import ImpactFunction

from qgis.core import QgsVectorLayer, QgsRasterLayer

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
            raise IOError('No aggregation file')

    impact_function = ImpactFunction()
    if use_debug:
        impact_function.debug = True

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
            'gisv4', 'exposure', 'buildings.geojson')
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
        self.assertIsNotNone(impact_function.aggregate_hazard_impacted)
        # self.assertIsNotNone(impact_function.aggregation_impacted)
        self.assertIsNotNone(impact_function.analysis_layer)

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Duplicate test of test_scenario_directory.')
    def test_scenario(self):
        """Run test single scenario."""
        self.maxDiff = None
        use_debug = True

        scenario_path = standard_data_path(
            'scenario',
            'raster_classified_hazard_on_'
            'indivisible_polygons_exposure_'
            'grid_aggregation.json')
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
            try:
                self.assertDictEqual(expected, result)
            except:
                # In case of an exception, print the scenario path and re raise
                print 'Error with the scenario %s' % scenario_path
                raise

        path = standard_data_path('scenario')

        json_files = [
            join(path, f) for f in listdir(path)
            if isfile(join(path, f)) and f.endswith('json')
        ]

        for json_file in json_files:
            test_scenario(json_file)

    def test_post_processor(self):
        """Test for running post processor."""

        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.shp',
            clone_to_memory=True)
        self.assertIsNotNone(impact_layer)
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
