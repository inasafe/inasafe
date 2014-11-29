# coding=utf-8
"""Tests for core.py

InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Metadata**

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
from safe.impact_functions.core import (
    population_rounding_full,
    population_rounding,
    evacuated_population_needs
)
from safe_extras.parameters.resource_parameter import ResourceParameter


class TestCore(unittest.TestCase):
    def test_01_test_rounding(self):
        """Test for add_to_list function
        """
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

    def test_02_evacuated_population_needs(self):
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

if __name__ == '__main__':
    unittest.main()
