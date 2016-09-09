import unittest
import json
import os

from safe.test.utilities import get_qgis_app, standard_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.new_impact_function.impact_function import ImpactFunction

from qgis.core import QgsVectorLayer


def read_json_flow(json_path):
    """Helper method to read json file that contains a scenario

    :param json_path: Path to json file.
    :type json_path: unicode, str

    :returns: Tuple of dictionary contains a scenario and expected result
    :rtype: (dict, dict)
    """
    with open(json_path) as json_data:
        data = json.load(json_data)
    return data['scenario'], data['expected']

def run_scenario(scenario):
    """Run scenario

    :param scenario: Dictionary of hazard, exposure, and aggregation.
    :type scenario: dict

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
        elif os.path.exists(standard_data_path('aggregation', scenario['aggregation'])):
            aggregation_path = standard_data_path('aggregation', scenario['aggregation'])
        else:
            aggregation_path = None

    impact_function = ImpactFunction()
    impact_function.hazard = QgsVectorLayer(hazard_path, 'Hazard', 'ogr')
    impact_function.exposure = QgsVectorLayer(exposure_path, 'Exposure', 'ogr')
    if aggregation_path:
        impact_function.aggregation = QgsVectorLayer(aggregation_path, 'Exposure', 'ogr')

    result = impact_function.flow()

    return result

class TestImpactFunction(unittest.TestCase):
    """Test for Generic Polygon on Building Impact Function."""

    def test_impact_function_behaviour(self):
        """Test behaviour of impact function"""
        hazard_path = standard_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_path = standard_data_path('exposure', 'roads.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Roads', 'ogr')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        self.assertEqual(
            impact_function.algorithm, impact_function.line_algorithm)
        self.assertEqual(impact_function.name, 'Flood Polygon on Road Line')
        self.assertEqual(impact_function.title, 'be affected')

    @unittest.expectedFailure
    def test_run_impact_function(self):
        """Test running impact function on test data."""
        # Set up test data
        hazard_path = standard_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_path = standard_data_path('exposure', 'building-points.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Building Point', 'ogr')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.run()
        result = impact_function.impact_layer
        self.assertIsNotNone(result)

    def test_impact_function_flow(self):
        """Test running impact function on test data."""
        # Set up test data
        hazard_path = standard_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_path = standard_data_path('exposure', 'building-points.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Building Point', 'ogr')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer

        impact_function_state = impact_function.flow()
        from pprint import pprint
        pprint(impact_function_state)
        print json.dumps(impact_function_state)

    def test_scenario(self):
        scenario_path = standard_data_path('scenario', 'scenario_1.json')
        scenario, expected = read_json_flow(scenario_path)
        result = run_scenario(scenario)
        self.assertDictEqual(result, expected)

    def test_scenario_directory(self):
        self.maxDiff = None
        def test_scenario(scenario_path):
            scenario, expected = read_json_flow(scenario_path)
            result = run_scenario(scenario)
            self.assertDictEqual(result, expected)

        path = standard_data_path('scenario')
        json_files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for json_file in json_files:
            test_scenario(json_file)




if __name__ == '__main__':
    unittest.main()
