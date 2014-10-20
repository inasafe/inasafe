__author__ = 'user'

import unittest
import random
from safe.impact_functions.core import (
    population_rounding_full,
    population_rounding
)


class TestCore(unittest.TestCase):
    def test_01_test_rounding(self):
        """Test for add_to_list function
        """
        #rounding up
        for count in range(100):
            """After choosing some random numbers the sum of the randomly
            selected and one greater than that should be less than the
            population rounded versions of these.
            """
            n = random.randint(1, 1000000)
            n_pop, dummy = population_rounding_full(n)
            n1 = n + 1
            n1_pop, dummy = population_rounding_full(n1)
            self.assertGreater(n_pop + n1_pop, n + n1)

        self.assertEqual(population_rounding_full(989)[0], 990)
        self.assertEqual(population_rounding_full(991)[0], 1000)
        self.assertEqual(population_rounding_full(8888)[0], 8900)
        self.assertEqual(population_rounding_full(9888888)[0], 9889000)

        for count in range(100):
            n = random.randint(1, 1000000)
            self.assertEqual(
                population_rounding(n),
                population_rounding_full(n)[0])


if __name__ == '__main__':
    unittest.main()
