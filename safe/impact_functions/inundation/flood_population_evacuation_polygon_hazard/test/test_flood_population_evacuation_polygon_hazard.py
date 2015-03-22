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

__author__ = 'Rizky Maulana Nugraha'
__date__ = '20/03/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.test.utilities import TESTDATA, get_qgis_app, clone_shp_layer, \
    test_data_path, HAZDATA
from safe.impact_functions.inundation.flood_population_evacuation_polygon_hazard.impact_function import \
    FloodEvacuationFunctionVectorHazard
from safe.utilities.qgis_layer_wrapper import QgisWrapper

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodEvacuationFunctionVectorHazard(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodEvacuationFunctionVectorHazard)

    def test_run(self):
        function = FloodEvacuationFunctionVectorHazard.instance()

        # RM: didn't have the test data for now.
        # Will ask Akbar later
        building = 'people_jakarta_clip.tif'
        flood_data = 'Jakarta_RW_2007flood.shp'

        hazard_filename = os.path.join(HAZDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, building)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)
        # Let's set the extent to the hazard extent
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.extent = hazard_layer.extent
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # the count = 63
        count = sum(impact.get_data(attribute='population'))
        self.assertEquals(int(count/1000)*1000, 1380264000)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'units': 'wetdry',
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
