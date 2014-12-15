# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Flood on Building Test Cases.**

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

from safe.storage.core import read_layer
from safe.engine.core import calculate_impact
from safe.impact_functions import get_plugin
from safe.common.testing import TESTDATA, HAZDATA


class TestFloodBuildingIF(unittest.TestCase):
    """Test for Flood Building Impact Function."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_flood_building_impact_function_vector(self):
        """Test flood building impact function works (flood is polygon)."""
        building = 'test_flood_building_impact_exposure.shp'
        flood_data = 'test_flood_building_impact_hazard.shp'
        plugin_name = 'FloodBuildingImpactFunction'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, building)

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        impact_function = get_plugin(plugin_name)

        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()
        impact_layer = read_layer(impact_filename)

        keywords = impact_layer.get_keywords()
        buildings_total = keywords['buildings_total']
        buildings_affected = keywords['buildings_affected']

        self.assertEqual(buildings_total, 67)
        self.assertEqual(buildings_affected, 41)

    def test_flood_building_impact_function(self):
        """Flood building impact function works

        This test also exercises interpolation of hazard level (raster) to
        building locations (vector data).
        """
        for haz_filename in ['Flood_Current_Depth_Jakarta_geographic.asc',
                             'Flood_Design_Depth_Jakarta_geographic.asc']:
            # Name file names for hazard level and exposure
            hazard_filename = '%s/%s' % (HAZDATA, haz_filename)
            exposure_filename = ('%s/OSM_building_polygons_20110905.shp'
                                 % TESTDATA)

            # Calculate impact using API
            hazard_layer = read_layer(hazard_filename)
            exposure_layer = read_layer(exposure_filename)

            plugin_name = 'FloodBuildingImpactFunction'
            impact_function = get_plugin(plugin_name)

            impact_vector = calculate_impact(
                layers=[hazard_layer, exposure_layer],
                impact_fcn=impact_function)

            # Extract calculated result
            icoordinates = impact_vector.get_geometry()
            iattributes = impact_vector.get_data()

            # Check
            assert len(icoordinates) == 34960
            assert len(iattributes) == 34960

            # FIXME (Ole): check more numbers

    test_flood_building_impact_function.slow = True
