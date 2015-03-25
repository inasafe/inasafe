# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Categorised Hazard Population Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.impact_functions.generic.continuous_hazard_population.impact_function import \
    ContinuousHazardPopulationFunction

__author__ = 'lucernae'
__filename__ = 'test_classified_hazard_building'
__date__ = '24/03/15'


import unittest
import os

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.test.utilities import HAZDATA, TESTDATA, EXPDATA
from safe.common.utilities import OrderedDict


class TestContinuousHazardPopulationFunction(unittest.TestCase):
    """Test for ContinuousHazardPopulationFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(ContinuousHazardPopulationFunction)

    def test_run(self):
        function = ContinuousHazardPopulationFunction.instance()

        population = 'people_jakarta_clip.tif'
        flood_data = 'flood_jakarta_clip.tif'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact = function.impact

        # print "keywords", keywords
        keywords = impact.get_keywords()
        total_needs_full = keywords['total_needs']
        total_needs_weekly = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['weekly']
        ])
        total_needs_single = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['single']
        ])

        self.assertEqual(total_needs_weekly['Rice [kg]'], 1044400)
        self.assertEqual(total_needs_weekly['Family Kits'], 74600)
        self.assertEqual(total_needs_weekly['Drinking Water [l]'], 6527500)
        self.assertEqual(total_needs_weekly['Clean Water [l]'], 24991000)
        self.assertEqual(total_needs_single['Toilets'], 18650)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'metres_depth',
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
        self.assertEqual('ContinuousHazardPopulationFunction',
                         retrieved_IF,
                         'Expecting ContinuousHazardPopulationFunction.'
                         'But got %s instead' %
                         retrieved_IF)