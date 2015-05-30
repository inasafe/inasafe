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
from safe.impact_functions.generic.continuous_hazard_population\
    .impact_function import ContinuousHazardPopulationFunction

__author__ = 'lucernae'
__filename__ = 'test_classified_hazard_building'
__date__ = '24/03/15'


import unittest

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.test.utilities import test_data_path
from safe.common.utilities import OrderedDict


class TestContinuousHazardPopulationFunction(unittest.TestCase):
    """Test for ContinuousHazardPopulationFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ContinuousHazardPopulationFunction)

    def test_run(self):
        function = ContinuousHazardPopulationFunction.instance()

        hazard_path = test_data_path(
            'hazard', 'continuous_flood_20_20.asc')
        exposure_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

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

        self.assertEqual(total_needs_weekly['Rice [kg]'], 336)
        self.assertEqual(total_needs_weekly['Drinking Water [l]'], 2100)
        self.assertEqual(total_needs_weekly['Clean Water [l]'], 8040)
        self.assertEqual(total_needs_weekly['Family Kits'], 24)
        self.assertEqual(total_needs_single['Toilets'], 6)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'flood',
            'hazard_category': 'multiple_event',
            'continuous_hazard_unit': 'generic'
        }

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'exposure': 'population',
            'exposure_unit': 'count'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            ContinuousHazardPopulationFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
