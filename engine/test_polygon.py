#!/usr/bin/env python

import unittest
import numpy as num
from math import sqrt, pi
from numerical_tools import ensure_numeric

from polygon import *


def linear_function(x, y):
    return x + y


class Test_Polygon(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Polygon stuff
    def test_polygon_function_constants(self):
        p1 = [[0, 0], [10, 0], [10, 10], [0, 10]]
        p2 = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
              [30, 10], [40, -10]]

        f = Polygon_function([(p1, 1.0)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])    # Two first inside p1
        assert num.allclose(z, [1, 1, 0, 0])

        f = Polygon_function([(p2, 2.0)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])    # First and last inside p2
        assert num.allclose(z, [2, 0, 0, 2])

        # Combined
        f = Polygon_function([(p1, 1.0), (p2, 2.0)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 1, 0, 2])

    def Xtest_polygon_function_csvfile(self):
        from os import sep, getenv

        # Get path where this test is run
        #path = get_pathname_from_package('anuga.utilities')

        # Form absolute filename and read
        filename = path + sep + 'mainland_only.csv'
        p1 = read_polygon(filename)

        f = Polygon_function([(p1, 10.0)])
        z = f([430000, 480000], [490000, 7720000])  # 1st outside, 2nd inside

        assert num.allclose(z, [0, 10])

    def test_polygon_function_callable(self):
        """Check that values passed into Polygon_function can be callable."""

        p1 = [[0, 0], [10, 0], [10, 10], [0, 10]]
        p2 = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
              [30, 10], [40, -10]]

        f = Polygon_function([(p1, linear_function)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])  # Two first inside p1
        assert num.allclose(z, [10, 14, 0, 0])

        # Combined
        f = Polygon_function([(p1, linear_function), (p2, 2.0)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 14, 0, 2])

        # Combined w default
        f = Polygon_function([(p1, linear_function), (p2, 2.0)],
                             default=3.14)
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 14, 3.14, 2])

        # Combined w default func
        f = Polygon_function([(p1, linear_function), (p2, 2.0)],
                             default=linear_function)
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 14, 35, 2])

    def test_point_on_line(self):
        # Endpoints first
        assert point_on_line([0, 0], [[0, 0], [1, 0]])
        assert point_on_line([1, 0], [[0, 0], [1, 0]])

        # Endpoints first - non-simple
        assert point_on_line([-0.1, 0.0], [[-0.1, 0.0], [1.5, 0.6]])
        assert point_on_line([1.5, 0.6], [[-0.1, 0.0], [1.5, 0.6]])

        # Then points on line
        assert point_on_line([0.5, 0], [[0, 0], [1, 0]])
        assert point_on_line([0, 0.5], [[0, 1], [0, 0]])
        assert point_on_line([1, 0.5], [[1, 1], [1, 0]])
        assert point_on_line([0.5, 0.5], [[0, 0], [1, 1]])

        # Then points not on line
        assert not point_on_line([0.5, 0], [[0, 1], [1, 1]])
        assert not point_on_line([0, 0.5], [[0, 0], [1, 1]])

        # From real example that failed
        assert not point_on_line([40, 50], [[40, 20], [40, 40]])

        # From real example that failed
        assert not point_on_line([40, 19], [[40, 20], [40, 40]])

        # Degenerate line
        assert point_on_line([40, 19], [[40, 19], [40, 19]])
        assert not point_on_line([40, 19], [[40, 40], [40, 40]])

    def test_is_inside_polygon_main(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        assert is_inside_polygon((0.5, 0.5), polygon)
        assert not is_inside_polygon((0.5, 1.5), polygon)
        assert not is_inside_polygon((0.5, -0.5), polygon)
        assert not is_inside_polygon((-0.5, 0.5), polygon)
        assert not is_inside_polygon((1.5, 0.5), polygon)

        # Try point on borders
        assert is_inside_polygon((1., 0.5), polygon, closed=True)
        assert is_inside_polygon((0.5, 1.), polygon, closed=True)
        assert is_inside_polygon((0., 0.5), polygon, closed=True)
        assert is_inside_polygon((0.5, 0.), polygon, closed=True)

        assert not is_inside_polygon((0.5, 1.), polygon, closed=False)
        assert not is_inside_polygon((0., 0.5), polygon, closed=False)
        assert not is_inside_polygon((0.5, 0.), polygon, closed=False)
        assert not is_inside_polygon((1., 0.5), polygon, closed=False)

    def test_inside_polygon_main2(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # From real example (that failed)
        polygon = [[20, 20], [40, 20], [40, 40], [20, 40]]
        points = [[40, 50]]
        res = inside_polygon(points, polygon)
        assert len(res) == 0

        polygon = [[20, 20], [40, 20], [40, 40], [20, 40]]
        points = [[25, 25], [30, 20], [40, 50], [90, 20], [40, 90]]
        res = inside_polygon(points, polygon)
        assert len(res) == 2
        assert num.allclose(res, [0, 1])

        # More convoluted and non convex polygon
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        assert is_inside_polygon((0.5, 0.5), polygon)
        assert is_inside_polygon((1, -0.5), polygon)
        assert is_inside_polygon((1.5, 0), polygon)

        assert not is_inside_polygon((0.5, 1.5), polygon)
        assert not is_inside_polygon((0.5, -0.5), polygon)

        # Very convoluted polygon
        polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                   [30, 10], [40, -10]]
        assert is_inside_polygon((5, 5), polygon)
        assert is_inside_polygon((17, 7), polygon)
        assert is_inside_polygon((27, 2), polygon)
        assert is_inside_polygon((35, -5), polygon)
        assert not is_inside_polygon((15, 7), polygon)
        assert not is_inside_polygon((24, 3), polygon)
        assert not is_inside_polygon((25, -10), polygon)

        # Another combination (that failed)
        polygon = [[0, 0], [10, 0], [10, 10], [0, 10]]
        assert is_inside_polygon((5, 5), polygon)
        assert is_inside_polygon((7, 7), polygon)
        assert not is_inside_polygon((-17, 7), polygon)
        assert not is_inside_polygon((7, 17), polygon)
        assert not is_inside_polygon((17, 7), polygon)
        assert not is_inside_polygon((27, 8), polygon)
        assert not is_inside_polygon((35, -5), polygon)

        # Multiple polygons
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0], [10, 10],
                   [11, 10], [11, 11], [10, 11], [10, 10]]
        assert is_inside_polygon((0.5, 0.5), polygon)
        assert is_inside_polygon((10.5, 10.5), polygon)
        assert not is_inside_polygon((0, 5.5), polygon)

        # FIXME: Fails if point is 5.5, 5.5 - maybe ok, but
        # need to understand it
        #assert is_inside_polygon((5.5, 5.5), polygon)

        # Polygon with a hole
        polygon = [[-1, -1], [2, -1], [2, 2], [-1, 2], [-1, -1],
                   [0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]

        assert is_inside_polygon((0, -0.5), polygon)
        assert not is_inside_polygon((0.5, 0.5), polygon)

    def test_duplicate_points_being_ok(self):

        polygon = [[0, 0], [1, 0], [1, 0], [1, 0], [1, 1], [0, 1], [0, 0]]

        assert is_inside_polygon((0.5, 0.5), polygon)
        assert not is_inside_polygon((0.5, 1.5), polygon)
        assert not is_inside_polygon((0.5, -0.5), polygon)
        assert not is_inside_polygon((-0.5, 0.5), polygon)
        assert not is_inside_polygon((1.5, 0.5), polygon)

        # Try point on borders
        assert is_inside_polygon((1., 0.5), polygon, closed=True)
        assert is_inside_polygon((0.5, 1), polygon, closed=True)
        assert is_inside_polygon((0., 0.5), polygon, closed=True)
        assert is_inside_polygon((0.5, 0.), polygon, closed=True)

        assert not is_inside_polygon((0.5, 1), polygon, closed=False)
        assert not is_inside_polygon((0., 0.5), polygon, closed=False)
        assert not is_inside_polygon((0.5, 0.), polygon, closed=False)
        assert not is_inside_polygon((1., 0.5), polygon, closed=False)

        # From real example
        polygon = [[20, 20], [40, 20], [40, 40], [20, 40]]
        points = [[40, 50]]
        res = inside_polygon(points, polygon)
        assert len(res) == 0

    def test_inside_polygon_vector_version(self):
        # Now try the vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res = inside_polygon(points, polygon)
        assert num.allclose(res, [0, 1, 2])

    def test_outside_polygon(self):
        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # evaluate to False as the point 0.5, 0.5 is inside the unit square
        assert not is_outside_polygon([0.5, 0.5], U)

        # evaluate to True as the point 1.5, 0.5 is outside the unit square
        assert is_outside_polygon([1.5, 0.5], U)

        indices = outside_polygon([[0.5, 0.5], [1, -0.5], [0.3, 0.2]], U)
        assert num.allclose(indices, [1])

        # One more test of vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res = outside_polygon(points, polygon)
        assert num.allclose(res, [3, 4])

        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0],
                  [0.5, 1.5], [0.5, -0.5]]
        res = outside_polygon(points, polygon)

        assert num.allclose(res, [0, 4, 5])

    def test_outside_polygon2(self):
        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # evaluate to False as the point 0.5, 1.0 is inside the unit square
        assert not outside_polygon([0.5, 1.0], U, closed=True)

        # evaluate to True as the point 0.5, 1.0 is outside the unit square
        assert is_outside_polygon([0.5, 1.0], U, closed=False)

    def test_all_outside_polygon(self):
        """Test case where all points are outside poly"""

        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        points = [[2, 2], [1, 3], [-1, 1], [0, 2]]      # All outside

        indices, count = separate_points_by_polygon(points, U)
        assert count == 0                           # None inside
        assert num.allclose(indices, [3, 2, 1, 0])

        indices = outside_polygon(points, U, closed=True)
        assert num.allclose(indices, [0, 1, 2, 3])

        indices = inside_polygon(points, U, closed=True)
        assert num.allclose(indices, [])

    def test_all_inside_polygon(self):
        """Test case where all points are inside poly"""

        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        points = [[0.5, 0.5], [0.2, 0.3], [0, 0.5]]  # All inside (or on edge)

        indices, count = separate_points_by_polygon(points, U)
        assert count == 3       # All inside
        assert num.allclose(indices, [0, 1, 2])

        indices = outside_polygon(points, U, closed=True)
        assert num.allclose(indices, [])

        indices = inside_polygon(points, U, closed=True)
        assert num.allclose(indices, [0, 1, 2])

    def test_separate_points_by_polygon(self):
        # Unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        indices, count = separate_points_by_polygon([[0.5, 0.5],
                                                     [1, -0.5],
                                                     [0.3, 0.2]], U)
        assert num.allclose(indices, [0, 2, 1])
        assert count == 2

        # One more test of vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res, count = separate_points_by_polygon(points, polygon)

        assert num.allclose(res, [0, 1, 2, 4, 3])
        assert count == 3

        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0],
                  [0.5, 1.5], [0.5, -0.5]]
        res, count = separate_points_by_polygon(points, polygon)

        assert num.allclose(res, [1, 2, 3, 5, 4, 0])
        assert count == 3

    def test_populate_polygon(self):
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]
        points = populate_polygon(polygon, 5)

        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)

        # Very convoluted polygon
        polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                   [30, 10], [40, -10]]
        points = populate_polygon(polygon, 5)
        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)

    def test_populate_polygon_with_exclude(self):
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]
        ex_poly = [[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]]     # SW quarter
        points = populate_polygon(polygon, 5, exclude=[ex_poly])

        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly)

        # Overlap
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]
        ex_poly = [[-1, -1], [0.5, 0], [0.5, 0.5], [-1, 0.5]]
        points = populate_polygon(polygon, 5, exclude=[ex_poly])

        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly)

        # Multiple
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]
        ex_poly1 = [[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]]  # SW quarter
        ex_poly2 = [[0.5, 0.5], [0.5, 1], [1, 1], [1, 0.5]]  # NE quarter

        points = populate_polygon(polygon, 20, exclude=[ex_poly1, ex_poly2])

        assert len(points) == 20
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly1)
            assert not is_inside_polygon(point, ex_poly2)

        # Very convoluted polygon
        polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                   [30, 10], [40, -10]]
        ex_poly = [[-1, -1], [5, 0], [5, 5], [-1, 5]]
        points = populate_polygon(polygon, 20, exclude=[ex_poly])

        assert len(points) == 20
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly), '%s' % str(point)

    def test_populate_polygon_with_exclude2(self):

        M = 200  # Number of points
        min_outer = 0
        max_outer = 1000
        polygon_outer = [[min_outer, min_outer], [max_outer, min_outer],
                         [max_outer, max_outer], [min_outer, max_outer]]

        delta = 10
        min_inner1 = min_outer + delta
        max_inner1 = max_outer - delta
        inner1_polygon = [[min_inner1, min_inner1], [max_inner1, min_inner1],
                          [max_inner1, max_inner1], [min_inner1, max_inner1]]

        min_inner2 = min_outer + 2 * delta
        max_inner2 = max_outer - 2 * delta
        inner2_polygon = [[min_inner2, min_inner2], [max_inner2, min_inner2],
                          [max_inner2, max_inner2], [min_inner2, max_inner2]]

        points = populate_polygon(polygon_outer, M,
                                  exclude=[inner1_polygon, inner2_polygon])

        assert len(points) == M
        for point in points:
            assert is_inside_polygon(point, polygon_outer)
            assert not is_inside_polygon(point, inner1_polygon)
            assert not is_inside_polygon(point, inner2_polygon)

        # Very convoluted polygon
        polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                   [30, 10], [40, -10]]
        ex_poly = [[-1, -1], [5, 0], [5, 5], [-1, 5]]
        points = populate_polygon(polygon, M, exclude=[ex_poly])

        assert len(points) == M
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly), '%s' % str(point)

    def test_large_example(self):
        """Large polygon clipping example works
        """

        M = 500  # Number of points inside
        N = 300  # Number of points outside

        # Main box
        min_main = 0
        max_main = 100
        main_polygon = [[min_main, min_main], [max_main, min_main],
                        [max_main, max_main], [min_main, max_main]]

        # Outer box
        delta = 10
        min_outer = min_main - delta
        max_outer = max_main + delta
        outer_polygon = [[min_outer, min_outer], [max_outer, min_outer],
                         [max_outer, max_outer], [min_outer, max_outer]]

        # Create points inside and outside main polygon
        points_inside = populate_polygon(main_polygon, M)
        points_outside = populate_polygon(outer_polygon, N,
                                          exclude=[main_polygon])

        assert len(points_inside) == M
        for point in points_inside:
            assert is_inside_polygon(point, main_polygon)

        assert len(points_outside) == N
        for point in points_outside:
            assert not is_inside_polygon(point, main_polygon)

        # Test separation algorithm
        all_points = num.concatenate((points_inside, points_outside))
        assert all_points.shape[0] == M + N

        indices, count = separate_points_by_polygon(all_points, main_polygon)
        msg = 'Expected %i points inside, got %i' % (M, count)
        assert count == M, msg

        msg = 'Expected %i indices, got %i' % (M + N, len(indices))
        assert len(indices) == M + N, msg

        for point in all_points[indices[:count]]:
            assert is_inside_polygon(point, main_polygon)

        for point in all_points[indices[count:]]:
            assert not is_inside_polygon(point, main_polygon)

    def test_large_convoluted_example(self):
        """Large convoluted polygon clipping example works
        """

        M = 500  # Number of points inside
        N = 300  # Number of points outside

        # Main box
        main_polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                        [30, 10], [40, -10]]
        main_polygon = ensure_numeric(main_polygon)

        # Outer box
        delta = 5
        x_min = min(main_polygon[:, 0]) - delta
        x_max = max(main_polygon[:, 0]) + delta
        y_min = min(main_polygon[:, 1]) - delta
        y_max = max(main_polygon[:, 1]) + delta

        outer_polygon = [[x_min, y_min], [x_max, y_min],
                         [x_max, y_max], [x_min, y_max]]

        # Create points inside and outside main polygon
        points_inside = populate_polygon(main_polygon, M)
        points_outside = populate_polygon(outer_polygon, N,
                                          exclude=[main_polygon])

        assert len(points_inside) == M
        for point in points_inside:
            assert is_inside_polygon(point, main_polygon)

        assert len(points_outside) == N
        for point in points_outside:
            assert not is_inside_polygon(point, main_polygon)

        # Test separation algorithm
        all_points = num.concatenate((points_inside, points_outside))
        assert all_points.shape[0] == M + N

        indices, count = separate_points_by_polygon(all_points, main_polygon)
        msg = 'Expected %i points inside, got %i' % (M, count)
        assert count == M, msg

        msg = 'Expected %i indices, got %i' % (M + N, len(indices))
        assert len(indices) == M + N, msg

        for point in all_points[indices[:count]]:
            assert is_inside_polygon(point, main_polygon)

        for point in all_points[indices[count:]]:
            assert not is_inside_polygon(point, main_polygon)

    def test_large_convoluted_example_random(self):
        """Large convoluted polygon clipping example works (random points)
        """

        M = 1000  # Number of points

        # Main box
        main_polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                        [30, 10], [40, -10]]
        main_polygon = ensure_numeric(main_polygon)

        # Outer box
        delta = 5
        x_min = min(main_polygon[:, 0]) - delta
        x_max = max(main_polygon[:, 0]) + delta
        y_min = min(main_polygon[:, 1]) - delta
        y_max = max(main_polygon[:, 1]) + delta

        outer_polygon = [[x_min, y_min], [x_max, y_min],
                         [x_max, y_max], [x_min, y_max]]

        # Create points inside and outside main polygon
        all_points = populate_polygon(outer_polygon, M, seed=17)
        assert len(all_points) == M
        all_points = ensure_numeric(all_points)

        # Test separation algorithm
        indices, count = separate_points_by_polygon(all_points, main_polygon)

        msg = 'Expected %i points inside, got %i' % (271, count)
        assert count == 271, msg

        msg = 'Expected %i indices, got %i' % (M, len(indices))
        assert len(indices) == M, msg

        for point in all_points[indices[:count]]:
            assert is_inside_polygon(point, main_polygon)

        for point in all_points[indices[count:]]:
            assert not is_inside_polygon(point, main_polygon)

    def test_in_and_outside_polygon_main(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        inside, outside = in_and_outside_polygon((0.5, 0.5), polygon)
        assert inside[0] == 0
        assert len(outside) == 0

        inside, outside = in_and_outside_polygon((1., 0.5), polygon,
                                                 closed=True)
        assert inside[0] == 0
        assert len(outside) == 0

        inside, outside = in_and_outside_polygon((1., 0.5), polygon,
                                                 closed=False)
        assert len(inside) == 0
        assert outside[0] == 0

        points = [(1., 0.25), (1., 0.75)]
        inside, outside = in_and_outside_polygon(points, polygon, closed=True)
        assert num.alltrue(inside == [0, 1])
        assert len(outside) == 0

        inside, outside = in_and_outside_polygon(points, polygon, closed=False)
        assert len(inside) == 0
        assert num.alltrue(outside == [0, 1])

        points = [(100., 0.25), (0.5, 0.5)]
        inside, outside = in_and_outside_polygon(points, polygon)
        assert num.alltrue(inside == [1])
        assert outside[0] == 0

        points = [(100., 0.25), (0.5, 0.5), (39, 20),
                  (0.6, 0.7), (56, 43), (67, 90)]
        inside, outside = in_and_outside_polygon(points, polygon)
        assert num.alltrue(inside == [1, 3])
        assert num.alltrue(outside == [0, 2, 4, 5])

    def test_intersection1(self):
        line0 = [[-1, 0], [1, 0]]
        line1 = [[0, -1], [0, 1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [0.0, 0.0])

    def test_intersection2(self):
        line0 = [[0, 0], [24, 12]]
        line1 = [[0, 12], [24, 0]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [12.0, 6.0])

        # Swap direction of one line
        line1 = [[24, 0], [0, 12]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [12.0, 6.0])

        # Swap order of lines
        status, value = intersection(line1, line0)
        assert status == 1
        assert num.allclose(value, [12.0, 6.0])

    def test_intersection3(self):
        line0 = [[0, 0], [24, 12]]
        line1 = [[0, 17], [24, 0]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [14.068965517, 7.0344827586])

        # Swap direction of one line
        line1 = [[24, 0], [0, 17]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [14.068965517, 7.0344827586])

        # Swap order of lines
        status, value = intersection(line1, line0)
        assert status == 1
        assert num.allclose(value, [14.068965517, 7.0344827586])

    def test_intersection_endpoints(self):
        """test_intersection_endpoints(self):

        Test that coinciding endpoints are picked up
        """

        line0 = [[0, 0], [1, 1]]
        line1 = [[1, 1], [2, 1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [1.0, 1.0])

        line0 = [[1, 1], [2, 0]]
        line1 = [[1, 1], [2, 1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [1.0, 1.0])

    # This function is a helper function for
    # the test_intersection_bug_20081110_?() set of tests.
    # This function tests all parallel line cases for 4 collinear points.
    # This function should never be run directly by the unittest code.
    def helper_parallel_intersection_code(self, P1, P2, P3, P4):
        # lines in same direction, no overlap
        # 0:         ---->----
        # 1:                     --------->-----------
        line0 = [P1, P2]
        line1 = [P3, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 3,
                    'Expected status 3, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(value is None,
                        'Expected value of None, got %s' % str(value))

        # lines in same direction, no overlap
        # 0:         ----<----
        # 1:                     ---------<-----------
        line0 = [P2, P1]
        line1 = [P4, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 3,
                    'Expected status 3, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(value is None,
                        'Expected value of None, got %s' % str(value))

        # lines in opposite direction, no overlap
        # 0:         ----<----
        # 1:                     --------->-----------
        line0 = [P2, P1]
        line1 = [P3, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 3,
                    'Expected status 3, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(value is None,
                        'Expected value of None, got %s' % str(value))

        # lines in opposite direction, no overlap
        # 0:         ---->----
        # 1:                     ---------<-----------
        line0 = [P1, P2]
        line1 = [P4, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 3,
                    'Expected status 3, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(value is None,
                        'Expected value of None, got %s' % str(value))

        # ---------------------------------------------------------------

        # line0 fully within line1, same direction
        # 0:         ---->----
        # 1:    --------->-----------
        # value should be line0:
        #            ---->----
        line0 = [P2, P3]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line0 fully within line1, same direction
        # 0:         ----<----
        # 1:    ---------<-----------
        # value should be line0:
        #            ----<----
        line0 = [P3, P2]
        line1 = [P4, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line0 fully within line1, opposite direction
        # 0:         ----<----
        # 1:    --------->-----------
        # value should be line0:
        #            ----<----
        line0 = [P3, P2]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line0 fully within line1, opposite direction
        # 0:         ---->----
        # 1:    ---------<-----------
        # value should be line0:
        #            ---->----
        line0 = [P2, P3]
        line1 = [P4, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # --------------------------------------------------------------
        # line1 fully within line0, same direction
        # 0:    --------->-----------
        # 1:         ---->----
        # value should be line1:
        #            ---->----
        line0 = [P1, P4]
        line1 = [P2, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line1 fully within line0, same direction
        # 0:    ---------<-----------
        # 1:         ----<----
        # value should be line1:
        #            ----<----
        line0 = [P4, P1]
        line1 = [P3, P2]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line1 fully within line0, opposite direction
        # 0:    ---------<-----------
        # 1:         ---->----
        # value should be line1:
        #            ---->----
        line0 = [P4, P1]
        line1 = [P2, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line1 fully within line0, opposite direction
        # 0:    --------->-----------
        # 1:         ----<----
        # value should be line1:
        #            ----<----
        line0 = [P1, P4]
        line1 = [P3, P2]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # ----------------------------------------------------------------
        # line in same direction, partial overlap
        # 0:    ----->-----
        # 1:       ------->--------
        # value should be segment line1_start->line0_end:
        #          --->----
        line0 = [P1, P3]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[0], line0[1]]))

        # line in same direction, partial overlap
        # 0:    -----<-----
        # 1:       -------<--------
        # value should be segment line0_start->line1_end:
        #          ---<----
        line0 = [P3, P1]
        line1 = [P4, P2]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0], line1[1]]))

        # line in opposite direction, partial overlap
        # 0:    -----<-----
        # 1:       ------->--------
        # value should be segment line0_start->line1_start:
        #          ---<----
        line0 = [P3, P1]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0], line1[0]]))

        # line in opposite direction, partial overlap
        # 0:    ----->-----
        # 1:       -------<--------
        # value should be segment line1_end->line0_end:
        #          --->----
        line0 = [P1, P3]
        line1 = [P4, P2]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[1], line0[1]]))

        # -------------------------------------------------------------------
        # line in same direction, partial overlap
        # 0:       ------>------
        # 1:    ------>------
        # value should be segment line0_start->line1_end:
        #          --->----
        line0 = [P2, P4]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0], line1[1]]))

        # line in same direction, partial overlap
        # 0:       ------<------
        # 1:    ------<------
        # value should be segment line1_start->line0_end:
        #          ----<-----
        line0 = [P4, P2]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[0], line0[1]]))

        # line in opposite direction, partial overlap
        # 0:       ------<------
        # 1:    ----->------
        # value should be segment line1_end->line0_end:
        #          --->----
        line0 = [P4, P2]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[1], line0[1]]))

        # line in opposite direction, partial overlap
        # 0:       ------>------
        # 1:    -----<------
        # value should be segment line0_start->line1_start:
        #          ---<----
        line0 = [P2, P4]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0], line1[0]]))

        # --------------------------------------------------------------------
        # line in same direction, same left point, line1 longer
        # 0:    ----->------
        # 1:    ------->--------
        # value should be line0:
        #       ----->------
        line0 = [P1, P3]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in same direction, same left point, line1 longer
        # 0:    -----<------
        # 1:    -------<--------
        # value should be line0:
        #       -----<------
        line0 = [P3, P1]
        line1 = [P4, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in opposite direction, same left point, line1 longer
        # 0:    ----->------
        # 1:    -------<--------
        # value should be line0:
        #       ----->------
        line0 = [P1, P3]
        line1 = [P4, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in opposite direction, same start point, line1 longer
        # 0:    -----<------
        # 1:    ------->--------
        # value should be line0:
        #       -----<------
        line0 = [P3, P1]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # -------------------------------------------------------------------
        # line in same direction, same left point, same right point
        # 0:    ------->--------
        # 1:    ------->--------
        # value should be line0 or line1:
        #       ------->--------
        line0 = [P1, P3]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in same direction, same left point, same right point
        # 0:    -------<--------
        # 1:    -------<--------
        # value should be line0 (or line1):
        #       -------<--------
        line0 = [P3, P1]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in opposite direction, same left point, same right point
        # 0:    ------->--------
        # 1:    -------<--------
        # value should be line0:
        #       ------->--------
        line0 = [P1, P3]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in opposite direction, same left point, same right point
        # 0:    -------<--------
        # 1:    ------->--------
        # value should be line0:
        #       -------<--------
        line0 = [P3, P1]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # -------------------------------------------------------------------
        # line in same direction, same right point, line1 longer
        # 0:        ----->------
        # 1:    ------->--------
        # value should be line0:
        #           ----->------
        line0 = [P2, P4]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in same direction, same right point, line1 longer
        # 0:        -----<------
        # 1:    -------<--------
        # value should be line0:
        #           -----<------
        line0 = [P4, P2]
        line1 = [P4, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in opposite direction, same right point, line1 longer
        # 0:        ----->------
        # 1:    -------<--------
        # value should be line0:
        #           ----->------
        line0 = [P2, P4]
        line1 = [P4, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # line in opposite direction, same right point, line1 longer
        # 0:        -----<------
        # 1:    ------->--------
        # value should be line0:
        #           -----<------
        line0 = [P4, P2]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # -------------------------------------------------------------------
        # line in same direction, same left point, line0 longer
        # 0:    ------->--------
        # 1:    ----->------
        # value should be line1:
        #       ----->------
        line0 = [P1, P4]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line in same direction, same left point, line0 longer
        # 0:    -------<--------
        # 1:    -----<------
        # value should be line1:
        #       -----<------
        line0 = [P4, P1]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line in opposite direction, same left point, line0 longer
        # 0:    ------->--------
        # 1:    -----<------
        # value should be line1:
        #       -----<------
        line0 = [P1, P4]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line in opposite direction, same left point, line0 longer
        # 0:    -------<--------
        # 1:    ----->------
        # value should be line1:
        #       ----->------
        line0 = [P4, P1]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # -------------------------------------------------------------------
        # line in same direction, same right point, line0 longer
        # 0:    ------->--------
        # 1:        ----->------
        # value should be line1:
        #           ----->------
        line0 = [P1, P4]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line in same direction, same right point, line0 longer
        # 0:    -------<--------
        # 1:        -----<------
        # value should be line1:
        #           -----<------
        line0 = [P4, P1]
        line1 = [P4, P2]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line in opposite direction, same right point, line0 longer
        # 0:    ------->--------
        # 1:        -----<------
        # value should be line1:
        #           -----<------
        line0 = [P1, P4]
        line1 = [P4, P2]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # line in opposite direction, same right point, line0 longer
        # 0:    -------<--------
        # 1:        ----->------
        # value should be line1:
        #           ----->------
        line0 = [P4, P1]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status != 2,
                    'Expected status 2, got status=%s, value=%s' %
                    (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

    def test_intersection_bug_20081110_TR(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right quadrant
        """

        # define 4 collinear points in top-right quadrant
        #    P1---P2---P3---P4
        P1 = [1.0, 1.0]
        P2 = [2.0, 2.0]
        P3 = [3.0, 3.0]
        P4 = [4.0, 4.0]

        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, 1.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, 1.0]
        P2 = [2.0, 2.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [2.0, 2.0]
        P3 = [3.0, 3.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [3.0, 3.0]
        P4 = [4.0, 4.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TL(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-left quadrant
        """

        # define 4 collinear points in top-left quadrant
        #    P1---P2---P3---P4
        P1 = [-1.0, 1.0]
        P2 = [-2.0, 2.0]
        P3 = [-3.0, 3.0]
        P4 = [-4.0, 4.0]

        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, 1.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, 1.0]
        P2 = [-2.0, 2.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [-2.0, 2.0]
        P3 = [-3.0, 3.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [-3.0, 3.0]
        P4 = [-4.0, 4.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_BL(self):
        """test_intersection_bug_20081110(self)

        Test all cases in bottom-left quadrant
        """

        # define 4 collinear points in bottom-left quadrant
        #    P1---P2---P3---P4
        P1 = [-1.0, -1.0]
        P2 = [-2.0, -2.0]
        P3 = [-3.0, -3.0]
        P4 = [-4.0, -4.0]

        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, -1.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, -1.0]
        P2 = [-2.0, -2.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [-2.0, -2.0]
        P3 = [-3.0, -3.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [-3.0, -3.0]
        P4 = [-4.0, -4.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_BR(self):
        """test_intersection_bug_20081110(self)

        Test all cases in bottom-right quadrant
        """

        # define 4 collinear points in bottom-right quadrant
        #    P1---P2---P3---P4
        P1 = [1.0, -1.0]
        P2 = [2.0, -2.0]
        P3 = [3.0, -3.0]
        P4 = [4.0, -4.0]

        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, -1.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, -1.0]
        P2 = [2.0, -2.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [2.0, -2.0]
        P3 = [3.0, -3.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [3.0, -3.0]
        P4 = [4.0, -4.0 + 1.0e-9]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TR_TL(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right & top-left quadrant
        """

        # define 4 collinear points, 1 in TL, 3 in TR
        #    P1-+-P2---P3---P4
        P1 = [-3.0, 1.0]
        P2 = [1.0, 5.0]
        P3 = [2.0, 6.0]
        P4 = [3.0, 7.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 2 in TL, 2 in TR
        #    P1---P2-+-P3---P4
        P1 = [-3.0, 1.0]
        P2 = [-2.0, 2.0]
        P3 = [2.0, 6.0]
        P4 = [3.0, 7.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 3 in TL, 1 in TR
        #    P1---P2---P3-+-P4
        P1 = [-3.0, 1.0]
        P2 = [-2.0, 2.0]
        P3 = [-1.0, 3.0]
        P4 = [3.0, 7.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TR_BL(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right & bottom-left quadrant
        """

        # define 4 collinear points, 1 in BL, 3 in TR
        #    P1-+-P2---P3---P4
        P1 = [-4.0, -3.0]
        P2 = [1.0, 2.0]
        P3 = [2.0, 3.0]
        P4 = [3.0, 4.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 2 in TL, 2 in TR
        #    P1---P2-+-P3---P4
        P1 = [-4.0, -3.0]
        P2 = [-3.0, -2.0]
        P3 = [2.0, 3.0]
        P4 = [3.0, 4.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 3 in TL, 1 in TR
        #    P1---P2---P3-+-P4
        P1 = [-4.0, -3.0]
        P2 = [-3.0, -2.0]
        P3 = [-2.0, -1.0]
        P4 = [3.0, 4.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TR_BR(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right & bottom-right quadrant
        """

        # define 4 collinear points, 1 in BR, 3 in TR
        #    P1-+-P2---P3---P4
        P1 = [1.0, -3.0]
        P2 = [5.0, 1.0]
        P3 = [6.0, 2.0]
        P4 = [7.0, 3.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 2 in BR, 2 in TR
        #    P1---P2-+-P3---P4
        P1 = [1.0, -3.0]
        P2 = [2.0, -2.0]
        P3 = [6.0, 2.0]
        P4 = [7.0, 3.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 3 in BR, 1 in TR
        #    P1---P2---P3-+-P4
        P1 = [1.0, -3.0]
        P2 = [2.0, -2.0]
        P3 = [3.0, -1.0]
        P4 = [7.0, 3.0]
        self.helper_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_direction_invariance(self):
        """This runs through a number of examples and checks that
        direction of lines don't matter.
        """

        line0 = [[0, 0], [100, 100]]

        common_end_point = [20, 150]

        for i in range(100):
            x = 20 + i * 1.0 / 100

            line1 = [[x, 0], common_end_point]
            status, p1 = intersection(line0, line1)
            assert status == 1

            # Swap direction of line1
            line1 = [common_end_point, [x, 0]]
            status, p2 = intersection(line0, line1)
            assert status == 1

            msg = ('Orientation of line should not matter.\n'
                   'However, segment [%f,%f], [%f, %f]' %
                   (x, 0, common_end_point[0], common_end_point[1]))
            msg += ' gave %s, \nbut when reversed we got %s' % (p1, p2)
            assert num.allclose(p1, p2), msg

            # Swap order of lines
            status, p3 = intersection(line1, line0)
            assert status == 1
            msg = 'Order of lines gave different results'
            assert num.allclose(p1, p3), msg

    def test_no_intersection(self):
        line0 = [[-1, 1], [1, 1]]
        line1 = [[0, -1], [0, 0]]

        status, value = intersection(line0, line1)
        assert status == 0
        assert value is None

    def test_intersection_parallel(self):
        line0 = [[-1, 1], [1, 1]]
        line1 = [[-1, 0], [5, 0]]

        status, value = intersection(line0, line1)
        assert status == 4
        assert value is None

        line0 = [[0, 0], [10, 100]]
        line1 = [[-10, 5], [0, 105]]

        status, value = intersection(line0, line1)
        assert status == 4
        assert value is None

    def test_intersection_coincide(self):
        """Test what happens when two lines partly coincide"""

        # Overlap 1
        line0 = [[0, 0], [5, 0]]
        line1 = [[-3, 0], [3, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[0, 0], [3, 0]])

        # Overlap 2
        line0 = [[-10, 0], [5, 0]]
        line1 = [[-3, 0], [10, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[-3, 0], [5, 0]])

        # Inclusion 1
        line0 = [[0, 0], [5, 0]]
        line1 = [[2, 0], [3, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, line1)

        # Inclusion 2
        line0 = [[1, 0], [5, 0]]
        line1 = [[-10, 0], [15, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, line0)

        # Exclusion (no intersection)
        line0 = [[-10, 0], [1, 0]]
        line1 = [[3, 0], [15, 0]]

        status, value = intersection(line0, line1)
        assert status == 3
        assert value is None

        # Try examples with some slope (y=2*x+5)

        # Overlap
        line0 = [[0, 5], [7, 19]]
        line1 = [[1, 7], [10, 25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        status, value = intersection(line1, line0)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        # Swap direction
        line0 = [[7, 19], [0, 5]]
        line1 = [[1, 7], [10, 25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[7, 19], [1, 7]])

        line0 = [[0, 5], [7, 19]]
        line1 = [[10, 25], [1, 7]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        # Inclusion
        line0 = [[1, 7], [7, 19]]
        line1 = [[0, 5], [10, 25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        line0 = [[0, 5], [10, 25]]
        line1 = [[1, 7], [7, 19]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        line0 = [[0, 5], [10, 25]]
        line1 = [[7, 19], [1, 7]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[7, 19], [1, 7]])

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Polygon, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
