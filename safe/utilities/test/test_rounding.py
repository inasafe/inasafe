# coding=utf-8

import logging
import random
import unittest

from safe.utilities.rounding import (
    population_rounding_full, population_rounding, add_separators)
from safe.utilities.i18n import locale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class TestCore(unittest.TestCase):

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

    def test_format_int(self):
        """Test formatting integer"""
        lang = locale()

        number = 10000000
        formatted_int = add_separators(number)
        if lang == 'id':
            expected_str = '10.000.000'
        else:
            expected_str = '10,000,000'
        self.assertEqual(expected_str, formatted_int)

        number = 1234
        formatted_int = add_separators(number)
        if lang == 'id':
            expected_str = '1.234'
        else:
            expected_str = '1,234'
        self.assertEqual(expected_str, formatted_int)

if __name__ == '__main__':
    unittest.main()
