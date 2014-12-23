# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *ITB Earthquake Fatality Model Test Cases.**

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
from safe.impact_functions.core import population_rounding
from safe.common.utilities import format_int


class TestITBFatalityFunction(unittest.TestCase):
    """Test for ITBFatalityFunction."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_itb_earthquake_fatality_estimation(self):
        """Fatalities from ground shaking can be computed correctly using the
            ITB fatality model (Test data from Hadi Ghasemi)."""
        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/itb_test_mmi.asc' % TESTDATA
        exposure_filename = '%s/itb_test_pop.asc' % TESTDATA

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)

        plugin_name = 'ITB Fatality Function'
        impact_function = get_plugin(plugin_name)

        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()

        impact_layer = read_layer(impact_filename)
        # calculated_result = I.get_data()
        # print calculated_result.shape
        keywords = impact_layer.get_keywords()
        # print "keywords", keywords
        population = float(keywords['total_population'])
        fatalities = float(keywords['total_fatalities'])

        # Check aggregated values
        expected_population = population_rounding(85424650.0)
        msg = ('Expected population was %f, I got %f'
               % (expected_population, population))
        assert population == expected_population, msg

        expected_fatalities = population_rounding(40871.3028)
        msg = ('Expected fatalities was %f, I got %f'
               % (expected_fatalities, fatalities))

        assert numpy.allclose(fatalities, expected_fatalities,
                              rtol=1.0e-5), msg

        # Check that aggregated number of fatilites is as expected
        all_numbers = int(numpy.sum([31.8937368131,
                                     2539.26369372,
                                     1688.72362573,
                                     17174.9261705,
                                     19436.834531]))
        msg = ('Aggregated number of fatalities not as expected: %i'
               % all_numbers)
        assert all_numbers == 40871, msg

        x = population_rounding(all_numbers)
        msg = ('Did not find expected fatality value %i in summary %s'
               % (x, keywords['impact_summary']))
        assert format_int(x) in keywords['impact_summary'], msg
