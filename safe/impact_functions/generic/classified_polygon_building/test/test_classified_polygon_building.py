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
from safe.impact_functions.generic.classified_polygon_building.impact_function\
    import ClassifiedPolygonBuildingFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer


class TestClassifiedPolygonBuildingFunction(unittest.TestCase):
    """Test for Generic Polygon on Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ClassifiedPolygonBuildingFunction)

    def test_run(self):
        """TestGenericPolygonBuildingFunction: Test running the IF."""
        generic_polygon_path = test_data_path(
            'hazard', 'classified_generic_polygon.shp')
        building_path = test_data_path('exposure', 'buildings.shp')

        hazard_layer = read_layer(generic_polygon_path)
        exposure_layer = read_layer(building_path)

        impact_function = ClassifiedPolygonBuildingFunction.instance()
        impact_function.hazard = hazard_layer
        impact_function.exposure = exposure_layer
        impact_function.parameters['hazard zone attribute'] = 'h_zone'
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = ('In each of the hazard zones how many buildings '
                             'might be affected.')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)

        zone_sum = impact_layer.get_data(attribute='zone')
        high_zone_count = zone_sum.count('High Hazard Zone')
        medium_zone_count = zone_sum.count('Medium Hazard Zone')
        low_zone_count = zone_sum.count('Low Hazard Zone')
        # The result
        expected_high_count = 11
        expected_medium_count = 161
        expected_low_count = 0
        message = 'Expecting %s for High Hazard Zone, but it returns %s' % (
            high_zone_count, expected_high_count)
        self.assertEqual(high_zone_count, expected_high_count, message)

        message = 'Expecting %s for Medium Hazard Zone, but it returns %s' % (
            expected_medium_count, medium_zone_count)
        self.assertEqual(medium_zone_count, expected_medium_count, message)

        message = 'Expecting %s for Low Hazard Zone, but it returns %s' % (
            expected_low_count, low_zone_count)
        self.assertEqual(expected_low_count, low_zone_count, message)

    def test_filter(self):
        """TestGenericPolygonBuildingFunction: Test filtering IF"""
        hazard_keywords = {
            'title': 'Generic Polygon',
            'category': 'hazard',
            'subcategory': 'earthquake',
            'unit': 'classes',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        exposure_keywords = {
            'category': 'exposure',
            'subcategory': 'structure',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            ClassifiedPolygonBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
