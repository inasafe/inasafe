# -*- coding: utf-8 -*-

import unittest
from math import sqrt

from safe.routing.core.middle import (
    distance,
    sum_distances,
    get_point,
    split_middle)


class TestMiddle(unittest.TestCase):

    def test_get_distance(self):
        self.assertEqual(distance((0, 0), (4, 0)), 4)
        self.assertEqual(distance((1, 1), (0, 0)), sqrt(2))
        self.assertEqual(distance((4, 4), (1, 1)), sqrt(18))

    def test_get_distances(self):
        l = ((0, 0), (4, 0), (4, 4), (0, 4))
        self.assertEquals(sum(sum_distances(l)), 12)

    def test_get_point(self):
        self.assertEquals(get_point((0, 0), (4, 0), 2), (2, 0))
        self.assertEquals(get_point((0, 0), (4, 0), 1), (1, 0))
        # self.assertEquals(get_point((1, 1), (4, 4), 1.5), (2.5, 2.5))

    def test_split_middle(self):
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
