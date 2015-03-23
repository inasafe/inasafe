# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Flood Vector on Population Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'
__date__ = '20/03/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.test.utilities import TESTDATA, get_qgis_app
from safe.impact_functions.inundation.flood_population_evacuation_polygon_hazard.impact_function import \
    FloodEvacuationFunctionVectorHazard


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodEvacuationFunctionVectorHazard(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodEvacuationFunctionVectorHazard)

    def test_run(self):
        function = FloodEvacuationFunctionVectorHazard.instance()

        population = 'pop_clip_flood_test.tif'
        flood_data = 'flood_poly_clip_flood_test.shp'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)
        # Let's set the extent to the hazard extent
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.extent = hazard_layer.extent
        function.run()
        impact = function.impact

        keywords = impact.get_keywords()
        # print "keywords", keywords
        affected_population = float(keywords['affected_population'])
        total_population = keywords['total_population']

        self.assertEqual(affected_population, 134000)
        self.assertEqual(total_population, 163000)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'wetdry',
            'layer_type': 'vector',
            'data_type': 'polygon'
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
        self.assertEqual('FloodEvacuationFunctionVectorHazard',
                         retrieved_IF,
                         'Expecting FloodEvacuationFunctionVectorHazard.'
                         'But got %s instead' %
                         retrieved_IF)
