# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Pager Earthquake Fatality Model Test Cases.**

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
from safe.test.utilities import TESTDATA


class TestITBFatalityFunction(unittest.TestCase):
    """Test for PAG Fatality Function."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_pager_earthquake_fatality_estimation(self):
        """Fatalities from ground shaking can be computed correctly
            using the Pager fatality model."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/itb_test_mmi.asc' % TESTDATA
        exposure_filename = '%s/itb_test_pop.asc' % TESTDATA

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)
        plugin_name = 'PAG Fatality Function'
        impact_function = get_plugin(plugin_name)

        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact_layer = read_layer(impact_filename)
        keywords = impact_layer.get_keywords()
        population = keywords['total_population']
        fatalities = keywords['total_fatalities']

        # Check aggregated values
        expected_population = 85425000.0
        msg = ('Expected population was %f, I got %f'
               % (expected_population, population))
        self.assertEqual(population, expected_population, msg)

        expected_fatalities = 410000.0
        msg = ('Expected fatalities was %f, I got %f'
               % (expected_fatalities, fatalities))
        assert numpy.allclose(
            fatalities, expected_fatalities, rtol=1.0e-5), msg
