# coding=utf-8
"""Tests for core.py

InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Core**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '24/10/14'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import random
import os
import logging
from collections import OrderedDict

from safe.impact_functions.core import (
    population_rounding_full,
    population_rounding,
    evacuated_population_needs)
from safe.common.resource_parameter import ResourceParameter
from safe.defaults import default_minimum_needs
from safe.test.utilities import TESTDATA, HAZDATA

LOGGER = logging.getLogger('InaSAFE')


class TestCore(unittest.TestCase):
    def setUp(self):
        """Setup test before each unit"""
        self.vector_path = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        self.raster_shake_path = os.path.join(
            HAZDATA, 'Shakemap_Padang_2009.asc')

    def test_population_rounding(self):
        """Test for population_rounding_full function."""
        # rounding up
        for _ in range(100):
            # After choosing some random numbers the sum of the randomly
            # selected and one greater than that should be less than the
            # population rounded versions of these.
            n = random.randint(1, 1000000)
            n_pop, dummy = population_rounding_full(n)
            n1 = n + 1
            n1_pop, dummy = population_rounding_full(n1)
            self.assertGreater(n_pop + n1_pop, n + n1)

        self.assertEqual(population_rounding_full(989)[0], 990)
        self.assertEqual(population_rounding_full(991)[0], 1000)
        self.assertEqual(population_rounding_full(8888)[0], 8900)
        self.assertEqual(population_rounding_full(9888888)[0], 9889000)

        for _ in range(100):
            n = random.randint(1, 1000000)
            self.assertEqual(
                population_rounding(n),
                population_rounding_full(n)[0])

    def test_evacuated_population_needs(self):
        """Test evacuated_population_needs function."""
        water = ResourceParameter()
        water.name = 'Water'
        water.unit.name = 'litre'
        water.unit.abbreviation = 'l'
        water.unit.plural = 'litres'
        water.frequency = 'weekly'
        water.maximum_allowed_value = 10
        water.minimum_allowed_value = 0
        water.value = 5
        rice = ResourceParameter()
        rice.name = 'Rice'
        rice.unit.name = 'kilogram'
        rice.unit.abbreviation = 'kg'
        rice.unit.plural = 'kilograms'
        rice.frequency = 'daily'
        rice.maximum_allowed_value = 1
        rice.minimum_allowed_value = 0
        rice.value = 0.5
        total_needs = evacuated_population_needs(
            10,
            [water.serialize(), rice.serialize()]
        )
        self.assertEqual(total_needs['weekly'][0]['name'], 'Water')
        self.assertEqual(total_needs['weekly'][0]['amount'], 50)
        self.assertEqual(total_needs['weekly'][0]['table name'], 'Water [l]')
        self.assertEqual(total_needs['daily'][0]['name'], 'Rice')
        self.assertEqual(total_needs['daily'][0]['amount'], 5)
        self.assertEqual(total_needs['daily'][0]['table name'], 'Rice [kg]')

    def test_default_needs(self):
        """default calculated needs are as expected
        """
        minimum_needs = [
            parameter.serialize() for parameter in
            default_minimum_needs()]
        # 20 Happens to be the smallest number at which integer rounding
        # won't make a difference to the result
        result = evacuated_population_needs(20, minimum_needs)['weekly']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])

        assert (result['Rice [kg]'] == 56 and
                result['Drinking Water [l]'] == 350 and
                result['Clean Water [l]'] == 1340 and
                result['Family Kits'] == 4)

        result = evacuated_population_needs(10, minimum_needs)['single']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])
        assert result['Toilets'] == 1

    def test_arbitrary_needs(self):
        """custom need ratios calculated are as expected
        """
        minimum_needs = [
            parameter.serialize() for parameter in
            default_minimum_needs()]
        minimum_needs[0]['value'] = 4
        minimum_needs[1]['value'] = 3
        minimum_needs[2]['value'] = 2
        minimum_needs[3]['value'] = 1
        minimum_needs[4]['value'] = 0.2
        result = evacuated_population_needs(10, minimum_needs)['weekly']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])

        assert (result['Rice [kg]'] == 40 and
                result['Drinking Water [l]'] == 30 and
                result['Clean Water [l]'] == 20 and
                result['Family Kits'] == 10)
        result = evacuated_population_needs(10, minimum_needs)['single']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])
        assert result['Toilets'] == 2

if __name__ == '__main__':
    unittest.main()
