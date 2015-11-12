# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest
from math import sqrt

from safe.routing.core.middle import (
    distance,
    sum_distances,
    get_point,
    split_middle)


class TestMiddle(unittest.TestCase):

    def test_get_distance(self):
        """Test the middle of a segment."""
        self.assertEqual(distance((0, 0), (4, 0)), 4)
        self.assertEqual(distance((1, 1), (0, 0)), sqrt(2))
        self.assertEqual(distance((4, 4), (1, 1)), sqrt(18))

    def test_get_distances(self):
        """Test sum length."""
        l = ((0, 0), (4, 0), (4, 4), (0, 4))
        self.assertEquals(sum(sum_distances(l)), 12)

    def test_get_point(self):
        """Test to get a point between two points with a distance."""
        self.assertEquals(get_point((0, 0), (4, 0), 2), (2, 0))
        self.assertEquals(get_point((0, 0), (4, 0), 1), (1, 0))
        # self.assertEquals(get_point((1, 1), (4, 4), 1.5), (2.5, 2.5))

    def test_split_middle(self):
        """Test to split a linestrings in the middle."""
        r = ([(0, 0), (4, 0), (4, 4)], [(4, 4), (0, 4), (0, 0)])
        l = [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]
        self.assertEquals(split_middle(l), r)

        r = ([(0, 0), (1, 1), (2, 2)], [(2, 2), (3, 3), (4, 4)])
        l = [(0, 0), (1, 1), (3, 3), (4, 4)]
        self.assertEquals(split_middle(l), r)

        l = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
        r = ([(0, 0), (1, 1), (2, 2), (2.5, 2.5)],
             [(2.5, 2.5), (3, 3), (4, 4), (5, 5)])
        self.assertEquals(split_middle(l), r)

        l = [(0, 0), (2, 2), (3, 3), (4, 4), (5, 5)]
        r = ([(0, 0), (2, 2), (2.5, 2.5)],
             [(2.5, 2.5), (3, 3), (4, 4), (5, 5)])
        self.assertEquals(split_middle(l), r)

        l = [(0, 0), (4, 0)]
        r = ([(0, 0), (2, 0)], [(2, 0), (4, 0)])
        self.assertEquals(split_middle(l), r)

if __name__ == '__main__':
    unittest.main()
