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
from safe.test.utilities import test_data_path, get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.volcanic.volcano_point_building.impact_function \
    import VolcanoPointBuildingFunction
from safe.storage.core import read_layer
from safe.storage.safe_layer import SafeLayer


class TestVolcanoPointBuildingFunction(unittest.TestCase):
    """Test for Volcano Point on Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(VolcanoPointBuildingFunction)

    def test_run(self):
        """TestVolcanoPointBuildingFunction: Test running the IF."""
        volcano_path = test_data_path('hazard', 'volcano_point.shp')
        building_path = test_data_path('exposure', 'buildings.shp')

        hazard_layer = read_layer(volcano_path)
        exposure_layer = read_layer(building_path)

        impact_function = VolcanoPointBuildingFunction.instance()
        impact_function.hazard = SafeLayer(hazard_layer)
        impact_function.exposure = SafeLayer(exposure_layer)
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = (
            'In the event of volcano point how many buildings might be '
            'affected')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)

        # The buildings should all be categorised into 3000 zone
        zone_sum = sum(impact_layer.get_data(
            attribute=impact_function.target_field))
        expected_sum = 3 * 181
        message = 'Expecting %s, but it returns %s' % (expected_sum, zone_sum)
        self.assertEqual(zone_sum, expected_sum, message)

    def test_filter(self):
        """TestVolcanoPointBuildingFunction: Test filtering IF"""
        hazard_keywords = {
            'volcano_name_field': 'NAME',
            'hazard_category': 'multiple_event',
            'keyword_version': 3.2,
            'title': 'Volcano Point',
            'hazard': 'volcano',
            'source': 'smithsonian',
            'layer_geometry': 'point',
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
        }

        exposure_keywords = {
            'license': 'Open Data Commons Open Database License (ODbL)',
            'keyword_version': 3.2,
            'structure_class_field': 'TYPE',
            'title': 'Buildings',
            'layer_geometry': 'polygon',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'date': '26-03-2015 14:03',
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'exposure': 'structure'}

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            VolcanoPointBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
