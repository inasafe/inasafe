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
from safe.impact_functions.volcanic.volcano_polygon_population\
    .impact_function import VolcanoPolygonPopulationFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer


class TestVolcanoPolygonPopulationFunction(unittest.TestCase):
    """Test for Volcano Polygon on Population Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(VolcanoPolygonPopulationFunction)

    def test_run(self):
        """TestVolcanoPolygonPopulationFunction: Test running the IF."""
        merapi_krb_path = test_data_path('hazard', 'volcano_krb.shp')
        population_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')

        merapi_krb_layer = read_layer(merapi_krb_path)
        population_layer = read_layer(population_path)

        impact_function = VolcanoPolygonPopulationFunction.instance()

        # 2. Run merapi krb
        impact_function.hazard = merapi_krb_layer
        impact_function.exposure = population_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = ('In the event of volcano krb how many population '
                             'might need evacuation')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)
        # Count by hand
        expected_affected_population = 181
        result = numpy.nansum(impact_layer.get_data())
        self.assertEqual(expected_affected_population, result, message)

    def test_filter(self):
        """TestVolcanoPolygonPopulationFunction: Test filtering IF"""
        hazard_keywords = {
            'title': 'merapi',
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
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
            VolcanoPolygonPopulationFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
