# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *VolcanoPolygonHazardPopulation Impact Function Test Cases.*

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'akbargumbira@gmail.com'
__date__ = '12/12/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.storage.core import read_layer
from safe.engine.core import calculate_impact
from safe.impact_functions import get_plugin
from safe.test.utilities import TESTDATA, EXPDATA
from safe.impact_functions.core import population_rounding
from safe.common.utilities import format_int


class TestVolcanoPolygonHazardPopulationFunction(unittest.TestCase):
    """Test for VolcanoPolygonHazardPopulation Impact Function."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_volcano_population_evacuation_impact(self):
        """Population impact from volcanic hazard is computed correctly."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/donut.shp' % TESTDATA
        exposure_filename = ('%s/pop_merapi_clip.tif' % TESTDATA)

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        plugin_name = 'Volcano Polygon Hazard Population'
        impact_function = get_plugin(plugin_name)

        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact_layer = read_layer(impact_filename)

        keywords = impact_layer.get_keywords()

        # Check for expected results:
        for value in ['Merapi', 192055, 56514, 68568, 66971]:
            if isinstance(value, int):
                x = format_int(population_rounding(value))
            else:
                x = value
            summary = keywords['impact_summary']
            msg = ('Did not find expected value %s in summary %s'
                   % (x, summary))
            assert x in summary, msg

    test_volcano_population_evacuation_impact.slow = True

    def test_volcano_circle_population_impact(self):
        """Volcano function runs circular evacuation zone."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/Merapi_alert.shp' % TESTDATA
        exposure_filename = ('%s/glp10ag.asc' % EXPDATA)

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        plugin_name = 'Volcano Polygon Hazard Population'
        impact_function = get_plugin(plugin_name)

        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact_layer = read_layer(impact_filename)
        keywords = impact_layer.get_keywords()
        print keywords
        # This is the expected number of people affected
        # Distance [km]	Total	Cumulative
        # 3	     15.800	15.800
        # 5	     17.300	33.100
        # 10	125.000	158.000
        message = 'Result not as expected'
        impact_summary = keywords['impact_summary']
        self.assertTrue(format_int(15800) in impact_summary, message)
        self.assertTrue(format_int(17300) in impact_summary, message)
        self.assertTrue(format_int(125000) in impact_summary, message)
