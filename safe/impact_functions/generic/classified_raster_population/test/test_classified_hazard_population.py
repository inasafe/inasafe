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
__author__ = 'lucernae'
__filename__ = 'test_classified_hazard_building'
__date__ = '24/03/15'

import unittest

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.test.utilities import test_data_path
from safe.impact_functions.generic.classified_raster_population\
    .impact_function import ClassifiedRasterHazardPopulationFunction


class TestClassifiedHazardPopulationFunction(unittest.TestCase):
    """Test for ClassifiedHazardPopulationImpactFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ClassifiedRasterHazardPopulationFunction)

    def test_run(self):
        function = ClassifiedRasterHazardPopulationFunction.instance()

        hazard_path = test_data_path('hazard', 'classified_flood_20_20.asc')
        exposure_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact_layer = function.impact

        impact_data = impact_layer.get_data()

        # Total people affected = 200
        expected = 200
        result = sum(sum(impact_data))
        message = 'Expecting %s, but it returns %s' % (expected, result)
        self.assertEqual(expected, result, message)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'raster',
            'hazard': 'flood',
            'hazard_category': 'multiple_event',
            'raster_hazard_classification': 'generic_raster_hazard_classes'
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
            ClassifiedRasterHazardPopulationFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
