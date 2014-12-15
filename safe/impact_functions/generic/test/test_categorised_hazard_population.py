# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Categorised Hazard Population Impact Function Test Cases.**

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


class TestCategorisedHazardPopulationImpactFunction(unittest.TestCase):
    """Test for CategorisedHazardPopulationImpactFunction."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_categorised_hazard_population_impact_function(self):
        """Categorised Hazard Population IF works as expected."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/jakarta_flood_category_123.asc' % HAZDATA
        exposure_filename = '%s/Population_Jakarta_geographic.asc' % TESTDATA

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        plugin_name = 'Categorised Hazard Population Impact Function'
        impact_function = get_plugin(plugin_name)

        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact_layer = read_layer(impact_filename)
        keywords = impact_layer.get_keywords()
        impact_summary = keywords['impact_summary']

        # This is the expected number
        # FIXME Akbar: This number does not make sense, pls check manually
        # the exposure data or there's something wrong with the IF
        # Total Population Affected - 99,219,000
        # Population in High risk areas - 38,940,000
        # Population in Medium risk areas - 29,341,000
        # Population in Low risk areas - 30,939,000
        # Population Not Affected - 256,770,000
        message = 'Result not as expected'
        self.assertTrue(format_int(99219000) in impact_summary, message)
        self.assertTrue(format_int(38940000) in impact_summary, message)
        self.assertTrue(format_int(29341000) in impact_summary, message)
        self.assertTrue(format_int(30939000) in impact_summary, message)
        self.assertTrue(format_int(256770000) in impact_summary, message)
