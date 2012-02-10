#!/usr/bin/env python

import unittest
import numpy as num
from math import sqrt, pi
from anuga.utilities.numerical_tools import ensure_numeric
from anuga.utilities.system_tools import get_pathname_from_package

from polygon import *
from anuga.coordinate_transforms.geo_reference import Geo_reference
from anuga.geospatial_data.geospatial_data import Geospatial_data


def test_function(x, y):
    return x+y


class Test_Polygon(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_that_C_extension_compiles(self):
        FN = 'polygon_ext.c'
        try:
            import polygon_ext
        except:
            from compile import compile

            try:
                compile(FN)
            except:
                raise Exception, 'Could not compile %s' %FN
            else:
                import polygon_ext

    # Polygon stuff
    def test_polygon_function_constants(self):
        p1 = [[0,0], [10,0], [10,10], [0,10]]
        p2 = [[0,0], [10,10], [15,5], [20, 10], [25,0], [30,10], [40,-10]]

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

    def test_polygon_function_csvfile(self):
        from os import sep, getenv

        # Get path where this test is run
        path = get_pathname_from_package('anuga.utilities')

        # Form absolute filename and read
        filename = path + sep + 'mainland_only.csv'
        p1 = read_polygon(filename)

        f = Polygon_function([(p1, 10.0)])
        z = f([430000, 480000], [490000, 7720000]) # 1st outside, 2nd inside

        assert num.allclose(z, [0, 10])

    def test_polygon_function_georef(self):
        """Check that georeferencing works"""

        from anuga.coordinate_transforms.geo_reference import Geo_reference

        geo = Geo_reference(56, 200, 1000)

        # Make points 'absolute'
        p1 = [[200,1000], [210,1000], [210,1010], [200,1010]]
        p2 = [[200,1000], [210,1010], [215,1005], [220, 1010], [225,1000],
              [230,1010], [240,990]]

        f = Polygon_function([(p1, 1.0)], geo_reference=geo)
        z = f([5, 5, 27, 35], [5, 9, 8, -5]) # Two first inside p1

        assert num.allclose(z, [1, 1, 0, 0])

        f = Polygon_function([(p2, 2.0)], geo_reference=geo)
        z = f([5, 5, 27, 35], [5, 9, 8, -5]) # First and last inside p2
        assert num.allclose(z, [2, 0, 0, 2])

        # Combined
        f = Polygon_function([(p1, 1.0), (p2, 2.0)], geo_reference=geo)
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 1, 0, 2])

        # Check that it would fail without geo
        f = Polygon_function([(p1, 1.0), (p2, 2.0)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert not num.allclose(z, [2, 1, 0, 2])

    def test_polygon_function_callable(self):
        """Check that values passed into Polygon_function can be callable."""

        p1 = [[0,0], [10,0], [10,10], [0,10]]
        p2 = [[0,0], [10,10], [15,5], [20, 10], [25,0], [30,10], [40,-10]]

        f = Polygon_function([(p1, test_function)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5]) # Two first inside p1
        assert num.allclose(z, [10, 14, 0, 0])

        # Combined
        f = Polygon_function([(p1, test_function), (p2, 2.0)])
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 14, 0, 2])

        # Combined w default
        f = Polygon_function([(p1, test_function), (p2, 2.0)], default = 3.14)
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 14, 3.14, 2])

        # Combined w default func
        f = Polygon_function([(p1, test_function), (p2, 2.0)],
                             default=test_function)
        z = f([5, 5, 27, 35], [5, 9, 8, -5])
        assert num.allclose(z, [2, 14, 35, 2])

    def test_point_on_line(self):
        # Endpoints first
        assert point_on_line([0,0], [[0,0], [1,0]])
        assert point_on_line([1,0], [[0,0], [1,0]])

        # Endpoints first - non-simple
        assert point_on_line([-0.1,0.0], [[-0.1,0.0], [1.5,0.6]])
        assert point_on_line([1.5,0.6], [[-0.1,0.0], [1.5,0.6]])

        # Then points on line
        assert point_on_line([0.5,0], [[0,0], [1,0]])
        assert point_on_line([0,0.5], [[0,1], [0,0]])
        assert point_on_line([1,0.5], [[1,1], [1,0]])
        assert point_on_line([0.5,0.5], [[0,0], [1,1]])

        # Then points not on line
        assert not point_on_line([0.5,0], [[0,1], [1,1]])
        assert not point_on_line([0,0.5], [[0,0], [1,1]])

        # From real example that failed
        assert not point_on_line([40,50], [[40,20], [40,40]])

        # From real example that failed
        assert not point_on_line([40,19], [[40,20], [40,40]])

        # Degenerate line
        assert point_on_line([40,19], [[40,19], [40,19]])
        assert not point_on_line([40,19], [[40,40], [40,40]])

    def test_is_inside_polygon_main(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,1], [0,1]]

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

    def test_inside_polygon_main(self):
        """test_is_inside_polygon_quick
        
        Test fast version of of is_inside_polygon
        """

        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,1], [0,1]]

        assert is_inside_polygon_quick( (0.5, 0.5), polygon )
        assert not is_inside_polygon_quick( (0.5, 1.5), polygon )
        assert not is_inside_polygon_quick( (0.5, -0.5), polygon )
        assert not is_inside_polygon_quick( (-0.5, 0.5), polygon )
        assert not is_inside_polygon_quick( (1.5, 0.5), polygon )

        # Try point on borders
        assert is_inside_polygon_quick( (1., 0.5), polygon, closed=True)
        assert is_inside_polygon_quick( (0.5, 1), polygon, closed=True)
        assert is_inside_polygon_quick( (0., 0.5), polygon, closed=True)
        assert is_inside_polygon_quick( (0.5, 0.), polygon, closed=True)

        assert not is_inside_polygon_quick( (0.5, 1), polygon, closed=False)
        assert not is_inside_polygon_quick( (0., 0.5), polygon, closed=False)
        assert not is_inside_polygon_quick( (0.5, 0.), polygon, closed=False)
        assert not is_inside_polygon_quick( (1., 0.5), polygon, closed=False)


    def test_inside_polygon_main(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,1], [0,1]]

        # From real example (that failed)
        polygon = [[20,20], [40,20], [40,40], [20,40]]
        points = [[40, 50]]
        res = inside_polygon(points, polygon)
        assert len(res) == 0

        polygon = [[20,20], [40,20], [40,40], [20,40]]
        points = [[25, 25], [30, 20], [40, 50], [90, 20], [40, 90]]
        res = inside_polygon(points, polygon)
        assert len(res) == 2
        assert num.allclose(res, [0,1])

        # More convoluted and non convex polygon
        polygon = [[0,0], [1,0], [0.5,-1], [2, -1], [2,1], [0,1]]
        assert is_inside_polygon( (0.5, 0.5), polygon )
        assert is_inside_polygon( (1, -0.5), polygon )
        assert is_inside_polygon( (1.5, 0), polygon )

        assert not is_inside_polygon( (0.5, 1.5), polygon )
        assert not is_inside_polygon( (0.5, -0.5), polygon )

        assert is_inside_polygon_quick( (0.5, 0.5), polygon )
        assert is_inside_polygon_quick( (1, -0.5), polygon )
        assert is_inside_polygon_quick( (1.5, 0), polygon )

        assert not is_inside_polygon_quick( (0.5, 1.5), polygon )
        assert not is_inside_polygon_quick( (0.5, -0.5), polygon )

        # Very convoluted polygon
        polygon = [[0,0], [10,10], [15,5], [20, 10], [25,0], [30,10], [40,-10]]
        assert is_inside_polygon((5, 5), polygon)
        assert is_inside_polygon((17, 7), polygon)
        assert is_inside_polygon((27, 2), polygon)
        assert is_inside_polygon((35, -5), polygon)
        assert not is_inside_polygon((15, 7), polygon)
        assert not is_inside_polygon((24, 3), polygon)
        assert not is_inside_polygon((25, -10), polygon)

        # Another combination (that failed)
        polygon = [[0,0], [10,0], [10,10], [0,10]]
        assert is_inside_polygon((5, 5), polygon)
        assert is_inside_polygon((7, 7), polygon)
        assert not is_inside_polygon((-17, 7), polygon)
        assert not is_inside_polygon((7, 17), polygon)
        assert not is_inside_polygon((17, 7), polygon)
        assert not is_inside_polygon((27, 8), polygon)
        assert not is_inside_polygon((35, -5), polygon)

        # Multiple polygons
        polygon = [[0,0], [1,0], [1,1], [0,1], [0,0], [10,10],
                   [11,10], [11,11], [10,11], [10,10]]
        assert is_inside_polygon((0.5, 0.5), polygon)
        assert is_inside_polygon((10.5, 10.5), polygon)

        # FIXME: Fails if point is 5.5, 5.5
        assert not is_inside_polygon((0, 5.5), polygon)

        # Polygon with a hole
        polygon = [[-1,-1], [2,-1], [2,2], [-1,2], [-1,-1],
                   [0,0], [1,0], [1,1], [0,1], [0,0]]

        assert is_inside_polygon((0, -0.5), polygon)
        assert not is_inside_polygon((0.5, 0.5), polygon)

    def test_duplicate_points_being_ok(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,0], [1,0], [1,1], [0,1], [0,0]]

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
        polygon = [[20,20], [40,20], [40,40], [20,40]]
        points = [[40, 50]]
        res = inside_polygon(points, polygon)
        assert len(res) == 0

    def test_inside_polygon_vector_version(self):
        # Now try the vector formulation returning indices
        polygon = [[0,0], [1,0], [0.5,-1], [2, -1], [2,1], [0,1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res = inside_polygon( points, polygon, verbose=False )
        assert num.allclose(res, [0,1,2])

    def test_outside_polygon(self):
        # unit square
        U = [[0,0], [1,0], [1,1], [0,1]]

        # evaluate to False as the point 0.5, 0.5 is inside the unit square
        assert not is_outside_polygon([0.5, 0.5], U)

        # evaluate to True as the point 1.5, 0.5 is outside the unit square
        assert is_outside_polygon([1.5, 0.5], U)

        indices = outside_polygon([[0.5, 0.5], [1, -0.5], [0.3, 0.2]], U)
        assert num.allclose(indices, [1])

        # One more test of vector formulation returning indices
        polygon = [[0,0], [1,0], [0.5,-1], [2, -1], [2,1], [0,1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res = outside_polygon(points, polygon)
        assert num.allclose(res, [3, 4])

        polygon = [[0,0], [1,0], [0.5,-1], [2, -1], [2,1], [0,1]]
        points = [[0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0],
                  [0.5, 1.5], [0.5, -0.5]]
        res = outside_polygon(points, polygon)

        assert num.allclose(res, [0, 4, 5])

    def test_outside_polygon2(self):
        # unit square
        U = [[0,0], [1,0], [1,1], [0,1]]

        # evaluate to False as the point 0.5, 1.0 is inside the unit square
        assert not outside_polygon([0.5, 1.0], U, closed = True)

        # evaluate to True as the point 0.5, 1.0 is outside the unit square
        assert is_outside_polygon([0.5, 1.0], U, closed = False)

    def test_all_outside_polygon(self):
        """Test case where all points are outside poly"""

        # unit square
        U = [[0,0], [1,0], [1,1], [0,1]]

        points = [[2,2], [1,3], [-1,1], [0,2]]      # All outside

        indices, count = separate_points_by_polygon(points, U)
        assert count == 0                           # None inside
        assert num.allclose(indices, [3, 2, 1, 0])

        indices = outside_polygon(points, U, closed = True)
        assert num.allclose(indices, [0, 1, 2, 3])

        indices = inside_polygon(points, U, closed = True)
        assert num.allclose(indices, [])

    def test_all_inside_polygon(self):
        """Test case where all points are inside poly"""

        # unit square
        U = [[0,0], [1,0], [1,1], [0,1]]

        points = [[0.5,0.5], [0.2,0.3], [0,0.5]]    # All inside (or on edge)

        indices, count = separate_points_by_polygon(points, U)
        assert count == 3       # All inside
        assert num.allclose(indices, [0, 1, 2])

        indices = outside_polygon(points, U, closed=True)
        assert num.allclose(indices, [])

        indices = inside_polygon(points, U, closed=True)
        assert num.allclose(indices, [0, 1, 2])


    def test_separate_points_by_polygon(self):
        # unit square
        U = [[0,0], [1,0], [1,1], [0,1]]

        indices, count = separate_points_by_polygon([[0.5, 0.5],
                                                     [1, -0.5],
                                                     [0.3, 0.2]],
                                                    U)
        assert num.allclose( indices, [0, 2, 1] )
        assert count == 2

        # One more test of vector formulation returning indices
        polygon = [[0,0], [1,0], [0.5,-1], [2, -1], [2,1], [0,1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res, count = separate_points_by_polygon(points, polygon)

        assert num.allclose(res, [0, 1, 2, 4, 3])
        assert count == 3

        polygon = [[0,0], [1,0], [0.5,-1], [2, -1], [2,1], [0,1]]
        points = [ [0.5, 1.4], [0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]
        res, count = separate_points_by_polygon( points, polygon )

        assert num.allclose( res, [1,2,3,5,4,0] )
        assert count == 3


    def test_is_inside_triangle(self):
        # Simplest case:
        triangle = [[0, 0], [1, 0], [0.5, 1]]

        assert is_inside_triangle((0.5, 0.5), triangle)
        assert is_inside_triangle((0.9, 0.1), triangle)
        assert not is_inside_triangle((0.5, 1.5), triangle)
        assert not is_inside_triangle((0.5, -0.5), triangle)
        assert not is_inside_triangle((-0.5, 0.5), triangle)
        assert not is_inside_triangle((1.5, 0.5), triangle)

        # Try point on borders
        assert is_inside_triangle((0.5, 0), triangle, closed=True)
        assert is_inside_triangle((1, 0), triangle, closed=True)

        assert not is_inside_triangle((0.5, 0), triangle, closed=False)
        assert not is_inside_triangle((1, 0), triangle, closed=False)

        # Try vertices
        for P in triangle:
            assert is_inside_triangle(P, triangle, closed=True)
            assert not is_inside_triangle(P, triangle, closed=False)

        # Slightly different
        triangle = [[0, 0.1], [1, -0.2], [0.5, 1]]
        assert is_inside_triangle((0.5, 0.5), triangle)
        assert is_inside_triangle((0.4, 0.1), triangle)
        assert not is_inside_triangle((1, 1), triangle)

        # Try vertices
        for P in triangle:
            assert is_inside_triangle(P, triangle, closed=True)
            assert not is_inside_triangle(P, triangle, closed=False)


    def test_populate_polygon(self):
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        points = populate_polygon(polygon, 5)

        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)

            assert is_inside_polygon_quick(point, polygon)


        # Very convoluted polygon
        polygon = [[0,0], [10,10], [15,5], [20, 10], [25,0], [30,10], [40,-10]]
        points = populate_polygon(polygon, 5)
        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert is_inside_polygon_quick(point, polygon)


    def test_populate_polygon_with_exclude(self):
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        ex_poly = [[0,0], [0.5,0], [0.5, 0.5], [0,0.5]]     # SW quarter
        points = populate_polygon(polygon, 5, exclude=[ex_poly])

        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly)

        # overlap
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        ex_poly = [[-1,-1], [0.5,0], [0.5, 0.5], [-1,0.5]]
        points = populate_polygon(polygon, 5, exclude=[ex_poly])

        assert len(points) == 5
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly)

        # Multiple
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        ex_poly1 = [[0,0], [0.5,0], [0.5, 0.5], [0,0.5]]    # SW quarter
        ex_poly2 = [[0.5,0.5], [0.5,1], [1, 1], [1,0.5]]    # NE quarter

        points = populate_polygon(polygon, 20, exclude=[ex_poly1, ex_poly2])

        assert len(points) == 20
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly1)
            assert not is_inside_polygon(point, ex_poly2)

        # Very convoluted polygon
        polygon = [[0,0], [10,10], [15,5], [20, 10], [25,0], [30,10], [40,-10]]
        ex_poly = [[-1,-1], [5,0], [5, 5], [-1,5]]
        points = populate_polygon(polygon, 20, exclude=[ex_poly])

        assert len(points) == 20
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly), '%s' % str(point)

    def test_populate_polygon_with_exclude2(self):
        min_outer = 0
        max_outer = 1000
        polygon_outer = [[min_outer,min_outer], [max_outer,min_outer],
                         [max_outer,max_outer], [min_outer,max_outer]]

        delta = 10
        min_inner1 = min_outer + delta
        max_inner1 = max_outer - delta
        inner1_polygon = [[min_inner1,min_inner1], [max_inner1,min_inner1],
                          [max_inner1,max_inner1], [min_inner1,max_inner1]]

        density_inner2 = 1000
        min_inner2 = min_outer + 2*delta
        max_inner2 = max_outer - 2*delta
        inner2_polygon = [[min_inner2,min_inner2], [max_inner2,min_inner2],
                          [max_inner2,max_inner2], [min_inner2,max_inner2]]

        points = populate_polygon(polygon_outer, 20,
                                  exclude=[inner1_polygon, inner2_polygon])

        assert len(points) == 20
        for point in points:
            assert is_inside_polygon(point, polygon_outer)
            assert not is_inside_polygon(point, inner1_polygon)
            assert not is_inside_polygon(point, inner2_polygon)

        # Very convoluted polygon
        polygon = [[0,0], [10,10], [15,5], [20, 10], [25,0], [30,10], [40,-10]]
        ex_poly = [[-1,-1], [5,0], [5, 5], [-1,5]]
        points = populate_polygon(polygon, 20, exclude=[ex_poly])

        assert len(points) == 20
        for point in points:
            assert is_inside_polygon(point, polygon)
            assert not is_inside_polygon(point, ex_poly), '%s' % str(point)

    def test_point_in_polygon(self):
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        point = point_in_polygon(polygon)
        assert is_inside_polygon(point, polygon)

        # this may get into a vicious loop
        # polygon = [[1e32,1e54], [1,0], [1,1], [0,1]]

        polygon = [[1e15,1e7], [1,0], [1,1], [0,1]]
        point = point_in_polygon(polygon)
        assert is_inside_polygon(point, polygon)

        polygon = [[0,0], [1,0], [1,1], [1e8,1e8]]
        point = point_in_polygon(polygon)
        assert is_inside_polygon(point, polygon)

        polygon = [[1e32,1e54], [-1e32,1e54], [1e32,-1e54]]
        point = point_in_polygon(polygon)
        assert is_inside_polygon(point, polygon)

        polygon = [[1e18,1e15], [1,0], [0,1]]
        point = point_in_polygon(polygon)
        assert is_inside_polygon(point, polygon)

    def test_in_and_outside_polygon_main(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,1], [0,1]]

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

        points = [(1., 0.25),(1., 0.75)]
        inside, outside = in_and_outside_polygon(points, polygon, closed=True)
        assert num.alltrue(inside == [0,1])
        assert len(outside) == 0

        inside, outside = in_and_outside_polygon(points, polygon, closed=False)
        assert len(inside) == 0
        assert num.alltrue(outside == [0,1])

        points = [(100., 0.25), (0.5, 0.5) ]
        inside, outside = in_and_outside_polygon(points, polygon)
        assert num.alltrue(inside == [1])
        assert outside[0] == 0

        points = [(100., 0.25),(0.5, 0.5), (39,20), (0.6,0.7),(56,43),(67,90)]
        inside, outside = in_and_outside_polygon(points, polygon)
        assert num.alltrue(inside == [1, 3])
        assert num.alltrue(outside == [0, 2, 4, 5])

    def test_intersection1(self):
        line0 = [[-1,0], [1,0]]
        line1 = [[0,-1], [0,1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [0.0, 0.0])

    def test_intersection2(self):
        line0 = [[0,0], [24,12]]
        line1 = [[0,12], [24,0]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [12.0, 6.0])

        # Swap direction of one line
        line1 = [[24,0], [0,12]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [12.0, 6.0])

        # Swap order of lines
        status, value = intersection(line1, line0)
        assert status == 1
        assert num.allclose(value, [12.0, 6.0])

    def test_intersection3(self):
        line0 = [[0,0], [24,12]]
        line1 = [[0,17], [24,0]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [14.068965517, 7.0344827586])

        # Swap direction of one line
        line1 = [[24,0], [0,17]]

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

        line0 = [[0,0], [1,1]]
        line1 = [[1,1], [2,1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [1.0, 1.0])

        line0 = [[1,1], [2,0]]
        line1 = [[1,1], [2,1]]

        status, value = intersection(line0, line1)
        assert status == 1
        assert num.allclose(value, [1.0, 1.0])

    # This function is a helper function for
    # the test_intersection_bug_20081110_?() set of tests.
    # This function tests all parallel line cases for 4 collinear points.
    # This function should never be run directly by the unittest code.
    def helper_test_parallel_intersection_code(self, P1, P2, P3, P4):
        # lines in same direction, no overlap
        # 0:         ---->----
        # 1:                     --------->-----------
        line0 = [P1, P2]
        line1 = [P3, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=3, 'Expected status 3, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(value is None, 'Expected value of None, got %s' %
                                       str(value))

        # lines in same direction, no overlap
        # 0:         ----<----
        # 1:                     ---------<-----------
        line0 = [P2, P1]
        line1 = [P4, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=3, 'Expected status 3, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(value is None, 'Expected value of None, got %s' %
                                       str(value))

        # lines in opposite direction, no overlap
        # 0:         ----<----
        # 1:                     --------->-----------
        line0 = [P2, P1]
        line1 = [P3, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=3, 'Expected status 3, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(value is None, 'Expected value of None, got %s' %
                                       str(value))

        # lines in opposite direction, no overlap
        # 0:         ---->----
        # 1:                     ---------<-----------
        line0 = [P1, P2]
        line1 = [P4, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=3, 'Expected status 3, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(value is None, 'Expected value of None, got %s' %
                                       str(value))

        # ----------------------------------------------------------------------

        # line0 fully within line1, same direction
        # 0:         ---->----
        # 1:    --------->-----------
        # value should be line0:
        #            ---->----
        line0 = [P2, P3]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # ----------------------------------------------------------------------

        # line1 fully within line0, same direction
        # 0:    --------->-----------
        # 1:         ---->----
        # value should be line1:
        #            ---->----
        line0 = [P1, P4]
        line1 = [P2, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # ----------------------------------------------------------------------

        # line in same direction, partial overlap
        # 0:    ----->-----
        # 1:       ------->--------
        # value should be segment line1_start->line0_end:
        #          --->----
        line0 = [P1, P3]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[0],line0[1]]))

        # line in same direction, partial overlap
        # 0:    -----<-----
        # 1:       -------<--------
        # value should be segment line0_start->line1_end:
        #          ---<----
        line0 = [P3, P1]
        line1 = [P4, P2]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0],line1[1]]))

        # line in opposite direction, partial overlap
        # 0:    -----<-----
        # 1:       ------->--------
        # value should be segment line0_start->line1_start:
        #          ---<----
        line0 = [P3, P1]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0],line1[0]]))

        # line in opposite direction, partial overlap
        # 0:    ----->-----
        # 1:       -------<--------
        # value should be segment line1_end->line0_end:
        #          --->----
        line0 = [P1, P3]
        line1 = [P4, P2]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[1],line0[1]]))

        # ----------------------------------------------------------------------

        # line in same direction, partial overlap
        # 0:       ------>------
        # 1:    ------>------
        # value should be segment line0_start->line1_end:
        #          --->----
        line0 = [P2, P4]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0],line1[1]]))

        # line in same direction, partial overlap
        # 0:       ------<------
        # 1:    ------<------
        # value should be segment line1_start->line0_end:
        #          ----<-----
        line0 = [P4, P2]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[0],line0[1]]))

        # line in opposite direction, partial overlap
        # 0:       ------<------
        # 1:    ----->------
        # value should be segment line1_end->line0_end:
        #          --->----
        line0 = [P4, P2]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line1[1],line0[1]]))

        # line in opposite direction, partial overlap
        # 0:       ------>------
        # 1:    -----<------
        # value should be segment line0_start->line1_start:
        #          ---<----
        line0 = [P2, P4]
        line1 = [P3, P1]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, [line0[0],line1[0]]))

        # ----------------------------------------------------------------------

        # line in same direction, same left point, line1 longer
        # 0:    ----->------
        # 1:    ------->--------
        # value should be line0:
        #       ----->------
        line0 = [P1, P3]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # ----------------------------------------------------------------------

        # line in same direction, same left point, same right point
        # 0:    ------->--------
        # 1:    ------->--------
        # value should be line0 or line1:
        #       ------->--------
        line0 = [P1, P3]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # ----------------------------------------------------------------------

        # line in same direction, same right point, line1 longer
        # 0:        ----->------
        # 1:    ------->--------
        # value should be line0:
        #           ----->------
        line0 = [P2, P4]
        line1 = [P1, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, line0))

        # ----------------------------------------------------------------------

        # line in same direction, same left point, line0 longer
        # 0:    ------->--------
        # 1:    ----->------
        # value should be line1:
        #       ----->------
        line0 = [P1, P4]
        line1 = [P1, P3]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
                               (str(status), str(value)))
        self.failUnless(num.allclose(value, line1))

        # ----------------------------------------------------------------------

        # line in same direction, same right point, line0 longer
        # 0:    ------->--------
        # 1:        ----->------
        # value should be line1:
        #           ----->------
        line0 = [P1, P4]
        line1 = [P2, P4]
        status, value = intersection(line0, line1)
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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
        self.failIf(status!=2, 'Expected status 2, got status=%s, value=%s' %
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

        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, 1.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, 1.0]
        P2 = [2.0, 2.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [2.0, 2.0]
        P3 = [3.0, 3.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [3.0, 3.0]
        P4 = [4.0, 4.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

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

        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, 1.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, 1.0]
        P2 = [-2.0, 2.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [-2.0, 2.0]
        P3 = [-3.0, 3.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [-3.0, 3.0]
        P4 = [-4.0, 4.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

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

        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, -1.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [-1.0, -1.0]
        P2 = [-2.0, -2.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [-2.0, -2.0]
        P3 = [-3.0, -3.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [-3.0, -3.0]
        P4 = [-4.0, -4.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

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

        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, -1.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P1 = [1.0, -1.0]
        P2 = [2.0, -2.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P2 = [2.0, -2.0]
        P3 = [3.0, -3.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)
        P3 = [3.0, -3.0]
        P4 = [4.0, -4.0+1.0e-9]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TR_TL(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right & top-left quadrant
        """

        # define 4 collinear points, 1 in TL, 3 in TR
        #    P1-+-P2---P3---P4
        P1 = [-3.0, 1.0]
        P2 = [ 1.0, 5.0]
        P3 = [ 2.0, 6.0]
        P4 = [ 3.0, 7.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 2 in TL, 2 in TR
        #    P1---P2-+-P3---P4
        P1 = [-3.0, 1.0]
        P2 = [-2.0, 2.0]
        P3 = [ 2.0, 6.0]
        P4 = [ 3.0, 7.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 3 in TL, 1 in TR
        #    P1---P2---P3-+-P4
        P1 = [-3.0, 1.0]
        P2 = [-2.0, 2.0]
        P3 = [-1.0, 3.0]
        P4 = [ 3.0, 7.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TR_BL(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right & bottom-left quadrant
        """

        # define 4 collinear points, 1 in BL, 3 in TR
        #    P1-+-P2---P3---P4
        P1 = [-4.0, -3.0]
        P2 = [ 1.0,  2.0]
        P3 = [ 2.0,  3.0]
        P4 = [ 3.0,  4.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 2 in TL, 2 in TR
        #    P1---P2-+-P3---P4
        P1 = [-4.0, -3.0]
        P2 = [-3.0, -2.0]
        P3 = [ 2.0,  3.0]
        P4 = [ 3.0,  4.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 3 in TL, 1 in TR
        #    P1---P2---P3-+-P4
        P1 = [-4.0, -3.0]
        P2 = [-3.0, -2.0]
        P3 = [-2.0, -1.0]
        P4 = [ 3.0,  4.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

    def test_intersection_bug_20081110_TR_BR(self):
        """test_intersection_bug_20081110(self)

        Test all cases in top-right & bottom-right quadrant
        """

        # define 4 collinear points, 1 in BR, 3 in TR
        #    P1-+-P2---P3---P4
        P1 = [ 1.0, -3.0]
        P2 = [ 5.0,  1.0]
        P3 = [ 6.0,  2.0]
        P4 = [ 7.0,  3.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 2 in BR, 2 in TR
        #    P1---P2-+-P3---P4
        P1 = [ 1.0, -3.0]
        P2 = [ 2.0, -2.0]
        P3 = [ 6.0,  2.0]
        P4 = [ 7.0,  3.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)

        # define 4 collinear points, 3 in BR, 1 in TR
        #    P1---P2---P3-+-P4
        P1 = [ 1.0, -3.0]
        P2 = [ 2.0, -2.0]
        P3 = [ 3.0, -1.0]
        P4 = [ 7.0,  3.0]
        self.helper_test_parallel_intersection_code(P1, P2, P3, P4)


    def test_intersection_direction_invariance(self):
        """This runs through a number of examples and checks that
        direction of lines don't matter.
        """

        line0 = [[0,0], [100,100]]

        common_end_point = [20, 150]

        for i in range(100):
            x = 20 + i * 1.0/100

            line1 = [[x,0], common_end_point]
            status, p1 = intersection(line0, line1)
            assert status == 1

            # Swap direction of line1
            line1 = [common_end_point, [x,0]]
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
        line0 = [[-1,1], [1,1]]
        line1 = [[0,-1], [0,0]]

        status, value = intersection(line0, line1)
        assert status == 0
        assert value is None

    def test_intersection_parallel(self):
        line0 = [[-1,1], [1,1]]
        line1 = [[-1,0], [5,0]]

        status, value = intersection(line0, line1)
        assert status == 4
        assert value is None

        line0 = [[0,0], [10,100]]
        line1 = [[-10,5], [0,105]]

        status, value = intersection(line0, line1)
        assert status == 4
        assert value is None

    def test_intersection_coincide(self):
        """Test what happens when two lines partly coincide"""

        # Overlap 1
        line0 = [[0,0], [5,0]]
        line1 = [[-3,0], [3,0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[0,0], [3,0]])

        # Overlap 2
        line0 = [[-10,0], [5,0]]
        line1 = [[-3,0], [10,0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[-3, 0], [5,0]])

        # Inclusion 1
        line0 = [[0,0], [5,0]]
        line1 = [[2,0], [3,0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, line1)

        # Inclusion 2
        line0 = [[1,0], [5,0]]
        line1 = [[-10,0], [15,0]]

        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, line0)

        # Exclusion (no intersection)
        line0 = [[-10,0], [1,0]]
        line1 = [[3,0], [15,0]]

        status, value = intersection(line0, line1)
        assert status == 3
        assert value is None

        # Try examples with some slope (y=2*x+5)

        # Overlap
        line0 = [[0,5], [7,19]]
        line1 = [[1,7], [10,25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        status, value = intersection(line1, line0)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        # Swap direction
        line0 = [[7,19], [0,5]]
        line1 = [[1,7], [10,25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[7, 19], [1, 7]])

        line0 = [[0,5], [7,19]]
        line1 = [[10,25], [1,7]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1, 7], [7, 19]])

        # Inclusion
        line0 = [[1,7], [7,19]]
        line1 = [[0,5], [10,25]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1,7], [7, 19]])

        line0 = [[0,5], [10,25]]
        line1 = [[1,7], [7,19]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[1,7], [7, 19]])

        line0 = [[0,5], [10,25]]
        line1 = [[7,19], [1,7]]
        status, value = intersection(line0, line1)
        assert status == 2
        assert num.allclose(value, [[7, 19], [1, 7]])


    def NOtest_inside_polygon_main(self):
        # FIXME (Ole): Why is this disabled?
        #print "inside",inside
        #print "outside",outside

        assert not inside_polygon((0.5, 1.5), polygon)
        assert not inside_polygon((0.5, -0.5), polygon)
        assert not inside_polygon((-0.5, 0.5), polygon)
        assert not inside_polygon((1.5, 0.5), polygon)

        # Try point on borders
        assert inside_polygon((1., 0.5), polygon, closed=True)
        assert inside_polygon((0.5, 1), polygon, closed=True)
        assert inside_polygon((0., 0.5), polygon, closed=True)
        assert inside_polygon((0.5, 0.), polygon, closed=True)

        assert not inside_polygon((0.5, 1), polygon, closed=False)
        assert not inside_polygon((0., 0.5), polygon, closed=False)
        assert not inside_polygon((0.5, 0.), polygon, closed=False)
        assert not inside_polygon((1., 0.5), polygon, closed=False)

        # From real example (that failed)
        polygon = [[20,20], [40,20], [40,40], [20,40]]
        points = [[40, 50]]
        res = inside_polygon(points, polygon)
        assert len(res) == 0

        polygon = [[20,20], [40,20], [40,40], [20,40]]
        points = [[25, 25], [30, 20], [40, 50], [90, 20], [40, 90]]
        res = inside_polygon(points, polygon)
        assert len(res) == 2
        assert num.allclose(res, [0,1])

    def test_polygon_area(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        assert polygon_area(polygon) == 1

        # Simple case: Polygon is a rectangle
        polygon = [[0,0], [1,0], [1,4], [0,4]]
        assert polygon_area(polygon) == 4

        # Simple case: Polygon is a unit triangle
        polygon = [[0,0], [1,0], [0,1]]
        assert polygon_area(polygon) == 0.5

        # Simple case: Polygon is a diamond
        polygon = [[0,0], [1,1], [2,0], [1, -1]]
        assert polygon_area(polygon) == 2.0

        # Complex case where numerical errors might occur
        polygon = [[314037.58727982, 6224952.2960092],
                   [314038.58727982, 6224952.2960092],
                   [314038.58727982, 6224953.2960092],
                   [314037.58727982, 6224953.2960092]]
        assert polygon_area(polygon) == 1.0

    def test_poly_xy(self):
        # Simplest case: Polygon is the unit square
        polygon = [[0,0], [1,0], [1,1], [0,1]]
        x, y = poly_xy(polygon)
        assert len(x) == len(polygon)+1
        assert len(y) == len(polygon)+1
        assert x[0] == 0
        assert x[1] == 1
        assert x[2] == 1
        assert x[3] == 0
        assert y[0] == 0
        assert y[1] == 0
        assert y[2] == 1
        assert y[3] == 1

    # Arbitrary polygon
        polygon = [[1,5], [1,1], [100,10], [1,10], [3,6]]
        x, y = poly_xy(polygon)
        assert len(x) == len(polygon)+1
        assert len(y) == len(polygon)+1
        assert x[0] == 1
        assert x[1] == 1
        assert x[2] == 100
        assert x[3] == 1
        assert x[4] == 3
        assert y[0] == 5
        assert y[1] == 1
        assert y[2] == 10
        assert y[3] == 10
        assert y[4] == 6

    # Disabled
    def xtest_plot_polygons(self):
        import os

        # Simplest case: Polygon is the unit square
        polygon1 = [[0,0], [1,0], [1,1], [0,1]]
        polygon2 = [[1,1], [2,1], [3,2], [2,2]]
        v = plot_polygons([polygon1, polygon2], 'test1')
        assert len(v) == 4
        assert v[0] == 0
        assert v[1] == 3
        assert v[2] == 0
        assert v[3] == 2

        # Another case
        polygon3 = [[1,5], [10,1], [100,10], [50,10], [3,6]]
        v = plot_polygons([polygon2,polygon3], 'test2')
        assert len(v) == 4
        assert v[0] == 1
        assert v[1] == 100
        assert v[2] == 1
        assert v[3] == 10

        os.remove('test1.png')
        os.remove('test2.png')

    def test_inside_polygon_geospatial(self):
        #Simplest case: Polygon is the unit square
        polygon_absolute = [[0,0], [1,0], [1,1], [0,1]]
        poly_geo_ref = Geo_reference(57, 100, 100)
        polygon = poly_geo_ref.change_points_geo_ref(polygon_absolute)
        poly_spatial = Geospatial_data(polygon, geo_reference=poly_geo_ref)

        points_absolute = (0.5, 0.5)
        points_geo_ref = Geo_reference(57, 78, -56)
        points = points_geo_ref.change_points_geo_ref(points_absolute)
        points_spatial = Geospatial_data(points, geo_reference=points_geo_ref)

        assert is_inside_polygon(points_absolute, polygon_absolute)
        assert is_inside_polygon(ensure_numeric(points_absolute),
                                 ensure_numeric(polygon_absolute))
        assert is_inside_polygon(points_absolute, poly_spatial)
        assert is_inside_polygon(points_spatial, poly_spatial)
        assert is_inside_polygon(points_spatial, polygon_absolute)

        assert is_inside_polygon(points_absolute, polygon_absolute)

    def NOtest_decimate_polygon(self):
        polygon = [[0,0], [10,10], [15,5], [20, 10],
                   [25,0], [30,10], [40,-10], [35, -5]]

        dpoly = decimate_polygon(polygon, factor=2)

        print dpoly

        assert len(dpoly)*2==len(polygon)

        minx = maxx = polygon[0][0]
        miny = maxy = polygon[0][1]
        for point in polygon[1:]:
            x, y = point

            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y

        assert [minx, miny] in polygon
        print minx, maxy
        assert [minx, maxy] in polygon
        assert [maxx, miny] in polygon
        assert [maxx, maxy] in polygon

    def test_interpolate_polyline(self):
        """test_interpolate_polyline(self):

        This test is added under the assumption that the function
        interpolate_polyline implemented by John Jakeman works.
        It has been exercised somewhat by tests of sts boundary,
        but never before separately.
        """

        f = num.array([58.06150614, 58.06150614, 58.06150614])
        vertex_coordinates = num.array([[0., 0., ],
                                        [4.04092634, 1106.11074699],
                                        [8.08836552, 2212.16910609]])
        gauge_neighbour_id = [1, 2, -1]
        point_coordinates = num.array([[2.21870766e+03, 1.09802864e+03],
                                       [1.62739645e+03, 2.20626983e+03],
                                       [5.20084967e+02, 2.21030386e+03],
                                       [6.06464546e+00, 1.65913993e+03],
                                       [1.61934862e+03, -5.88143836e+00],
                                       [5.11996623e+02, -1.85956061e+00],
                                       [2.02046270e+00, 5.53055373e+02]])

        z_ref = [0., 0., 0., 58.06150614, 0., 0., 58.06150614]

        z = interpolate_polyline(f, vertex_coordinates,
                                 gauge_neighbour_id, point_coordinates)
        assert num.allclose(z, z_ref)

        # Another f
        f = num.array([58.06150614, 158.06150614, 258.06150614])
        z_ref = [0., 0., 0., 208.06150645, 0., 0., 108.0615061]
        z = interpolate_polyline(f, vertex_coordinates,
                                 gauge_neighbour_id, point_coordinates)
        assert num.allclose(z, z_ref)

        # Other and simpler numbers
        f = num.array([1, 5, 13])
        vertex_coordinates = num.array([[0., 0., ],
                                        [4., 4.],
                                        [8., 8.]])
        point_coordinates = num.array([[0.1, 0.1],
                                       [3.5, 3.5],
                                       [4.0, 4.0],
                                       [5.2, 5.2],
                                       [7.0, 7.0],
                                       [8.3, 8.3]])
        gauge_neighbour_id = [1, 2, -1]

        z = interpolate_polyline(f, vertex_coordinates,
                                 gauge_neighbour_id, point_coordinates)
        z_ref = [1.1, 4.5, 5., 7.4, 11., 0.]
        assert num.allclose(z, z_ref)

        # Test exception thrown for one point
        f = num.array([5])
        vertex_coordinates = num.array([[4., 4.]])
        try:
            z = interpolate_polyline(f, vertex_coordinates,
                                     gauge_neighbour_id, point_coordinates)
        except Exception:
            pass
        else:
            raise Exception, 'One point should have raised exception'

        # More polyline nodes
        data = num.array([1, 5, 13, 12, 6, 29])
        polyline_nodes = num.array([[0., 0.],
                                    [4., 4.],
                                    [8., 8.],
                                    [10., 10.],
                                    [10., 5.],
                                    [10., 0.]])
        point_coordinates = num.array([[0.1, 0.1],
                                       [3.5, 3.5],
                                       [4.0, 4.0],
                                       [5.2, 5.2],
                                       [7.0, 7.0],
                                       [8.3, 8.3],
                                       [10., 10.],
                                       [10., 9.],
                                       [10., 7.1],
                                       [10., 4.3],
                                       [10., 1.0]])
        gauge_neighbour_id = [1, 2, 3, 4, 5, -1]
        z = interpolate_polyline(data, polyline_nodes,
                                 gauge_neighbour_id, point_coordinates)
        z_ref = [1.1, 4.5, 5., 7.4, 11., 12.85, 12., 10.8, 8.52, 9.22, 24.4]
        assert num.allclose(z, z_ref)


    def test_is_inside_triangle_more(self):

        res = is_inside_triangle([0.5, 0.5], [[ 0.5,  0. ],
                                              [ 0.5,  0.5],
                                              [ 0.,   0. ]])
        assert res is True

        res = is_inside_triangle([0.59999999999999998, 0.29999999999999999],
                                 [[ 0.5,  0. ], [ 0.5, 0.5], [0., 0.]])
        assert res is False

        res = is_inside_triangle([0.59999999999999998, 0.29999999999999999],
                                 [[1., 0.], [1., 0.5], [0.5, 0.]])
        assert res is False


        res = is_inside_triangle([0.59999999999999998, 0.29999999999999999],
                                 [[0.5, 0.5], [0.5, 0.], [1., 0.5]])
        assert res is True


        res = is_inside_triangle([0.10000000000000001, 0.20000000000000001],
                                 [[0.5, 0.], [0.5, 0.5], [0., 0.]])
        assert res is False


        res = is_inside_triangle([0.10000000000000001, 0.20000000000000001],
                                 [[0., 0.5], [0., 0.], [0.5, 0.5]])
        assert res is True

        res = is_inside_triangle([0.69999999999999996, 0.69999999999999996],
                                 [[0.5, 0.], [0.5, 0.5], [0., 0.]])
        assert res is False

        res = is_inside_triangle([0.59999999999999998, 0.29999999999999999],
                                 [[0.25, 0.5], [0.25, 0.25], [0.5, 0.5]])
        assert res is False


        res = is_inside_triangle([10, 3],
                                 [[0.1, 0.],
                                  [0.1, 0.08333333],
                                  [0., 0.]])
        assert res is False

################################################################################

if __name__ == "__main__":
    suite = unittest.makeSuite(Test_Polygon,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
