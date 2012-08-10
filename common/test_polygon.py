import unittest
import numpy
import sys
import os

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from math import sqrt, pi

from storage.vector import Vector

from polygon import *
from testing import test_polygon, test_lines
from numerics import ensure_numeric


def linear_function(x, y):
    return x + y


class Test_Polygon(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Polygon stuff
    def test_point_on_line(self):
        """Points coinciding with lines are correctly detected
        """

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

    def test_point_on_line_vector(self):
        """Points coinciding with lines are correctly detected (vector version)

        Vectorised version
        """

        # Common variables
        N = 100
        x0 = 0
        x1 = 50
        x0in = x0 + 5
        x1in = x1 - 5
        space = numpy.linspace(x0, x1, num=N, endpoint=True)

        # First a couple where all points are included
        h_points = numpy.zeros((N, 2), numpy.float64)
        h_points[:, 0] = space
        horiz_line = [[x0, 0], [x1, 0]]
        res = point_on_line(h_points, horiz_line)
        assert numpy.alltrue(res)

        v_points = numpy.zeros((N, 2), numpy.float64)
        v_points[:, 1] = space
        vertical_line = [[0, x0], [0, x1]]
        res = point_on_line(v_points, vertical_line)
        assert numpy.alltrue(res)

        # Then some where points are outside
        horiz_line = [[x0in, 0], [x1in, 0]]
        res = point_on_line(h_points, horiz_line)
        assert numpy.sometrue(res)
        ref = (x0in < h_points[:, 0]) * (h_points[:, 0] < x1in)
        assert numpy.alltrue(res == ref)

        vertical_line = [[0, x0in], [0, x1in]]
        res = point_on_line(v_points, vertical_line)
        ref = (x0in < v_points[:, 1]) * (v_points[:, 1] < x1in)
        assert numpy.alltrue(res == ref)

        # Diagonal example - all in
        diagonal_line = [[x0, x0], [x1, x1]]
        d_points = numpy.zeros((N, 2), numpy.float64)
        d_points[:, 0] = space
        d_points[:, 1] = space
        res = point_on_line(d_points, diagonal_line)
        assert numpy.alltrue(res)

        # Example with all out - all False
        res = point_on_line(d_points, vertical_line)
        assert not numpy.sometrue(res)

        # Then a more realistic example, diagonal with points outside
        points = numpy.concatenate((d_points, [[31, 12], [0, 3]]))
        res = point_on_line(points, diagonal_line)
        assert numpy.alltrue(res[:N])
        assert not numpy.sometrue(res[N:])

    def test_is_inside_polygon_main1(self):
        """Points are classified as either inside polygon or not
        """

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
        """Points can be classified as either inside or outside polygon (2)
        """

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
        assert numpy.allclose(res, [0, 1])

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
        """Polygons can have duplicate points without problems
        """

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
        """Indices of points inside polygon are correct
        """

        # Now try the vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res = inside_polygon(points, polygon)
        assert numpy.allclose(res, [0, 1, 2])

    def test_outside_polygon(self):
        """Points are classified as either outside polygon or not
        """

        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # evaluate to False as the point 0.5, 0.5 is inside the unit square
        assert not is_outside_polygon([0.5, 0.5], U)

        # evaluate to True as the point 1.5, 0.5 is outside the unit square
        assert is_outside_polygon([1.5, 0.5], U)

        indices = outside_polygon([[0.5, 0.5], [1, -0.5], [0.3, 0.2]], U)
        assert numpy.allclose(indices, [1])

        # One more test of vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res = outside_polygon(points, polygon)
        assert numpy.allclose(res, [3, 4])

        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0],
                  [0.5, 1.5], [0.5, -0.5]]
        res = outside_polygon(points, polygon)

        assert numpy.allclose(res, [0, 4, 5])

    def test_outside_polygon2(self):
        """Points are classified as either outside polygon or not (2)
        """

        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # evaluate to False as the point 0.5, 1.0 is inside the unit square
        assert not outside_polygon([0.5, 1.0], U, closed=True)

        # evaluate to True as the point 0.5, 1.0 is outside the unit square
        assert is_outside_polygon([0.5, 1.0], U, closed=False)

    def test_all_outside_polygon(self):
        """Corner case where all points are outside polygon works"""

        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        points = [[2, 2], [1, 3], [-1, 1], [0, 2]]      # All outside

        inside, outside = separate_points_by_polygon(points, U)
        assert len(inside) == 0                           # None inside
        assert numpy.allclose(outside, [0, 1, 2, 3])

        indices = outside_polygon(points, U, closed=True)
        assert numpy.allclose(indices, [0, 1, 2, 3])

        indices = inside_polygon(points, U, closed=True)
        assert numpy.allclose(indices, [])

    def test_all_inside_polygon(self):
        """Corner case where all points are inside polygon works"""

        # unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        points = [[0.5, 0.5], [0.2, 0.3], [0, 0.5]]  # All inside (or on edge)

        inside, outside = separate_points_by_polygon(points, U)
        assert len(outside) == 0       # All inside
        assert numpy.allclose(inside, [0, 1, 2])

        indices = outside_polygon(points, U, closed=True)
        assert numpy.allclose(indices, [])

        indices = inside_polygon(points, U, closed=True)
        assert numpy.allclose(indices, [0, 1, 2])

    def test_separate_points_by_polygon_edge(self):
        """Points on polygon edge correctly detected
        """

        # Unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # Try with boundary (vertical edge) point
        inside, outside = separate_points_by_polygon([[0, 0.5],
                                                      [0.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        # Try with boundary (horizontal edge) point
        inside, outside = separate_points_by_polygon([[0.5, 0.0],
                                                      [0.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        # Try with boundary (corner) point
        inside, outside = separate_points_by_polygon([[0.0, 0.0],
                                                      [0.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        # One outside
        inside, outside = separate_points_by_polygon([[0, 0.5],
                                                      [1.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(inside) == 2
        assert numpy.allclose(inside, [0, 2])

    def test_separate_points_by_polygon1(self):
        """Set of points is correctly separated according to polygon
        """

        # Unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        inside, outside = separate_points_by_polygon([[0.5, 0.5]], U)
        assert len(inside) == 1
        assert numpy.allclose(inside, [0])

        inside, outside = separate_points_by_polygon([[0.5, 0.5],
                                                     [0.3, 0.2]], U)
        assert len(inside) == 2
        assert numpy.allclose(inside, [0, 1])

        inside, outside = separate_points_by_polygon([[0.5, 0.5],
                                                     [0.3, 0.2],
                                                     [0.6, 0.7]], U)
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        inside, outside = separate_points_by_polygon([[0.3, 0.2]], U)
        assert len(inside) == 1
        assert numpy.allclose(inside, [0])

        inside, outside = separate_points_by_polygon([[0.3, 0.2],
                                                     [1, -0.5]], U)
        assert len(inside) == 1
        assert numpy.allclose(inside, [0])
        assert numpy.allclose(outside, [1])

        inside, outside = separate_points_by_polygon([[0.5, 0.5],
                                                     [1, -0.5],
                                                     [0.3, 0.2]], U)
        assert numpy.allclose(inside, [0, 2])
        assert numpy.allclose(outside, [1])

        inside, outside = separate_points_by_polygon([[0.1, 0.1],
                                                     [0.5, 0.5],
                                                     [1, -0.5],
                                                     [0.3, 0.2]], U)
        assert numpy.allclose(inside, [0, 1, 3])
        assert numpy.allclose(outside, [2])

        # Try with boundary (edge) point
        inside, outside = separate_points_by_polygon([[0, 0.5],
                                                     [0.1, 0.2]], U)
        assert numpy.allclose(inside, [0, 1])

        # Try with boundary (corner) point
        inside, outside = separate_points_by_polygon([[0, 0],
                                                      [0.1, 0.2]], U)
        assert numpy.allclose(inside, [0, 1])

        # Try with a range of cases point
        inside, outside = separate_points_by_polygon([[0, 0],  # corner
                                                      [0, 0.5],  # edge
                                                      [0.1, 0.2]], U)
        assert numpy.allclose(inside, [0, 1, 2])

        # One more test of vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        inside, outside = separate_points_by_polygon(points, polygon)
        assert numpy.allclose(inside, [0, 1, 2])
        assert numpy.allclose(outside, [3, 4])

        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0],
                  [0.5, 1.5], [0.5, -0.5]]
        inside, outside = separate_points_by_polygon(points, polygon)
        assert numpy.allclose(inside, [1, 2, 3])
        assert numpy.allclose(outside, [0, 4, 5])

    def test_separate_points_by_polygon_characterisation(self):
        """Numpy version of polygon clipping agrees with python version
        """

        # Unit square
        U = [[0, 0], [1, 0], [1, 1], [0, 1]]

        inside_r, outside_r = separate_points_by_polygon([[0.5, 0.5],
                                                          [0.3, 0.2]],
                                                         U,
                                                         use_numpy=True)
        inside_p, outside_p = separate_points_by_polygon([[0.5, 0.5],
                                                          [0.3, 0.2]],
                                                         U,
                                                         use_numpy=False)

        assert numpy.allclose(inside_r, inside_p)
        assert numpy.allclose(outside_r, outside_p)

        inside_r, outside_r = separate_points_by_polygon([[0.5, 0.5],
                                                          [0.3, 0.2],
                                                          [0.6, 0.7]],
                                                         U,
                                                         use_numpy=True)
        inside_p, outside_p = separate_points_by_polygon([[0.5, 0.5],
                                                          [0.3, 0.2],
                                                          [0.6, 0.7]],
                                                         U,
                                                         use_numpy=False)

        assert numpy.allclose(inside_r, inside_p)
        assert numpy.allclose(outside_r, outside_p)

        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0],
                  [0.5, 1.5], [0.5, -0.5]]
        ins_r, out_r = separate_points_by_polygon(points, polygon,
                                                  use_numpy=True)
        ins_p, out_p = separate_points_by_polygon(points, polygon,
                                                  use_numpy=False)
        assert numpy.allclose(ins_r, ins_p)
        assert numpy.allclose(out_r, out_p)

        assert numpy.allclose(ins_p, [1, 2, 3])
        assert numpy.allclose(out_p, [0, 4, 5])

    def test_polygon_clipping_error_handling(self):
        """Polygon clipping checks input as expected"""

        U = [[0, 0], [1, 0], [1, 1], [0, 1]]
        points = [[2, 2], [1, 3], [-1, 1], [0, 2]]

        # Correct call
        separate_points_by_polygon(points, U)

        # Input errors
        try:
            outside_polygon(points, ['what'])
        except:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            outside_polygon('Hmmm', U)
        except:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            inside_polygon(points, U, closed=7)
        except:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

    def test_populate_polygon(self):
        """Polygon can be populated by random points
        """

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
        """Polygon with hole can be populated by random points
        """

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
        """Polygon with hole can be populated by random points (2)
        """

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
        all_points = numpy.concatenate((points_inside, points_outside))
        assert all_points.shape[0] == M + N

        inside, outside = separate_points_by_polygon(all_points, main_polygon)
        count = len(inside)
        msg = 'Expected %i points inside, got %i' % (M, count)
        assert count == M, msg

        msg = 'Expected %i indices outside, got %i' % (N, len(outside))
        assert len(outside) == N, msg

        for point in all_points[inside]:
            assert is_inside_polygon(point, main_polygon)

        for point in all_points[outside]:
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
        all_points = numpy.concatenate((points_inside, points_outside))
        assert all_points.shape[0] == M + N

        inside, outside = separate_points_by_polygon(all_points, main_polygon)
        count = len(inside)
        msg = 'Expected %i points inside, got %i' % (M, count)
        assert count == M, msg

        msg = 'Expected %i indices outside, got %i' % (N, len(outside))
        assert len(outside) == N, msg

        for point in all_points[inside]:
            assert is_inside_polygon(point, main_polygon)

        for point in all_points[outside]:
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
        inside, outside = separate_points_by_polygon(all_points, main_polygon)
        count = len(inside)
        msg = 'Expected %i points inside, got %i' % (271, count)
        assert count == 271, msg

        msg = 'Expected %i indices outside, got %i' % (729, len(outside))
        assert len(outside) == 729, msg

        for point in all_points[inside]:
            assert is_inside_polygon(point, main_polygon)

        for point in all_points[outside]:
            assert not is_inside_polygon(point, main_polygon)

    def test_in_and_outside_polygon_main(self):
        """Set of points is correctly separated according to polygon (2)
        """

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
        assert numpy.alltrue(inside == [0, 1])
        assert len(outside) == 0

        inside, outside = in_and_outside_polygon(points, polygon, closed=False)
        assert len(inside) == 0
        assert numpy.alltrue(outside == [0, 1])

        points = [(100., 0.25), (0.5, 0.5)]
        inside, outside = in_and_outside_polygon(points, polygon)
        assert numpy.alltrue(inside == [1])
        assert outside[0] == 0

        points = [(100., 0.25), (0.5, 0.5), (39, 20),
                  (0.6, 0.7), (56, 43), (67, 90)]
        inside, outside = in_and_outside_polygon(points, polygon)
        assert numpy.alltrue(inside == [1, 3])
        assert numpy.alltrue(outside == [0, 2, 4, 5])

    def test_intersection1(self):
        """Intersection of two simple lines works
        """

        line0 = [[-1, 0], [1, 0]]
        line1 = [[0, -1], [0, 1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [0.0, 0.0])

    def test_intersection2(self):
        """Intersection point is independent of direction
        """

        line0 = [[0, 0], [24, 12]]
        line1 = [[0, 12], [24, 0]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [12.0, 6.0])

        # Swap direction of one line
        line1 = [[24, 0], [0, 12]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [12.0, 6.0])

        # Swap order of lines
        status, value = intersection(line1, line0)
        assert status == 1
        assert numpy.allclose(value, [12.0, 6.0])

    def test_intersection3(self):
        """Intersection point is independent of direction (2)
        """

        line0 = [[0, 0], [24, 12]]
        line1 = [[0, 17], [24, 0]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [14.068965517, 7.0344827586])

        # Swap direction of one line
        line1 = [[24, 0], [0, 17]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [14.068965517, 7.0344827586])

        # Swap order of lines
        status, value = intersection(line1, line0)
        assert status == 1
        assert numpy.allclose(value, [14.068965517, 7.0344827586])

    def test_intersection_endpoints(self):
        """Intersection of lines with coinciding endpoints works

        Test that coinciding endpoints are picked up
        """

        line0 = [[0, 0], [1, 1]]
        line1 = [[1, 1], [2, 1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [1.0, 1.0])

        line0 = [[1, 1], [2, 0]]
        line1 = [[1, 1], [2, 1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert numpy.allclose(value, [1.0, 1.0])

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, [line1[0], line0[1]]))

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
        self.failUnless(numpy.allclose(value, [line0[0], line1[1]]))

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
        self.failUnless(numpy.allclose(value, [line0[0], line1[0]]))

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
        self.failUnless(numpy.allclose(value, [line1[1], line0[1]]))

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
        self.failUnless(numpy.allclose(value, [line0[0], line1[1]]))

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
        self.failUnless(numpy.allclose(value, [line1[0], line0[1]]))

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
        self.failUnless(numpy.allclose(value, [line1[1], line0[1]]))

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
        self.failUnless(numpy.allclose(value, [line0[0], line1[0]]))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line0))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

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
        self.failUnless(numpy.allclose(value, line1))

    def test_intersection_bug_20081110_TR_TL(self):
        """Intersection corner case top-right and top-left

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
        """Intersection corner case top-right and bottom-left

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
        """Intersection corner case top-right and bottom-right

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
        """Intersection is direction invariant

        This runs through a number of examples and checks that
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
            assert numpy.allclose(p1, p2), msg

            # Swap order of lines
            status, p3 = intersection(line1, line0)
            assert status == 1
            msg = 'Order of lines gave different results'
            assert numpy.allclose(p1, p3), msg

    def test_no_intersection(self):
        """Lines that don't intersect return None as expected
        """

        line0 = [[-1, 1], [1, 1]]
        line1 = [[0, -1], [0, 0]]

        status, value = intersection(line0, line1)
        assert status == 0
        assert value is None

    def test_intersection_parallel(self):
        """Parallel lines are correctly detected in intersection code
        """

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
        """Two lines that partly coincide are handled correctly
        """

        # Overlap 1
        line0 = [[0, 0], [5, 0]]
        line1 = [[-3, 0], [3, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[0, 0], [3, 0]])

        # Overlap 2
        line0 = [[-10, 0], [5, 0]]
        line1 = [[-3, 0], [10, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[-3, 0], [5, 0]])

        # Inclusion 1
        line0 = [[0, 0], [5, 0]]
        line1 = [[2, 0], [3, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, line1)

        # Inclusion 2
        line0 = [[1, 0], [5, 0]]
        line1 = [[-10, 0], [15, 0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, line0)

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
        assert numpy.allclose(value, [[1, 7], [7, 19]])

        status, value = intersection(line1, line0)
        assert status == 2
        assert numpy.allclose(value, [[1, 7], [7, 19]])

        # Swap direction
        line0 = [[7, 19], [0, 5]]
        line1 = [[1, 7], [10, 25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[7, 19], [1, 7]])

        line0 = [[0, 5], [7, 19]]
        line1 = [[10, 25], [1, 7]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[1, 7], [7, 19]])

        # Inclusion
        line0 = [[1, 7], [7, 19]]
        line1 = [[0, 5], [10, 25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[1, 7], [7, 19]])

        line0 = [[0, 5], [10, 25]]
        line1 = [[1, 7], [7, 19]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[1, 7], [7, 19]])

        line0 = [[0, 5], [10, 25]]
        line1 = [[7, 19], [1, 7]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert numpy.allclose(value, [[7, 19], [1, 7]])

        # Real life issue
        p1 = [122.22480486608671, -8.6220054852698347]
        p2 = [122.22467227475077, -8.621828474280294]
        p3 = [122.22485121475052, -8.6220016038563081]
        p4 = [122.22472918310231, -8.6218197001101728]
        line0 = [p1, p2]
        line1 = [p3, p4]
        #Vector(geometry=[line0, line1],
        #       geometry_type='line').write_to_file('impossible_state.shp')
        status, value = intersection(line0, line1)
        assert status == 0
        assert value is None

    def test_clip_line_by_polygon_simple(self):
        """Simple lines are clipped and classified by polygon
        """

        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # Simple horizontal fully intersecting line
        line = [[-1, 0.5], [2, 0.5]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 0.5], [1, 0.5]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 0.5], [0, 0.5]],
                               [[1, 0.5], [2, 0.5]]])

        # Simple horizontal line coinciding with polygon edge
        # It will be clipped at its midpoint, but segments fused again
        line = [[-1, 1], [2, 1]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 1], [0.5, 1], [1, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 1], [0, 1]],
                               [[1, 1], [2, 1]]])

        # Simple vertical fully intersecting line
        line = [[0.5, -1], [0.5, 2]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0.5, 0], [0.5, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[0.5, -1], [0.5, 0]],
                               [[0.5, 1], [0.5, 2]]])

        # Simple vertical line coinciding with polygon edge
        # It will be clipped at its midpoint, but segments fused again
        line = [[1, -1], [1, 2]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[1, 0], [1, 0.5], [1, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[1, -1], [1, 0]],
                               [[1, 1], [1, 2]]])

        # Simple sloping fully intersecting line
        line = [[-1, 0.0], [2, 1.0]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 1.0 / 3], [1, 2.0 / 3]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 0], [0, 1.0 / 3]],
                               [[1, 2.0 / 3], [2, 1]]])

        # Simple sloping line coinciding with one edge, intersecting another
        line = [[-1, 0.0], [1, 2.0 / 3]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 1.0 / 3], [1, 2.0 / 3]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 0], [0, 1.0 / 3]]])

        # Diagonal line intersecting corners
        line = [[-1, -1], [2, 2]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 0], [1, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, -1], [0, 0]],
                               [[1, 1], [2, 2]]])

        # Diagonal line intersecting corners - other way
        line = [[-1, 2], [2, -1]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 1], [1, 0]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 2], [0, 1]],
                               [[1, 0], [2, -1]]])

        # Diagonal line coinciding with one corner
        line = [[-1, -1], [1, 1]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 0], [1, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, -1], [0, 0]]])

        # Very convoluted polygon
        polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                   [30, 10], [40, -10]]

        line = [[-10, 6], [60, 6]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[6, 6], [14, 6]], [[16, 6.], [22, 6]],
                              [[28, 6], [32, 6]]])
        assert numpy.allclose(outside_line_segments,
                              [[[-10, 6], [6, 6]], [[14, 6], [16, 6]],
                              [[22, 6], [28, 6]], [[32, 6], [60, 6]]])

    def test_clip_composite_lines_by_polygon(self):
        """Composite lines are clipped and classified by polygon
        """

        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # One line with same two segments changing direction inside polygon
        line = [[-1, 0.5], [0.5, 0.5], [0.5, 2]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 0.5], [0.5, 0.5], [0.5, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 0.5], [0, 0.5]],
                               [[0.5, 1], [0.5, 2]]])

        # One line with multiple segments both inside and outside polygon
        line = [[-1, 0.5], [-0.5, 0.5], [0.5, 0.5],
                [1.0, 0.5], [1.5, 0.5], [2.0, 0.5]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)
        assert len(inside_line_segments) == 1
        assert numpy.allclose(inside_line_segments,
                              [[0, 0.5], [0.5, 0.5], [1.0, 0.5]])

    def test_clip_lines_by_polygon_multi(self):
        """Multiple composite lines are clipped and classified by polygon
        """

        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # Two lines changing direction inside polygon
        lines = [[[-1, 0.5], [0.5, 0.5]],
                 [[0.5, 0.5], [0.5, 2]]]

        inside_line_segments, outside_line_segments = \
            clip_lines_by_polygon(lines, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 0.5], [0.5, 0.5]],
                               [[0.5, 0.5], [0.5, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 0.5], [0, 0.5]],
                               [[0.5, 1], [0.5, 2]]])

        # Multiple lines with different number of segments
        lines = [[[-1, 0.5], [0.5, 0.5], [0.5, 2]],
                 [[-1, 0.0], [1, 2.0 / 3]]]

        inside_line_segments, outside_line_segments = \
            clip_lines_by_polygon(lines, polygon)

        assert numpy.allclose(inside_line_segments[0],
                              [[0, 0.5], [0.5, 0.5], [0.5, 1]])
        assert numpy.allclose(inside_line_segments[1],
                              [[0, 1.0 / 3], [1, 2.0 / 3]])

        assert numpy.allclose(outside_line_segments,
                              [[[-1, 0.5], [0, 0.5]],
                               [[0.5, 1], [0.5, 2]],
                               [[-1, 0], [0, 1.0 / 3]]])

    def test_clip_lines_by_polygon_real_data(self):
        """Real roads are clipped by complex polygon
        """

        inside_line_segments, outside_line_segments = \
            clip_lines_by_polygon(test_lines, test_polygon)

        # These lines have compontes both inside and outside
        assert len(inside_line_segments) == 13
        assert len(outside_line_segments) == 17

        # Store for visual inspection by e.g. QGis
        if False:
            Vector(geometry=[test_polygon],
                   geometry_type='polygon').write_to_file('test_polygon.shp')
            Vector(geometry=test_lines,
                   geometry_type='line').write_to_file('test_lines.shp')
            Vector(geometry=inside_line_segments,
                   geometry_type='line').write_to_file('inside_segments.shp')
            Vector(geometry=outside_line_segments,
                   geometry_type='line').write_to_file('outside_segments.shp')

        # Check that midpoints of each segment are correctly placed
        for seg in inside_line_segments:
            N = len(seg)
            for i in range(N - 1):
                midpoint = (seg[i] + seg[i + 1]) / 2
                assert is_inside_polygon(midpoint, test_polygon)

        for seg in outside_line_segments:
            N = len(seg)
            for i in range(N - 1):
                midpoint = (seg[i] + seg[i + 1]) / 2
                assert not is_inside_polygon(midpoint, test_polygon)

        # Characterisation test based on visually verified result
        #print inside_line_segments, len(inside_line_segments)
        #print outside_line_segments, len(outside_line_segments)
        assert len(inside_line_segments) == 13
        assert len(outside_line_segments) == 17
        assert numpy.allclose(inside_line_segments[0],
                              [[122.23028405, -8.62598333],
                               [122.22879, -8.624855],
                               [122.22776827, -8.62420644]])

        assert numpy.allclose(inside_line_segments[-1],
                              [[122.247938, -8.632926],
                               [122.24793987, -8.63351817]])

        assert numpy.allclose(outside_line_segments[0],
                              [[122.231021, -8.626557],
                               [122.230563, -8.626194],
                               [122.23028405, -8.62598333]])

        assert numpy.allclose(outside_line_segments[-1],
                              [[122.24793987, -8.63351817],
                               [122.24794, -8.63356],
                               [122.24739, -8.63622]])

        # Not joined are (but that's OK)
        #[[122.231108, -8.626598], [122.231021, -8.626557]]
        #[[122.231021, -8.626557], [122.230284, -8.625983]]

    def test_join_segments(self):
        """Consecutive line segments can be joined into continuous line
        """

        # Two segments forming one line
        segments = [[[-1, 0.5], [0.5, 0.5]],
                    [[0.5, 0.5], [0.5, 2]]]
        lines = join_line_segments(segments)

        assert len(lines) == 1
        assert numpy.allclose(lines[0], [[-1, 0.5], [0.5, 0.5], [0.5, 2]])

        # Longer line
        segments = [[[0.0, 0.5], [0.5, 0.5]],
                    [[0.5, 0.5], [0.5, 2.0]],
                    [[0.5, 2.0], [1.0, 2.0]],
                    [[1.0, 2.0], [2.0, 2.0]]]
        lines = join_line_segments(segments)
        assert len(lines) == 1
        assert numpy.allclose(lines[0], [[0.0, 0.5], [0.5, 0.5],
                                         [0.5, 2.0], [1.0, 2.0],
                                         [2.0, 2.0]])

        # Disjoint segment forming two multilines
        segments = [[[0.0, 0.5], [0.5, 0.5]],
                    [[0.5, 0.5], [0.5, 2.0]],
                    [[0.7, 2.0], [1.0, 2.0]],
                    [[1.0, 2.0], [2.0, 2.0]]]
        lines = join_line_segments(segments)
        assert len(lines) == 2
        assert numpy.allclose(lines[0], [[0.0, 0.5], [0.5, 0.5],
                                         [0.5, 2.0]])
        assert numpy.allclose(lines[1], [[0.7, 2.0], [1.0, 2.0],
                                         [2.0, 2.0]])

        # Another example
        segments = [[[0, 0.5], [0.5, 0.5]],
                    [[0.5, 0.5], [0.5, 1]],
                    [[0, 1.0 / 3], [1, 2.0 / 3]]]
        lines = join_line_segments(segments)
        assert len(lines) == 2
        assert numpy.allclose(lines[0], [[0.0, 0.5], [0.5, 0.5],
                                         [0.5, 1.0]])
        assert numpy.allclose(lines[1], [[0, 1.0 / 3], [1, 2.0 / 3]])

        # One with all segments separate
        segments = [[[-1, 0.5], [0, 0.5]],
                    [[0.5, 1], [0.5, 2]],
                    [[-1, 0], [0, 1.0 / 3]]]
        lines = join_line_segments(segments)
        assert len(lines) == 3
        for i in range(len(lines)):
            assert numpy.allclose(lines[i], segments[i])


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Polygon, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
