# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Earthquake Building IF Test Cases.**

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
from safe.common.testing import TESTDATA, HAZDATA
from safe.common.utilities import format_int


class TestEarthquakeBuildingImpactFunction(unittest.TestCase):
    """Test for EarthquakeBuildingImpactFunction."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_earthquake_building_impact_function(self):
        """Earthquake Building Impact Function works as expected."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/eq_yogya_2006.asc' % HAZDATA
        exposure_filename = '%s/OSM_building_polygons_20110905.shp' % TESTDATA

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        plugin_name = 'Earthquake Building Impact Function'
        impact_function = get_plugin(plugin_name)

        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact_layer = read_layer(impact_filename)
        # calculated_result = I.get_data()
        # print calculated_result.shape
        keywords = impact_layer.get_keywords()
        impact_summary = keywords['impact_summary']

        # This is the expected number of building might be affected
        # Hazard Level - Buildings Affected
        # Low - 845
        # Medium - 15524
        # High - 122
        message = 'Result not as expected'
        self.assertTrue(format_int(845) in impact_summary, message)
        self.assertTrue(format_int(15524) in impact_summary, message)
        self.assertTrue(format_int(122) in impact_summary, message)
