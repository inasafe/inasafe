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

import os
import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_vector_osm_building_impact.\
    impact_function import FloodVectorBuildingImpactFunction
from safe.storage.core import read_layer
from safe.test.utilities import TESTDATA, get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodVectorBuildingImpactFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodVectorBuildingImpactFunction)

    def test_run(self):
        impact_function = FloodVectorBuildingImpactFunction.instance()

        building = 'test_flood_building_impact_exposure.shp'
        flood_data = 'test_flood_building_impact_hazard.shp'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, building)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        impact_function.hazard = hazard_layer
        impact_function.exposure = exposure_layer
        impact_function.extent = [106.8139860, -6.2043560,
                           106.8405950, -6.2263570]
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = ('In the event of a flood in jakarta how many osm '
                             'building polygons might be flooded')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question())
        self.assertEqual(expected_question, impact_function.question(), message)

        # Extract calculated result
        keywords = impact_layer.get_keywords()
        buildings_total = keywords['buildings_total']
        buildings_affected = keywords['buildings_affected']

        self.assertEqual(buildings_total, 67)
        self.assertEqual(buildings_affected, 41)

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
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('FloodVectorBuildingImpactFunction',
                         retrieved_IF,
                         'Expecting FloodVectorBuildingImpactFunction.'
                         'But got %s instead' %
                         retrieved_IF)
