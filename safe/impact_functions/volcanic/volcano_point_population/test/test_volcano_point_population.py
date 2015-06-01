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
import numpy

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.volcanic.volcano_point_population\
    .impact_function import VolcanoPointPopulationFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer


class TestVolcanoPointPopulationFunction(unittest.TestCase):
    """Test for Volcano Point on Population Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(VolcanoPointPopulationFunction)

    def test_run(self):
        """TestVolcanoPointPopulationFunction: Test running the IF."""
        merapi_point_path = test_data_path('hazard', 'volcano_point.shp')
        population_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')

        merapi_point_layer = read_layer(merapi_point_path)
        population_layer = read_layer(population_path)

        impact_function = VolcanoPointPopulationFunction.instance()

        # Run merapi point
        impact_function.hazard = merapi_point_layer
        impact_function.exposure = population_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = (
            'In the event of a volcano point how many '
            'people might be impacted')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)
        # Count by hand
        expected_affected_population = 200
        result = numpy.nansum(impact_layer.get_data())
        message = 'Expecting %s, but it returns %s' % (
            expected_affected_population, result)
        self.assertEqual(expected_affected_population, result, message)

    def test_filter(self):
        """TestVolcanoPointPopulationFunction: Test filtering IF"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'none',
            'layer_geometry': 'point',
            'hazard': 'volcano',
            'hazard_category': 'multiple_event',
            'vector_hazard_classification': 'volcano_vector_hazard_classes'
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
            VolcanoPointPopulationFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
