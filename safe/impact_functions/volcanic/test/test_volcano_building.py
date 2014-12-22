# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Volcano on Building Test Cases.**

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
from safe.common.testing import TESTDATA
from safe.common.utilities import format_int
from safe.test.utilities import test_data_path


class TestVolcanoBuildingImpact(unittest.TestCase):
    """Test for Volcano Building Impact Function."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_volcano_building_impact(self):
        """Building impact from volcanic hazard is computed correctly."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = os.path.join(TESTDATA, 'donut.shp')
        exposure_filename = test_data_path('exposure', 'bangunan.shp')

        # Calculate impact using API
        hazard = read_layer(hazard_filename)
        exposure = read_layer(exposure_filename)

        plugin_name = 'Volcano Building Impact'
        impact_function = get_plugin(plugin_name)
        impact_function.parameters['name attribute'] = 'GUNUNG'
        print 'Calculating'
        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard, exposure], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact = read_layer(impact_filename)

        keywords = impact.get_keywords()

        # Check for expected results:
        for value in ['Merapi', 5, 86, 91, 1, 21, 22, 6, 107, 113]:
            if isinstance(value, int):
                x = format_int(value)
            else:
                x = value
            summary = keywords['impact_summary']
            message = (
                'Did not find expected value %s in summary %s' % (x, summary))
            self.assertIn(x, summary, message)
