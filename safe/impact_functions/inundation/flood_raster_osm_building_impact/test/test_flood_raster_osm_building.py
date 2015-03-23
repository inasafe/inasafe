# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Flood Raster Building Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'lucernae'

import os
import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_raster_osm_building_impact\
    .impact_function import \
    FloodRasterBuildingImpactFunction
from safe.storage.core import read_layer
from safe.test.utilities import TESTDATA, get_qgis_app, HAZDATA


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodRasterBuildingImpactFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodRasterBuildingImpactFunction)

    def test_run(self):
        impact_function = FloodRasterBuildingImpactFunction.instance()

        flood_hazards = ['Flood_Current_Depth_Jakarta_geographic.asc',
                         'Flood_Design_Depth_Jakarta_geographic.asc']
        for flood_data in flood_hazards:

            building = 'OSM_building_polygons_20110905.shp'

            hazard_filename = os.path.join(HAZDATA, flood_data)
            exposure_filename = os.path.join(TESTDATA, building)

            # calculate impact
            hazard_layer = read_layer(hazard_filename)
            exposure_layer = read_layer(exposure_filename)

            impact_function.hazard = hazard_layer
            impact_function.exposure = exposure_layer
            impact_function.run()
            impact_layer = impact_function.impact


            # Extract calculated result
            icoordinates = impact_layer.get_geometry()
            iattributes = impact_layer.get_data()

            # Check
            self.assertEqual(len(icoordinates), 34960)
            self.assertEqual(len(iattributes), 34960)

    def test_filter(self):
        hazard_keywords = {
            'subcategory': 'tsunami',
            'unit': 'metres_depth',
            'layer_type': 'raster',
            'data_type': 'continuous'
        }

        exposure_keywords = {
            'subcategory': 'structure',
            'unit': 'building_type',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('FloodRasterBuildingImpactFunction',
                         retrieved_IF,
                         'Expecting FloodRasterBuildingImpactFunction.'
                         'But got %s instead' %
                         retrieved_IF)
