# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Flood Raster on Population Test Cases.**

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
# pylint: disable=W0611
from collections import OrderedDict
# pylint: enable=W0611

from safe.storage.core import read_layer
from safe.engine.core import calculate_impact
from safe.impact_functions import get_plugin
from safe.common.testing import TESTDATA


class FloodEvacuationFunctionVectorHazard(unittest.TestCase):
    """Test for Flood Vector on Population."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_flood_population_evacuation_polygon(self):
        """Flood population evacuation (flood is polygon)
        """
        population = 'pop_clip_flood_test.tif'
        flood_data = 'flood_poly_clip_flood_test.shp'
        plugin_name = 'FloodEvacuationFunctionVectorHazard'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)

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
        # print "keywords", keywords
        affected_population = float(keywords['affected_population'])
        total_population = keywords['total_population']

        self.assertEqual(affected_population, 134000)
        self.assertEqual(total_population, 163000)
