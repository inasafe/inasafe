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
import os

from safe.impact_functions.core import (
    get_admissible_plugins,
    population_rounding_full,
    population_rounding,
    evacuated_population_needs
)
from safe.common.resource_parameter import ResourceParameter
from safe.common.testing import TESTDATA, HAZDATA
from safe_qgis.safe_interface import read_file_keywords


class TestCore(unittest.TestCase):
    def setUp(self):
        """Setup test before each unit"""
        self.vector_path = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        self.raster_shake_path = os.path.join(
            HAZDATA, 'Shakemap_Padang_2009.asc')

    def test_get_admissible_plugins(self):
        """Test for get_admissible_plugins function."""
        functions = get_admissible_plugins()
        message = 'No functions available (len=%ss)' % len(functions)
        self.assertTrue(len(functions) > 0, message)

        # Also test if it works when we give it two layers
        # to see if we can determine which functions will
        # work for them.
        keywords1 = read_file_keywords(self.raster_shake_path)
        keywords2 = read_file_keywords(self.vector_path)
        # We need to explicitly add the layer type to each keyword list
        keywords1['layertype'] = 'raster'
        keywords2['layertype'] = 'vector'

        functions = [keywords1, keywords2]
        functions = get_admissible_plugins(functions)
        message = 'No functions available (len=%ss)' % len(functions)
        self.assertTrue(len(functions) > 0, message)

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
