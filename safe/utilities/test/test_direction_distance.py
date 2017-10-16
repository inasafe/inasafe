# coding=utf-8
"""Test Direction and Distance Calculation."""


import unittest

from safe.utilities.direction_distance import (
    bearing_to_cardinal
)


class TestDirectionDistance(unittest.TestCase):

    """Class to test direction_distance"""

    def test_cardinality(self):
        """Test getting cardinality information when an angle is given."""
        # Test using standard bearing angle
        self.assertEqual(bearing_to_cardinal(0), 'N')
        self.assertEqual(bearing_to_cardinal(22.5), 'NNE')
        self.assertEqual(bearing_to_cardinal(45), 'NE')
        self.assertEqual(bearing_to_cardinal(67.5), 'ENE')
        self.assertEqual(bearing_to_cardinal(90), 'E')
        self.assertEqual(bearing_to_cardinal(112.5), 'ESE')
        self.assertEqual(bearing_to_cardinal(135), 'SE')
        self.assertEqual(bearing_to_cardinal(157.5), 'SSE')
        self.assertEqual(bearing_to_cardinal(180), 'S')
        self.assertEqual(bearing_to_cardinal(0), 'N')
        self.assertEqual(bearing_to_cardinal(-22.5), 'NNW')
        self.assertEqual(bearing_to_cardinal(-45), 'NW')
        self.assertEqual(bearing_to_cardinal(-67.5), 'WNW')
        self.assertEqual(bearing_to_cardinal(-90), 'W')
        self.assertEqual(bearing_to_cardinal(-112.5), 'WSW')
        self.assertEqual(bearing_to_cardinal(-135), 'SW')
        self.assertEqual(bearing_to_cardinal(-157.5), 'SSW')

        # Test with non standard bearing angle
        self.assertEqual(bearing_to_cardinal(10), 'N')
        self.assertEqual(bearing_to_cardinal(20), 'N')
        self.assertEqual(bearing_to_cardinal(30), 'NNE')
        self.assertEqual(bearing_to_cardinal(40), 'NNE')
        self.assertEqual(bearing_to_cardinal(50), 'NE')
        self.assertEqual(bearing_to_cardinal(60), 'NE')
        self.assertEqual(bearing_to_cardinal(70), 'ENE')
        self.assertEqual(bearing_to_cardinal(80), 'ENE')


if __name__ == '__main__':
    unittest.main()
