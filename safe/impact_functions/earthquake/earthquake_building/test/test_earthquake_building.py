# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact function Test Cases.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '11/12/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.earthquake.earthquake_building.impact_function \
    import EarthquakeBuildingFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer


class TestEarthquakeBuildingFunction(unittest.TestCase):
    """Test for Earthquake on Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(EarthquakeBuildingFunction)

    def test_run(self):
        """TestEarthquakeBuildingFunction: Test running the IF."""
        eq_path = test_data_path('hazard', 'earthquake.tif')
        building_path = test_data_path(
            'exposure', 'buildings.shp')

        eq_layer = read_layer(eq_path)
        building_layer = read_layer(building_path)

        impact_function = EarthquakeBuildingFunction.instance()
        impact_function.hazard = eq_layer
        impact_function.exposure = building_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = ('In the event of earthquake how many '
                             'buildings might be affected')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)
        # Count by hand,
        # 1 = low, 2 = medium, 3 = high
        impact = {
            1: 0,
            2: 181,
            3: 0
        }
        result = {
            1: 0,
            2: 0,
            3: 0
        }
        impact_features = impact_layer.get_data()
        for i in range(len(impact_features)):
            impact_feature = impact_features[i]
            level = impact_feature.get(impact_function.target_field)
            result[level] += 1

        message = 'Expecting %s, but it returns %s' % (impact, result)
        self.assertEqual(impact, result, message)

    def test_filter(self):
        """TestEarthquakeBuildingFunction: Test filtering IF"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'earthquake',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'mmi'
        }

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'none',
            'layer_geometry': 'point',
            'exposure': 'structure'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            EarthquakeBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
