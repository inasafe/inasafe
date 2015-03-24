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
from safe.impact_functions.generic.classified_hazard_population.impact_function import \
    ClassifiedHazardPopulationFunction

__author__ = 'lucernae'
__filename__ = 'test_classified_hazard_building'
__date__ = '24/03/15'


import unittest
import os

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.test.utilities import HAZDATA, TESTDATA
from safe.common.utilities import OrderedDict


class TestClassifiedHazardPopulationFunction(unittest.TestCase):
    """Test for ClassifiedHazardPopulationImpactFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(ClassifiedHazardPopulationFunction)

    def test_run(self):
        function = ClassifiedHazardPopulationFunction.instance()

        population = 'people_jakarta_clip.tif'
        flood_data = 'jakarta_flood_category_123.asc'

        hazard_filename = os.path.join(HAZDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact_summary = function.impact

        keywords = impact_summary.get_keywords()

        message = 'Result not as expected'
        weekly_rice = keywords['total_needs']['weekly'][0]['amount']
        self.assertEqual(weekly_rice, 282800, message)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'classes',
            'layer_type': 'raster',
            'data_type': 'classified'
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
        self.assertEqual('ClassifiedHazardPopulationFunction',
                         retrieved_IF,
                         'Expecting ClassifiedHazardPopulationFunction.'
                         'But got %s instead' %
                         retrieved_IF)