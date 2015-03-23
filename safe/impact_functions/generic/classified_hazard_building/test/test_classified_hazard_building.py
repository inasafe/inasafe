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
__date__ = '23/03/15'


import unittest
import os

from safe.impact_functions.generic.classified_hazard_building.impact_function import \
    ClassifiedHazardBuildingImpactFunction
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.test.utilities import HAZDATA, EXPDATA


class TestClassifiedHazardBuildingFunction(unittest.TestCase):
    """Test for ClassifiedHazardPopulationImpactFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(ClassifiedHazardBuildingImpactFunction)

    def test_run(self):
        function = ClassifiedHazardBuildingImpactFunction.instance()

        building = 'DKI_buildings.shp'
        flood_data = 'jakarta_flood_category_123.asc'

        hazard_filename = os.path.join(HAZDATA, flood_data)
        exposure_filename = os.path.join(EXPDATA, building)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact_summary = function.impact

        keywords = impact_summary.get_keywords()

        message = 'Result not as expected'
        self.assertEqual(keywords['buildings_affected'], 2345, message)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'classes',
            'layer_type': 'raster',
            'data_type': 'classified'
        }

        exposure_keywords = {
            'subcategory': 'structure',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('ClassifiedHazardBuildingImpactFunction',
                         retrieved_IF,
                         'Expecting ClassifiedHazardBuildingImpactFunction.'
                         'But got %s instead' %
                         retrieved_IF)