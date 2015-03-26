# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Flood Vector Building Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'akbargumbira@gmail.com'
__date__ = '11/12/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_vector_osm_building_impact.\
    impact_function import FloodVectorBuildingFunction
from safe.storage.core import read_layer
from safe.test.utilities import test_data_path, get_qgis_app


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodVectorBuildingFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodVectorBuildingFunction)

    def test_run(self):
        impact_function = FloodVectorBuildingFunction.instance()

        hazard_path = test_data_path(
            'hazard', 'region_a', 'flood', 'flood_multipart_polygons.shp')
        exposure_path = test_data_path(
            'exposure', 'region_a', 'infrastructure', 'buildings.shp')

        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        impact_function.hazard = hazard_layer
        impact_function.exposure = exposure_layer
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = ('In the event of flood polygon region a how '
                             'many buildings region a might be flooded')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question())
        self.assertEqual(expected_question, impact_function.question(), message)

        # Extract calculated result
        keywords = impact_layer.get_keywords()
        buildings_total = keywords['buildings_total']
        buildings_affected = keywords['buildings_affected']

        self.assertEqual(buildings_total, 131)
        self.assertEqual(buildings_affected, 27)

    def test_filter(self):
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'wetdry',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        exposure_keywords = {
            'subcategory': 'structure',
            'units': 'building_type',
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
            FloodVectorBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
