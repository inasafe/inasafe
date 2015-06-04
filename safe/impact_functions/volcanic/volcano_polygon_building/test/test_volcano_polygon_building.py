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
from safe.impact_functions.volcanic.volcano_polygon_building.impact_function \
    import VolcanoPolygonBuildingFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer


class TestVolcanoPolygonBuildingFunction(unittest.TestCase):
    """Test for Volcano Polygon on Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(VolcanoPolygonBuildingFunction)

    def test_run(self):
        """TestVolcanoPolygonBuildingFunction: Test running the IF."""
        volcano_path = test_data_path('hazard', 'volcano_krb.shp')
        building_path = test_data_path('exposure', 'buildings.shp')

        hazard_layer = read_layer(volcano_path)
        exposure_layer = read_layer(building_path)

        impact_function = VolcanoPolygonBuildingFunction.instance()
        impact_function.hazard = hazard_layer
        impact_function.exposure = exposure_layer
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = ('In the event of volcano krb how many buildings '
                             'might be affected')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)

        # The buildings should all be categorised into 5000 zone
        zone_sum = impact_layer.get_data(attribute=impact_function.target_field)
        krb3_zone_count = zone_sum.count('Kawasan Rawan Bencana III')
        krb2_zone_count = zone_sum.count('Kawasan Rawan Bencana II')
        # The result (counted by hand)
        expected_krb3_count = 11
        expected_krb2_count = 161
        message = 'Expecting %s for KRB III zone, but it returns %s' % (
            krb3_zone_count, expected_krb3_count)
        self.assertEqual(krb3_zone_count, expected_krb3_count, message)
        message = 'Expecting %s for KRB II zone, but it returns %s' % (
            krb2_zone_count, expected_krb2_count)
        self.assertEqual(krb2_zone_count, expected_krb2_count, message)

    def test_filter(self):
        """TestVolcanoPolygonBuildingFunction: Test filtering IF"""
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
            'layer_mode': 'none',
            'layer_geometry': 'polygon',
            'exposure': 'structure'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            VolcanoPolygonBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
