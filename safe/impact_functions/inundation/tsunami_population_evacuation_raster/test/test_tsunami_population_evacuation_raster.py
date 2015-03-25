# coding=utf-8

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'test_tsunami_population_evacuation_raster'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

import os
import unittest

from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_functions.inundation\
    .tsunami_population_evacuation_raster.impact_function import \
    TsunamiEvacuationFunction
from safe.test.utilities import TESTDATA, get_qgis_app
from safe.common.utilities import OrderedDict

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestTsunamiEvacuationRaster(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(TsunamiEvacuationFunction)

    def test_run(self):
        function = TsunamiEvacuationFunction.instance()

        # RM: didn't have the test data for now.
        # Will ask Akbar later
        population = 'people_jakarta_clip.tif'
        flood_data = 'flood_jakarta_clip.tif'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)
        # Let's set the extent to the hazard extent
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # print "keywords", keywords
        keywords = impact.get_keywords()
        evacuated = float(keywords['evacuated'])
        total_needs_full = keywords['total_needs']
        total_needs_weekly = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['weekly']
        ])
        total_needs_single = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['single']
        ])

        # RM: Needs to be verified by Akbar first
        expected_evacuated = 75900
        self.assertEqual(evacuated, expected_evacuated)
        self.assertEqual(total_needs_weekly['Rice [kg]'], 212520)
        self.assertEqual(total_needs_weekly['Family Kits'], 15180)
        self.assertEqual(total_needs_weekly['Drinking Water [l]'], 1328250)
        self.assertEqual(total_needs_weekly['Clean Water [l]'], 5085300)
        self.assertEqual(total_needs_single['Toilets'], 3795)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'tsunami',
            'unit': 'm',
            'layer_type': 'raster',
            'data_type': 'continuous'
        }

        exposure_keywords = {
            'subcategory': 'population',
            'layer_type': 'raster',
            'data_type': 'continuous'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('TsunamiEvacuationFunction',
                         retrieved_IF,
                         'Expecting TsunamiEvacuationFunction.'
                         'But got %s instead' %
                         retrieved_IF)
