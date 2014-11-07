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
    evacuated_population_needs,
    evacuated_population_weekly_needs
)


class TestCore(unittest.TestCase):
    def test_01_test_rounding(self):
        """Test for add_to_list function
        """
        #rounding up
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
        total_needs = evacuated_population_needs(
            10,
            {'Water [l]': 5, 'Rice [kg]': 0.5},
            {
                "resources": [
                    {
                        "Default": "5",
                        "Minimum allowed": "0",
                        "Maximum allowed": "100",
                        "Frequency": "weekly",
                        "Resource name": "Water",
                        "Resource description": "Water",
                        "Unit": "litre",
                        "Units": "litres",
                        "Unit abbreviation": "l",
                        "Readable sentence": "Water."
                    },
                    {
                        "Default": "0.5",
                        "Minimum allowed": "0",
                        "Maximum allowed": "100",
                        "Frequency": "daily",
                        "Resource name": "Rice",
                        "Resource description": "food",
                        "Unit": "kilogram",
                        "Units": "kilograms",
                        "Unit abbreviation": "kg",
                        "Readable sentence": "Food."
                    }
                ],
                "provenance": "Test",
                "profile": "Test"
            }
        )
        self.assertEqual(total_needs['weekly'][0]['Resource name'], 'Water')
        self.assertEqual(total_needs['weekly'][0]['Amount'], 50)
        self.assertEqual(total_needs['daily'][0]['Resource name'], 'Rice')
        self.assertEqual(total_needs['daily'][0]['Amount'], 5)

    def test_03_evacuated_population_weekly_needs(self):
        total_needs = evacuated_population_weekly_needs(
            10,
            {'Water': 5, 'Rice': 0.5})
        self.assertEqual(total_needs['Water'], 50)
        self.assertEqual(total_needs['Rice'], 5)

if __name__ == '__main__':
    unittest.main()
