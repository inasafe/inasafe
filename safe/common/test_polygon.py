import unittest
import numpy

from safe.storage.vector import Vector
from safe.storage.raster import Raster
from safe.storage.geometry import Polygon
from safe.common.polygon import (separate_points_by_polygon,
                                 is_inside_polygon,
                                 is_outside_polygon,
                                 point_on_line,
                                 outside_polygon,
                                 inside_polygon,
                                 clip_lines_by_polygon,
                                 clip_lines_by_polygons,
                                 in_and_outside_polygon,
                                 intersection,
                                 join_line_segments,
                                 clip_line_by_polygon,
                                 clip_grid_by_polygons,
                                 populate_polygon,
                                 generate_random_points_in_bbox,
                                 PolygonInputError,
                                 line_dictionary_to_geometry)
from safe.common.testing import test_polygon, test_lines
from safe.common.numerics import ensure_numeric


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
        assert is_inside_polygon((5.5, 5.5), polygon)

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

    def test_separate_points_by_polygon0(self):
        """Points can be separated by polygon
        """

        # Now try the vector formulation returning indices
        polygon = [[0, 0], [1, 0], [0.5, -1], [2, -1], [2, 1], [0, 1]]
        points = [[0.5, 0.5], [1, -0.5], [1.5, 0], [0.5, 1.5], [0.5, -0.5]]

        inside, outside = separate_points_by_polygon(points, polygon)

        assert len(inside) + len(outside) == len(points)
        assert numpy.allclose(inside, [0, 1, 2])
        assert numpy.allclose(outside, [3, 4])

    def test_separate_points_by_polygon_empty_points(self):
        """Separate points by polygon ok when no points in bbox
        """

        # This is from a real example that failed
        polygon = numpy.array([[109.82203092, -7.22977256],
                               [109.82224507, -7.22986774],
                               [109.82255440, -7.22974876],
                               [109.82272096, -7.22960600],
                               [109.82283994, -7.22929667],
                               [109.82283994, -7.22884457],
                               [109.82272096, -7.22860662],
                               [109.82248302, -7.22841627],
                               [109.82241163, -7.22822591],
                               [109.82224507, -7.22822591],
                               [109.82210230, -7.22841627],
                               [109.82191195, -7.22860662],
                               [109.82179297, -7.22872560],
                               [109.82169779, -7.22882077],
                               [109.82172159, -7.22917769],
                               [109.82176918, -7.22932046],
                               [109.82188815, -7.22953461],
                               [109.82203092, -7.22977256]])
        points = numpy.zeros((0, 2))
        separate_points_by_polygon(points, polygon)

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
                                                      [0.1, 0.6]],
                                                     U,
                                                     closed=True)
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        inside, outside = separate_points_by_polygon([[0, 0.5],
                                                      [0.3, 0.3],
                                                      [0.1, 0.6]],
                                                     U,
                                                     closed=False)
        assert len(inside) == 2
        assert numpy.allclose(inside, [1, 2])

        # Try with boundary (horizontal edge) point
        inside, outside = separate_points_by_polygon([[0.5, 0.0],
                                                      [0.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(outside) == 0
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        # Try with boundary (corner) point
        inside, outside = separate_points_by_polygon([[0.0, 0.0],
                                                      [0.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(outside) == 0
        assert len(inside) == 3
        assert numpy.allclose(inside, [0, 1, 2])

        # One outside
        inside, outside = separate_points_by_polygon([[0, 0.5],
                                                      [1.3, 0.3],
                                                      [0.1, 0.6]], U)
        assert len(outside) == 1
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
        except PolygonInputError:
            pass
        else:
            msg = 'Should have raised PolygonInputError:'
            raise Exception(msg)

        try:
            outside_polygon('Hmmm', U)
        except PolygonInputError:
            pass
        else:
            msg = 'Should have raised PolygonInputError'
            raise Exception(msg)

        try:
            inside_polygon(points, U, closed=7)
        except PolygonInputError:
            pass
        else:
            msg = 'Should have raised PolygonInputError'
            raise Exception(msg)

    def test_clip_grid_by_polygon(self):
        """Regular grids can be clipped by polygons (with holes)
        """
        # Define an outer ring
        outer_ring = numpy.array([[106.79, -6.233],
                                  [106.80, -6.24],
                                  [106.78, -6.23],
                                  [106.77, -6.21],
                                  [106.79, -6.233]])

        # Define inner rings
        inner_rings = [numpy.array([[106.77827, -6.2252],
                                    [106.77775, -6.22378],
                                    [106.78, -6.22311],
                                    [106.78017, -6.22530],
                                    [106.77827, -6.2252]]),
                       numpy.array([[106.78652, -6.23215],
                                    [106.78642, -6.23075],
                                    [106.78746, -6.23143],
                                    [106.78831, -6.23307],
                                    [106.78652, -6.23215]])]

        # Make a grid
        N = 10
        A = numpy.arange(N * N).reshape((N, N))
        # Longitudes
        minx = min(outer_ring[:, 0])
        maxx = max(outer_ring[:, 0])
        dx = (maxx - minx) / N

        # Latitudes
        miny = min(outer_ring[:, 1])
        maxy = max(outer_ring[:, 1])
        dy = -(maxy - miny) / N

        #top left x, w-e pixel res, rot, top left y, rot, n-s pixel res
        #(lon_ul, dlon, 0, lat_ul, 0, dlat)
        geotransform = (minx, dx, 0, maxy, 0, dy)

        # Create suitable instance on the fly
        # See
        # http://docs.python.org/library/functions.html#type
        # http://jjinux.blogspot.com/2005/03/
        #      python-create-new-class-on-fly.html
        polygon_arg = [type('', (),
                            dict(outer_ring=outer_ring,
                                 inner_rings=inner_rings))()]

        # Call clipping function
        res = clip_grid_by_polygons(A, geotransform,
                                    polygon_arg)

        points = res[0][0]
        values = res[0][1]
        values = [{'val': float(x)} for x in values]

        # Check correctness (from QGIS inspection)
        assert numpy.allclose(points[0], [106.7745, -6.2175])
        assert numpy.allclose(points[3], [106.7805, -6.2235])
        assert numpy.allclose(points[9], [106.7865, -6.2325])
        assert values[0]['val'] == 21
        assert values[3]['val'] == 43
        assert values[9]['val'] == 75

        # Optionally store output for inspection with QGIS (this one is nice)
        if False:
            R = Raster(A, geotransform=geotransform)
            R.write_to_file('test_raster.tif')
            P = Vector(geometry=[Polygon(outer_ring=outer_ring,
                                         inner_rings=inner_rings)])
            P.write_to_file('test_polygon.shp')
            Vector(geometry=points,
                   data=values).write_to_file('test_points.shp')

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

    test_populate_polygon_with_exclude.slow = True

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

    test_populate_polygon_with_exclude2.slow = True

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

    test_large_example.slow = True

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

    test_large_convoluted_example.slow = True

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

    test_large_convoluted_example_random.slow = True

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

    def test_clip_points_by_polygons_with_holes(self):
        """Points can be separated by polygons with holes
        """

        # Define an outer ring
        outer_ring = numpy.array([[106.79, -6.233],
                                  [106.80, -6.24],
                                  [106.78, -6.23],
                                  [106.77, -6.21],
                                  [106.79, -6.233]])

        # Define inner rings
        inner_rings = [numpy.array([[106.77827, -6.2252],
                                    [106.77775, -6.22378],
                                    [106.78, -6.22311],
                                    [106.78017, -6.22530],
                                    [106.77827, -6.2252]]),
                       numpy.array([[106.78652, -6.23215],
                                    [106.78642, -6.23075],
                                    [106.78746, -6.23143],
                                    [106.78831, -6.23307],
                                    [106.78652, -6.23215]])]

        # Make some test points
        points = generate_random_points_in_bbox(outer_ring, 1000, seed=13)

        # Clip to outer ring, excluding holes
        inside, outside = in_and_outside_polygon(points, outer_ring,
                                                 holes=inner_rings)

        # Check wrapper functions
        assert numpy.all(inside == inside_polygon(points, outer_ring,
                                                  holes=inner_rings))
        assert numpy.all(outside == outside_polygon(points, outer_ring,
                                                    holes=inner_rings))

        # Verify that each point is where it should
        for point in points[inside, :]:
            # Must be inside outer ring
            assert is_inside_polygon(point, outer_ring)

            # But not in any of the inner rings
            assert not is_inside_polygon(point, inner_rings[0])
            assert not is_inside_polygon(point, inner_rings[1])

        for point in points[outside, :]:
            # Must be either outside outer ring or inside a hole
            assert (is_outside_polygon(point, outer_ring) or
                    is_inside_polygon(point, inner_rings[0]) or
                    is_inside_polygon(point, inner_rings[1]))

    def test_intersection1(self):
        """Intersection of two simple lines works
        """

        line0 = [[-1, 0], [1, 0]]
        line1 = [[0, -1], [0, 1]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [0.0, 0.0])

    def test_intersection2(self):
        """Intersection point is independent of direction
        """

        line0 = [[0, 0], [24, 12]]
        line1 = [[0, 12], [24, 0]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [12.0, 6.0])

        # Swap direction of one line
        line1 = [[24, 0], [0, 12]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [12.0, 6.0])

        # Swap order of lines
        value = intersection(line1, line0)
        assert numpy.allclose(value, [12.0, 6.0])

    def test_intersection3(self):
        """Intersection point is independent of direction (2)
        """

        line0 = [[0, 0], [24, 12]]
        line1 = [[0, 17], [24, 0]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [14.068965517, 7.0344827586])

        # Swap direction of one line
        line1 = [[24, 0], [0, 17]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [14.068965517, 7.0344827586])

        # Swap order of lines
        value = intersection(line1, line0)
        assert numpy.allclose(value, [14.068965517, 7.0344827586])

    def test_intersection_endpoints(self):
        """Intersection of lines with coinciding endpoints works

        Test that coinciding endpoints are picked up
        """

        line0 = [[0, 0], [1, 1]]
        line1 = [[1, 1], [2, 1]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [1.0, 1.0])

        line0 = [[1, 1], [2, 0]]
        line1 = [[1, 1], [2, 1]]

        value = intersection(line0, line1)
        assert numpy.allclose(value, [1.0, 1.0])

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
            p1 = intersection(line0, line1)

            # Swap direction of line1
            line1 = [common_end_point, [x, 0]]
            p2 = intersection(line0, line1)

            msg = ('Orientation of line should not matter.\n'
                   'However, segment [%f,%f], [%f, %f]' %
                   (x, 0, common_end_point[0], common_end_point[1]))
            msg += ' gave %s, \nbut when reversed we got %s' % (p1, p2)
            assert numpy.allclose(p1, p2), msg

            # Swap order of lines
            p3 = intersection(line1, line0)
            msg = 'Order of lines gave different results'
            assert numpy.allclose(p1, p3), msg

    test_intersection_direction_invariance.slow = True

    def test_no_intersection(self):
        """Lines that don't intersect return None as expected
        """

        line0 = [[-1, 1], [1, 1]]
        line1 = [[0, -1], [0, 0]]

        value = intersection(line0, line1)
        assert value is None

    def test_vectorised_intersection1(self):
        """Vectorised intersection of multiple lines works 1
        """

        line0 = [[0, 0], [24, 12]]

        # One way of building the array
        line1 = numpy.zeros(16).reshape(2, 2, 4)  # Three lines
        line1[0, 0, :] = [0, 24, 0, 15]   # x0
        line1[0, 1, :] = [12, 0, 24, 0]   # y0
        line1[1, 0, :] = [24, 0, 0, 5]    # x1
        line1[1, 1, :] = [0, 12, 12, 15]  # y1

        value = intersection(line0, line1)
        mask = - numpy.isnan(value[:, 0])
        v = value[mask]
        assert numpy.allclose(v,
                              [[12.0, 6.0],
                               [12.0, 6.0],
                               [11.25, 5.625]])

        # A more direct way of building the array
        line1 = [[[0, 24, 0, 15],    # x0
                  [12, 0, 24, 0]],   # y0
                 [[24, 0, 0, 5],     # x1
                  [0, 12, 12, 15]]]  # y1

        value = intersection(line0, line1)
        mask = - numpy.isnan(value[:, 0])
        v = value[mask]
        assert numpy.allclose(v,
                              [[12.0, 6.0],
                               [12.0, 6.0],
                               [11.25, 5.625]])

    def test_vectorised_intersection2(self):
        """Vectorised intersection of multiple lines works 2
        """

        # Common line segment to intersect with
        line0 = [[0, 0], [100, 100]]

        # Vectorised collection of line arguments
        N = 15  # Line 0 to 10 will intersect, 11 - 14 won't
        line1 = numpy.zeros(4 * N, numpy.float).reshape(2, 2, N)
        x0 = numpy.arange(N) * 10
        y0 = numpy.zeros(N)
        x1 = numpy.arange(N) * 10
        y1 = numpy.ones(N) * 100
        line1[0, 0, :] = x0
        line1[0, 1, :] = y0
        line1[1, 0, :] = x1
        line1[1, 1, :] = y1

        value = intersection(line0, line1)
        assert len(value.shape) == 2
        assert value.shape[0] == N
        assert value.shape[1] == 2

        for i in range(0, 11):
            assert value[i, 0] == i * 10

        for i in range(11, 15):
            assert numpy.all(numpy.isnan(value[i]))

    def test_intersection_parallel(self):
        """Parallel lines are correctly detected in intersection code
        """

        line0 = [[-1, 1], [1, 1]]
        line1 = [[-1, 0], [5, 0]]

        value = intersection(line0, line1)
        assert value is None

        line0 = [[0, 0], [10, 100]]
        line1 = [[-10, 5], [0, 105]]

        value = intersection(line0, line1)
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
        line = [[-1, 1], [2, 1]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[0, 1], [1, 1]]])

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
        line = [[1, -1], [1, 2]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_line_segments,
                              [[[1, 0], [1, 1]]])

        assert numpy.allclose(outside_line_segments,
                              [[[1, -1], [1, 0]],
                               [[1, 1], [1, 2]]])

        # Simple sloping fully intersecting line
        line = [[-1, 0.0], [2, 1.0]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[0, 1.0 / 3], [1, 2.0 / 3]]])

        assert numpy.allclose(outside_lines,
                              [[[-1, 0], [0, 1.0 / 3]],
                               [[1, 2.0 / 3], [2, 1]]])

        # Simple sloping line coinciding with one edge, intersecting another
        line = [[-1, 0.0], [1, 2.0 / 3]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[0, 1.0 / 3], [1, 2.0 / 3]]])

        assert numpy.allclose(outside_lines,
                              [[[-1, 0], [0, 1.0 / 3]]])

        # Diagonal line intersecting corners
        line = [[-1, -1], [2, 2]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[0, 0], [1, 1]]])

        assert numpy.allclose(outside_lines,
                              [[[-1, -1], [0, 0]],
                               [[1, 1], [2, 2]]])

        # Diagonal line intersecting corners - other way
        line = [[-1, 2], [2, -1]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[0, 1], [1, 0]]])

        assert numpy.allclose(outside_lines,
                              [[[-1, 2], [0, 1]],
                               [[1, 0], [2, -1]]])

        # Diagonal line coinciding with one corner
        line = [[-1, -1], [1, 1]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[0, 0], [1, 1]]])

        assert numpy.allclose(outside_lines,
                              [[[-1, -1], [0, 0]]])

        # Very convoluted polygon
        polygon = [[0, 0], [10, 10], [15, 5], [20, 10], [25, 0],
                   [30, 10], [40, -10]]

        line = [[-10, 6], [60, 6]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[6, 6], [14, 6]],
                               [[16, 6.], [22, 6]],
                               [[28, 6], [32, 6]]])
        assert numpy.allclose(outside_lines,
                              [[[-10, 6], [6, 6]], [[14, 6], [16, 6]],
                              [[22, 6], [28, 6]], [[32, 6], [60, 6]]])

    def test_clip_line_by_polygon_already_inside(self):
        """Polygon line clipping works for special cases
        """

        line = [[1.5, 0.5], [2.5, 0.5]]
        polygon = [[1, 0], [3, 0], [2, 1]]

        # Assert that this line is fully inside polygon
        inside, outside = clip_line_by_polygon(line, polygon)
        assert len(outside) == 0
        assert len(inside) > 0

    def test_clip_composite_lines_by_polygon(self):
        """Composite lines are clipped and classified by polygon
        """

        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # One line with same two segments changing direction inside polygon
        line = [[-1, 0.5], [0.5, 0.5], [0.5, 2]]

        inside_lines, outside_lines = \
            clip_line_by_polygon(line, polygon)

        assert numpy.allclose(inside_lines,
                              [[[0, 0.5], [0.5, 0.5], [0.5, 1]]])

        assert numpy.allclose(outside_lines,
                             [[[-1, 0.5], [0, 0.5]],
                               [[0.5, 1], [0.5, 2]]])

        # One line with multiple segments both inside and outside polygon
        line = [[-1, 0.5], [-0.5, 0.5], [0.5, 0.5],
                [1.0, 0.5], [1.5, 0.5], [2.0, 0.5]]

        inside_lines, outside_lines = clip_line_by_polygon(line, polygon)
        assert len(inside_lines) == 1
        assert numpy.allclose(inside_lines,
                              [[0, 0.5], [0.5, 0.5], [1.0, 0.5]])

    def test_clip_lines_by_polygon_multi(self):
        """Multiple composite lines are clipped and classified by polygon
        """

        # Simplest case: Polygon is the unit square
        polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

        # Two lines changing direction inside polygon
        lines = [[[-1, 0.5], [0.5, 0.5]],
                 [[0.5, 0.5], [0.5, 2]]]

        inside_lines, outside_lines = clip_lines_by_polygon(lines, polygon)

        assert numpy.allclose(inside_lines[0], [[0, 0.5], [0.5, 0.5]])
        assert numpy.allclose(inside_lines[1], [[0.5, 0.5], [0.5, 1]])

        assert numpy.allclose(outside_lines[0], [[-1, 0.5], [0, 0.5]])
        assert numpy.allclose(outside_lines[1], [[0.5, 1], [0.5, 2]])

        # Multiple lines with different number of segments
        lines = [[[-1, 0.5], [0.5, 0.5], [0.5, 2]],
                 [[-1, 0.0], [1, 2.0 / 3]]]

        inside_lines, outside_lines = \
            clip_lines_by_polygon(lines, polygon, check_input=True)

        assert len(inside_lines) == 2
        assert len(outside_lines) == 2

        for _, values in inside_lines.items():
            for line in values:
                assert type(line) == numpy.ndarray
                assert len(line.shape) == 2
                assert line.shape[1] == 2

        for _, values in outside_lines.items():
            for line in values:
                assert type(line) == numpy.ndarray
                assert len(line.shape) == 2
                assert line.shape[1] == 2

        assert numpy.allclose(inside_lines[0],
                              [[[0, 0.5], [0.5, 0.5], [0.5, 1]]])
        assert numpy.allclose(inside_lines[1],
                              [[[0, 1.0 / 3], [1, 2.0 / 3]]])

        assert numpy.allclose(outside_lines[0],
                              [[[-1, 0.5], [0, 0.5]],
                               [[0.5, 1], [0.5, 2]]])  # Two lines
        assert numpy.allclose(outside_lines[1], [[-1, 0], [0, 1.0 / 3]])

        # Test that lines dictionaries convert to geometries
        # (lists of Nx2 arrays)
        inside_geo = line_dictionary_to_geometry(inside_lines)
        outside_geo = line_dictionary_to_geometry(outside_lines)

        for line in inside_geo + outside_geo:
            assert type(line) == numpy.ndarray
            assert len(line.shape) == 2
            assert line.shape[1] == 2

        assert numpy.allclose(inside_geo[0],
                              [[0, 0.5], [0.5, 0.5], [0.5, 1]])

        assert numpy.allclose(inside_geo[1],
                               [[0, 1.0 / 3], [1, 2.0 / 3]])

        assert numpy.allclose(outside_geo,
                              [[[-1, 0.5], [0, 0.5]],
                               [[0.5, 1], [0.5, 2]],
                               [[-1, 0], [0, 1.0 / 3]]])

    def test_clip_lines_by_multiple_polygons(self):
        """Multiple composite lines are clipped by multiple polygons
        """

        # Test polys
        polygons = [[[0, 0], [1, 0], [1, 1], [0, 1]],  # Unit square
                    [[1, 0], [3, 0], [2, 1]],  # Adjacent triangle
                    [[0, 3], [1, 3], [0.5, 2],
                     [2, 2], [2, 4], [0, 4]],  # Convoluted
                    [[-1, -1], [5, -1], [5, 3], [5, 3]],  # Overlapping
                    [[-1, -1], [6, -1], [6, 6], [6, 6]]]  # Cover the others

        # Test lines
        input_lines = [[[0, 0.5], [4, 0.5]],
                       [[2, 0], [2, 5]],
                       [[0, 0], [5, 5]],
                       [[10, 10], [30, 10]],
                       [[-1, 0.5], [0.5, 0.5], [2.5, 3]],
                       [[0.5, 0.5], [0.5, 2]],
                       [[100, 100], [300, 100]],
                       [[0.3, 0.2], [0.7, 3], [1.0, 1.9]],
                       [[30, 10], [30, 20]]]

        #Vector(geometry=polygons).write_to_file('multiple_polygons.shp')
        #Vector(geometry=input_lines,
        #       geometry_type='line').write_to_file('input_lines.shp')
        lines_covered = clip_lines_by_polygons(input_lines, polygons)

        # Sanity checks
        assert len(lines_covered) == len(polygons)

        i = 0
        for lines in lines_covered:
            #filename = 'clipped_lines_%i.shp' % i
            #Vector(geometry=line_dictionary_to_geometry(lines),
            #       geometry_type='line').write_to_file(filename)
            i += 1

            assert len(lines) == len(input_lines)

        # Thorough check of all lines
        for i, polygon in enumerate(polygons):

            lines_in_polygon = lines_covered[i]
            for key in lines_in_polygon:
                for line in lines_covered[i][key]:

                    # Assert that this line is fully inside polygon
                    inside, outside = clip_line_by_polygon(line, polygon)
                    assert len(outside) == 0

                    # Line can be joined from separate segments but
                    # endpoints must match
                    for x in inside:
                        assert numpy.allclose(x[0], line[0])
                        assert numpy.allclose(x[-1], line[-1])

        # Spot checks

        # Polygon 2, line 1
        assert numpy.allclose(lines_covered[2][1][0],
                              [[2., 2.],
                               [2., 4.]])

        # Polygon 4, line 2
        # This one will fail if we ignore points_on_line check
        assert numpy.allclose(lines_covered[4][2][0],
                              [[0., 0.],
                               [5., 5.]])

        # Polygon 4, line 7
        assert numpy.allclose(lines_covered[4][7][0],
                              [[0.3, 0.2],
                               [0.31666667, 0.31666667]])

    def test_clip_lines_by_polygon_real_data(self):
        """Real roads are clipped by complex polygon
        """

        inside_lines, outside_lines = \
            clip_lines_by_polygon(test_lines, test_polygon,
                                  check_input=True)

        # Convert dictionaries to lists of lines
        inside_line_segments = line_dictionary_to_geometry(inside_lines)
        outside_line_segments = line_dictionary_to_geometry(outside_lines)

        # These lines have compontes both inside and outside
        assert len(inside_line_segments) == 13
        assert len(outside_line_segments) == 17

        # Store for visual inspection by e.g. QGis
        # Set to True, run test and do
        # qgis test_polygon.shp test_lines.shp in_segments.shp out_segments.shp
        if False:
            Vector(geometry=[test_polygon],
                   geometry_type='polygon').write_to_file('test_polygon.shp')
            Vector(geometry=test_lines,
                   geometry_type='line').write_to_file('test_lines.shp')
            Vector(geometry=inside_line_segments,
                   geometry_type='line').write_to_file('in_segments.shp')
            Vector(geometry=outside_line_segments,
                   geometry_type='line').write_to_file('out_segments.shp')

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

        # Check dictionaries directly (same data):
        assert len(inside_lines) == 6
        assert len(outside_lines) == 6
        assert numpy.allclose(inside_lines[0][0],
                              [[122.23028405, -8.62598333],
                               [122.22879, -8.624855],
                               [122.22776827, -8.62420644]])

        assert numpy.allclose(inside_lines[5][0],
                              [[122.247938, -8.632926],
                               [122.24793987, -8.63351817]])

        assert numpy.allclose(outside_lines[0][0],
                              [[122.231021, -8.626557],
                               [122.230563, -8.626194],
                               [122.23028405, -8.62598333]])

        assert numpy.allclose(outside_lines[0][1],
                              [[122.22776827, -8.62420644],
                               [122.227536, -8.624059],
                               [122.226648, -8.623494],
                               [122.225775, -8.623022],
                               [122.224872, -8.622444],
                               [122.22423, -8.6221],
                               [122.221931, -8.621082],
                               [122.2217, -8.62098],
                               [122.220577, -8.620555],
                               [122.21958, -8.62103]])

        assert numpy.allclose(outside_lines[5][0],
                              [[122.24793987, -8.63351817],
                               [122.24794, -8.63356],
                               [122.24739, -8.63622]])

    test_clip_lines_by_polygon_real_data.slow = True

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
