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

import numpy
import unittest

from safe.storage.core import read_layer
from safe.engine.core import calculate_impact
from safe.impact_functions import get_plugin
from safe.common.testing import TESTDATA
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

            # FIXME (Ole): Should also have test for concentric circle
            #              evacuation zones

    test_volcano_population_evacuation_impact.slow = True
