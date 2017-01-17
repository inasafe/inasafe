# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **Numeric module test cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
import numpy

from safe.gis.numerics import axes_to_points
from safe.gis.numerics import grid_to_points


class TestNumerics(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_axes2points(self):
        """Grid axes can be converted to point coordinates for all pixels"""

        # Test 1
        x = numpy.linspace(1, 3, 3)
        y = numpy.linspace(10, 20, 2)
        P = axes_to_points(x, y)
        assert numpy.allclose(
            P,
            [[1., 20.], [2., 20.], [3., 20.], [1., 10.], [2., 10.], [3., 10.]],
            rtol=0.0,
            atol=0.0)

        # Test 2
        x = numpy.linspace(1, 5, 11)
        y = numpy.linspace(10, 20, 5)
        P = axes_to_points(x, y)
        assert numpy.allclose(P[12, :], [1.4, 17.5])

    def test_grid2points(self):
        """Raster grids can be converted to point data."""

        # Pixel values
        A = [[1, 2, 3, 4],
             [5, 6, 7, 8],
             [9, 10, 11, 12]]
        A = numpy.array(A, dtype='f')
        M, N = A.shape
        L = M * N

        # Axis
        longitudes = numpy.linspace(100, 110, N, endpoint=False)
        latitudes = numpy.linspace(-4, 0, M, endpoint=True)

        # Call function to be tested
        P, V = grid_to_points(A, longitudes, latitudes)

        # Assert correctness
        assert P.shape[0] == L
        assert P.shape[1] == 2
        assert len(V) == L

        assert numpy.allclose(P[:N, 0], longitudes)
        assert numpy.allclose(P[:L:N, 1], latitudes[::-1])
        assert numpy.allclose(V, A.flat[:])


if __name__ == '__main__':
    suite = unittest.makeSuite(TestNumerics, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
