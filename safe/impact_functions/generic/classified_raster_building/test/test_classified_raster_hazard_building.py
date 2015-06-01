# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Classified Hazard Building Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'lucernae'
__filename__ = 'test_classified_hazard_building'
__date__ = '23/03/15'

import unittest
import math

from safe.impact_functions.generic.classified_raster_building\
    .impact_function import ClassifiedRasterHazardBuildingFunction
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.test.utilities import test_data_path


class TestClassifiedHazardBuildingFunction(unittest.TestCase):
    """Test for ClassifiedHazardPopulationImpactFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ClassifiedRasterHazardBuildingFunction)

    def test_run(self):
        function = ClassifiedRasterHazardBuildingFunction.instance()

        hazard_path = test_data_path('hazard', 'classified_flood_20_20.asc')
        exposure_path = test_data_path('exposure', 'buildings.shp')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact_layer = function.impact
        impact_data = impact_layer.get_data()

        # Count
        expected_impact = {
            1.0: 67,
            2.0: 49,
            3.0: 64
        }

        result_impact = {
            1.0: 0,
            2.0: 0,
            3.0: 0
        }
        for impact_feature in impact_data:
            level = impact_feature['level']
            if not math.isnan(level):
                result_impact[level] += 1
        message = 'Expecting %s, but it returns %s' % (
            expected_impact, result_impact)
        self.assertEqual(expected_impact, result_impact, message)

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
            'layer_mode': 'none',
            'layer_geometry': 'polygon',
            'exposure': 'structure',
        }
        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            ClassifiedRasterHazardBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
