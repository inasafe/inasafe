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
from safe.impact_functions.volcanic.volcano_polygon_population.impact_function \
    import VolcanoPolygonPopulationFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer


class TestVolcanoPolygonBuildingFunction(unittest.TestCase):
    """Test for Volcano Polygon on Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(VolcanoPolygonPopulationFunction)

    def test_run(self):
        """TestVolcanoPolygonPopulationFunction: Test running the IF."""
        merapi_point_path = test_data_path(
            'hazard', 'region_c', 'volcano', 'merapi_point.shp')
        merapi_krb_path = test_data_path(
            'hazard', 'region_c', 'volcano', 'merapi_krb.shp')
        population_path = test_data_path(
            'exposure', 'region_c', 'population', 'tenbytenraster.asc')

        merapi_point_layer = read_layer(merapi_point_path)
        merapi_krb_layer = read_layer(merapi_krb_path)
        population_layer = read_layer(population_path)

        impact_function = VolcanoPolygonPopulationFunction.instance()

        # 1. Run merapi point
        impact_function.hazard = merapi_point_layer
        impact_function.exposure = population_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = ('In the event of volcano merapi point region c '
                             'how many population region c might need evacuation')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question())
        self.assertEqual(expected_question, impact_function.question(), message)
        # Count by hand
        impact = {
            3000: 12,
            5000: 18,
            10000: 20
        }
        impact_features = impact_layer.get_data()
        for i in range(len(impact_features)):
            impact_feature = impact_features[i]
            radius = impact_feature.get('Radius')
            expected = impact[radius]
            result = impact_feature['population']
            message = 'Expecting %s, but it returns %s' % (expected, result)
            self.assertEqual(expected, result, message)

        # 2. Run merapi krb
        impact_function.hazard = merapi_krb_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = ('In the event of volcano merapi krb region c how '
                             'many population region c might need evacuation')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question())
        self.assertEqual(expected_question, impact_function.question(), message)
        # Count by hand
        impact = {
            'Kawasan Rawan Bencana III': 30,
            'Kawasan Rawan Bencana II': 8,
            'Kawasan Rawan Bencana I': 0,
        }
        impact_features = impact_layer.get_data()
        for i in range(len(impact_features)):
            impact_feature = impact_features[i]
            krb_zone = impact_feature.get('KRB')
            expected = impact[krb_zone]
            result = impact_feature['population']
            message = 'Expecting %s, but it returns %s' % (expected, result)
            self.assertEqual(expected, result, message)

    def test_filter(self):
        """TestVolcanoPolygonPopulationFunction: Test filtering IF"""
        hazard_keywords = {
            'category': 'hazard',
            'subcategory': 'volcano',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        exposure_keywords = {
            'category': 'exposure',
            'subcategory': 'population',
            'layer_type': 'raster',
            'data_type': 'continuous',
            'unit': 'people_per_pixel'
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
