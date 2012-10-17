"""**Polygon, line and point algorithms.**

.. tip::
   The main public functions are:
    separate_points_by_polygon: Fundamental clipper
    intersection: Determine intersections of lines

   Some more specific or helper functions include:
    inside_polygon
    is_inside_polygon
    outside_polygon
    is_outside_polygon
    point_on_line

"""

__author__ = 'Ole Nielsen <ole.moller.nielsen@gmail.com>'
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '01/11/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import logging
import numpy
from random import uniform, seed as seed_function

from safe.common.numerics import ensure_numeric
from safe.common.numerics import grid2points, geotransform2axes
from safe.common.exceptions import PolygonInputError, InaSAFEError

LOGGER = logging.getLogger('InaSAFE')


def separate_points_by_polygon(points, polygon,
                               polygon_bbox=None,
                               closed=True,
                               check_input=True,
                               use_numpy=True):
    """Determine whether points are inside or outside a polygon.

    Args:
        * points: Tuple of (x, y) coordinates, or list of tuples
        * polygon: list or Nx2 array of polygon vertices
        * polygon_bbox: (optional) bounding box for polygon
        * closed: (optional) determine whether points on boundary should be
              regarded as belonging to the polygon (closed = True)
              or not (closed = False). If None, boundary is left undefined,
              i.e. some points on boundary may be deemed to be inside while
              others may be deemed to be outside. This options makes
              the code faster.
        * check_input: Allows faster execution if set to False
        * use_numpy: Use the fast numpy implementation

    Returns:
        * indices_inside_polygon: array of indices of points
              falling inside the polygon
        * indices_outside_polygon: array of indices of points
              falling outside the polygon

    Raises: A generic Exception is raised for unexpected input.

    Example:

        U = [[0,0], [1,0], [1,1], [0,1]]  # Unit square
        separate_points_by_polygon( [[0.5, 0.5], [1, -0.5], [0.3, 0.2]], U)

        will return the indices [0, 2, 1] and count == 2 as only the first
        and the last point are inside the unit square

    Remarks:
        The vertices may be listed clockwise or counterclockwise and
        the first point may optionally be repeated.
        Polygons do not need to be convex.
        Polygons can have holes in them and points inside a hole is
        regarded as being outside the polygon.

    Algorithm is based on work by Darel Finley,
    http://www.alienryderflex.com/polygon/
    """

    # FIXME (Ole): Make sure bounding box here follows same format as
    #              those returned by layers. Methinks they don't at the moment
    if check_input:
        # Input checks
        msg = 'Keyword argument "closed" must be boolean or None'
        if not (isinstance(closed, bool) or closed is None):
            raise PolygonInputError(msg)

        try:
            points = ensure_numeric(points, numpy.float)
        except Exception, e:
            msg = ('Points could not be converted to numeric array: %s'
                   % str(e))
            raise PolygonInputError(msg)

        try:
            polygon = ensure_numeric(polygon, numpy.float)
        except Exception, e:
            msg = ('Polygon could not be converted to numeric array: %s'
                   % str(e))
            raise PolygonInputError(msg)

        msg = 'Polygon array must be a 2d array of vertices'
        if len(polygon.shape) != 2:
            raise PolygonInputError(msg)

        msg = 'Polygon array must have two columns'
        if polygon.shape[1] != 2:
            raise PolygonInputError(msg)

        msg = ('Points array must be 1 or 2 dimensional. '
               'I got %d dimensions: %s' % (len(points.shape), points))
        if not 0 < len(points.shape) < 3:
            raise PolygonInputError(msg)

        if len(points.shape) == 1:
            # Only one point was passed in. Convert to array of points.
            points = numpy.reshape(points, (1, 2))

        msg = ('Point array must have two columns (x,y), '
               'I got points.shape[1]=%d' % points.shape[0])
        if points.shape[1] != 2:
            raise PolygonInputError(msg)

        msg = ('Points array must be a 2d array. I got %s...'
               % str(points[:30]))
        if len(points.shape) != 2:
            raise PolygonInputError(msg)

        msg = 'Points array must have two columns'
        if points.shape[1] != 2:
            raise PolygonInputError(msg)

    # If there are no points return two 0-vectors
    if points.shape[0] == 0:
        return numpy.arange(0), numpy.arange(0)

    # Get polygon extents to rule out segments that
    # are outside its bounding box. This is a very important
    # optimisation
    if polygon_bbox is None:
        minpx = min(polygon[:, 0])
        maxpx = max(polygon[:, 0])
        minpy = min(polygon[:, 1])
        maxpy = max(polygon[:, 1])
        polygon_bbox = [minpx, maxpx, minpy, maxpy]
    else:
        minpx = polygon_bbox[0]
        maxpx = polygon_bbox[1]
        minpy = polygon_bbox[2]
        maxpy = polygon_bbox[3]

    x = points[:, 0]
    y = points[:, 1]

    # Only work on those that are inside polygon bounding box
    outside_box = (x > maxpx) + (x < minpx) + (y > maxpy) + (y < minpy)
    inside_box = -outside_box
    candidate_points = points[inside_box]

    if use_numpy:
        func = _separate_points_by_polygon
    else:
        func = _separate_points_by_polygon_python

    local_indices_inside, local_indices_outside = func(candidate_points,
                                                       polygon,
                                                       closed=closed)

    # Map local indices from candidate points to global indices of all points
    indices_outside_box = numpy.where(outside_box)[0]
    indices_inside_box = numpy.where(inside_box)[0]

    indices_inside_polygon = indices_inside_box[local_indices_inside]
    indices_in_box_outside_poly = indices_inside_box[local_indices_outside]
    indices_outside_polygon = numpy.concatenate((indices_outside_box,
                                                 indices_in_box_outside_poly))

    indices_outside_polygon.sort()  # Ensure order is deterministic

    return indices_inside_polygon, indices_outside_polygon


def _separate_points_by_polygon(points, polygon,
                                closed, rtol=0.0, atol=0.0):
    """Underlying algorithm to partition point according to polygon

    Input:
       points - Tuple of (x, y) coordinates, or list of tuples
       polygon - Nx2 array of polygon vertices
       closed - (optional) determine whether points on boundary should be
       regarded as belonging to the polygon (closed = True)
       or not (closed = False). Close can also be None.
       rtol, atol: Tolerances for when a point is considered to coincide with
                   a line. Default 0.0.

    Output:
       indices: array of same length as points with indices of points falling
       inside the polygon listed from the beginning and indices of points
       falling outside listed from the end.

       count: count of points falling inside the polygon

       The indices of points inside are obtained as indices[:count]
       The indices of points outside are obtained as indices[count:]
     """

    # Suppress numpy warnings (as we'll be dividing by zero)
    original_numpy_settings = numpy.seterr(invalid='ignore', divide='ignore')

    N = polygon.shape[0]
    M = points.shape[0]

    if M == 0:
        # If no points return two 0-vectors
        return numpy.arange(0), numpy.arange(0)

    # Vector to return sorted indices (inside first, then outside)
    indices = numpy.zeros(M, numpy.int)

    # Vector keeping track of which points are inside
    inside = numpy.zeros(M, dtype=numpy.int)  # All assumed outside initially

    x = points[:, 0]
    y = points[:, 1]

    # Algorithm for finding points inside polygon
    for i in range(N):
        # Loop through polygon edges
        j = (i + 1) % N
        px_i, py_i = polygon[i, :]
        px_j, py_j = polygon[j, :]

        # Edge crossing formula
        sigma = (y - py_i) / (py_j - py_i) * (px_j - px_i)
        seg_i = (py_i < y) * (py_j >= y)
        seg_j = (py_j < y) * (py_i >= y)
        mask = (px_i + sigma < x) * (seg_i + seg_j)

        inside[mask] = 1 - inside[mask]

    # Restore numpy warnings
    numpy.seterr(**original_numpy_settings)

    if closed is not None:
        # Find points on polygon boundary
        for i in range(N):
            # Loop through polygon edges
            j = (i + 1) % N
            edge = [polygon[i, :], polygon[j, :]]

            # Select those that are on the boundary
            boundary_points = point_on_line(points, edge, rtol, atol)

            if closed:
                inside[boundary_points] = 1
            else:
                inside[boundary_points] = 0

    # Record point as either inside or outside
    inside_index = numpy.sum(inside)  # How many points are inside

    # Indices of inside points
    indices[:inside_index] = numpy.where(inside)[0]

    # Indices of outside points
    indices[inside_index:] = numpy.where(1 - inside)[0]

    return indices[:inside_index], indices[inside_index:]


def _separate_points_by_polygon_python(points, polygon,
                                       closed, rtol=0.0, atol=0.0):
    """Underlying algorithm to partition point according to polygon

    Note:
       This is not using numpy code so very slow - available for testing only
       Use _separate_points_by_polygon which uses numpy for real work.


    Input:
       points - Tuple of (x, y) coordinates, or list of tuples
       polygon - Nx2 array of polygon vertices
       closed - (optional) determine whether points on boundary should be
       regarded as belonging to the polygon (closed = True)
       or not (closed = False)
       rtol, atol: Tolerances for when a point is considered to coincide with
                   a line. Default 0.0.

    Output:
       indices: array of same length as points with indices of points falling
       inside the polygon listed from the beginning and indices of points
       falling outside listed from the end.

       count: count of points falling inside the polygon

       The indices of points inside are obtained as indices[:count]
       The indices of points outside are obtained as indices[count:]


    """

    # Get polygon extents to quickly rule out points that
    # are outside its bounding box
    minpx = min(polygon[:, 0])
    maxpx = max(polygon[:, 0])
    minpy = min(polygon[:, 1])
    maxpy = max(polygon[:, 1])

    M = points.shape[0]
    N = polygon.shape[0]

    # Vector to return sorted indices (inside first, then outside)
    indices = numpy.zeros(M, numpy.int)

    inside_index = 0  # Keep track of points inside
    outside_index = M - 1  # Keep track of points outside (starting from end)

    # Begin main loop (for each point)
    for k in range(M):
        x = points[k, 0]
        y = points[k, 1]
        inside = 0

        if x > maxpx or x < minpx or y > maxpy or y < minpy:
            #  Skip if point is outside polygon bounding box
            pass
        else:
            # Check if it is inside polygon
            for i in range(N):
                # Loop through polygon vertices
                j = (i + 1) % N

                px_i = polygon[i, 0]
                py_i = polygon[i, 1]
                px_j = polygon[j, 0]
                py_j = polygon[j, 1]

                if point_on_line(points[k, :],
                                 [[px_i, py_i], [px_j, py_j]],
                                 rtol, atol):
                    #  Point coincides with line segment
                    if closed:
                        inside = 1
                    else:
                        inside = 0
                    break
                else:
                    # Check if truly inside polygon
                    if (((py_i < y) and (py_j >= y)) or
                        ((py_j < y) and (py_i >= y))):
                        sigma = (y - py_i) / (py_j - py_i) * (px_j - px_i)
                        if (px_i + sigma < x):
                            inside = 1 - inside

        # Record point as either inside or outside
        if inside == 1:
            indices[inside_index] = k
            inside_index += 1
        else:
            indices[outside_index] = k
            outside_index -= 1

    # Change reversed indices back to normal order
    tmp = indices[inside_index:].copy()
    indices[inside_index:] = tmp[::-1]

    # Return reference result
    return indices[:inside_index], indices[inside_index:]


def point_on_line(points, line, rtol=1.0e-5, atol=1.0e-8,
                  check_input=True):
    """Determine if a point is on a line segment

    Input
        points: Coordinates of either
                * one point given by sequence [x, y]
                * multiple points given by list of points or Nx2 array
        line: Endpoint coordinates [[x0, y0], [x1, y1]] or
              the equivalent 2x2 numeric array with each row corresponding
              to a point.
        rtol: Relative error for how close a point must be to be accepted
        atol: Absolute error for how close a point must be to be accepted

    Output
        True or False

    Notes

    Line can be degenerate and function still works to discern coinciding
    points from non-coinciding.

    Tolerances rtol and atol are used with numpy.allclose()
    """

    one_point = False
    if check_input:
        # Prepare input data
        points = ensure_numeric(points)
        line = ensure_numeric(line)

        if len(points.shape) == 1:
            # One point only - make into 1 x 2 array
            points = points[numpy.newaxis, :]
            one_point = True
        else:
            one_point = False

        msg = 'Argument points must be either [x, y] or an Nx2 array of points'
        if len(points.shape) != 2:
            raise Exception(msg)
        if not points.shape[0] > 0:
            raise Exception(msg)
        if points.shape[1] != 2:
            raise Exception(msg)

    N = points.shape[0]  # Number of points

    x = points[:, 0]
    y = points[:, 1]
    x0, y0 = line[0]
    x1, y1 = line[1]

    # Vector from beginning of line to point
    a0 = x - x0
    a1 = y - y0

    # It's normal vector
    a_normal0 = a1
    a_normal1 = -a0

    # Vector parallel to line
    b0 = x1 - x0
    b1 = y1 - y0

    # Dot product
    nominator = abs(a_normal0 * b0 + a_normal1 * b1)
    denominator = b0 * b0 + b1 * b1

    # Determine if point vector is parallel to line up to a tolerance
    is_parallel = numpy.zeros(N, dtype=numpy.bool)  # All False
    is_parallel[nominator <= atol + rtol * denominator] = True

    # Determine for points parallel to line if they are within end points
    a0p = a0[is_parallel]
    a1p = a1[is_parallel]

    len_a = numpy.sqrt(a0p * a0p + a1p * a1p)
    len_b = numpy.sqrt(b0 * b0 + b1 * b1)
    cross = a0p * b0 + a1p * b1

    # Initialise result to all False
    result = numpy.zeros(N, dtype=numpy.bool)

    # Result is True only if a0 * b0 + a1 * b1 >= 0 and len_a <= len_b
    result[is_parallel] = (cross >= 0) * (len_a <= len_b)

    # Return either boolean scalar or boolean vector
    if one_point:
        return result[0]
    else:
        return result


def in_and_outside_polygon(points, polygon,
                           closed=True,
                           holes=None,
                           check_input=True):
    """Separate a list of points into two sets inside and outside a polygon

    Input
        points: (tuple, list or array) of coordinates
        polygon: list or Nx2 array of polygon vertices
        closed: Set to True if points on boundary are considered
                to be 'inside' polygon
        holes: list of polygons representing holes. Points inside either of
               these are considered outside polygon

    Output
        inside: Indices of points inside the polygon
        outside: Indices of points outside the polygon

    See separate_points_by_polygon for more documentation
    """

    # Get separation by outer_ring
    inside, outside = separate_points_by_polygon(points, polygon,
                                                 closed=closed,
                                                 check_input=check_input)

    # Take care of holes
    if holes is not None:
        msg = ('Argument holes must be a list of polygons, '
               'I got %s' % holes)
        if not isinstance(holes, list):
            raise InaSAFEError(msg)

        for hole in holes:
            in_hole, out_hole = separate_points_by_polygon(points[inside],
                                                           hole,
                                                           closed=not closed,
                                                           check_input=True)

            in_hole = inside[in_hole]  # Inside hole
            inside = inside[out_hole]  # Inside outer_ring but outside hole

            # Add holde indices to outside
            outside = numpy.concatenate((outside, in_hole))

    return inside, outside


def is_inside_polygon(point, polygon, closed=True):
    """Determine if one point is inside a polygon

    See inside_polygon for more details
    """

    indices = inside_polygon(point, polygon, closed)

    if indices.shape[0] == 1:
        return True
    else:
        return False


def inside_polygon(points, polygon, closed=True, holes=None,
                   check_input=True):
    """Determine points inside a polygon

       Functions inside_polygon and outside_polygon have been defined in
       terms of separate_by_polygon which will put all inside indices in
       the first part of the indices array and outside indices in the last

       See separate_points_by_polygon for documentation

       points and polygon can be a geospatial instance,
       a list or a numeric array

       holes: list of polygons representing holes. Points inside either of
       these are not considered inside_polygon
    """

    indices, _ = in_and_outside_polygon(points, polygon,
                                        closed=closed,
                                        holes=holes,
                                        check_input=check_input)

    # Return indices of points inside polygon
    return indices


# FIXME (Ole): This also needs to fixed as per issue #324
def is_outside_polygon(point, polygon, closed=True):
    """Determine if one point is outside a polygon

    See outside_polygon for more details
    """

    indices = outside_polygon(point, polygon, closed=closed)

    if indices.shape[0] == 1:
        return True
    else:
        return False


def outside_polygon(points, polygon, closed=True,
                    holes=None, check_input=True):
    """Determine points outside a polygon

       Functions inside_polygon and outside_polygon have been defined in
       terms of separate_by_polygon which will put all inside indices in
       the first part of the indices array and outside indices in the last

       See separate_points_by_polygon for documentation

       holes: list of polygons representing holes. Points inside either of
              these are considered outside polygon
    """

    _, indices = in_and_outside_polygon(points, polygon,
                                        closed=closed,
                                        holes=holes,
                                        check_input=check_input)

    # Return indices of points outside polygon
    return indices


def clip_lines_by_polygon(lines, polygon,
                          closed=True,
                          check_input=True):
    """Clip multiple lines by polygon

    Input
       lines: Sequence of polylines: [[p0, p1, ...], [q0, q1, ...], ...]
              where pi and qi are point coordinates (x, y).
       polygon: list or Nx2 array of polygon vertices
       closed: (optional) determine whether points on boundary should be
               regarded as belonging to the polygon (closed = True)
               or not (closed = False) - False is not recommended here
               This parameter can also be None in which case it is undefined
               whether a line on the boundary will fall inside or outside.
               This will make the algorithm about 20% faster.
       check_input: Allows faster execution if set to False

    Output
       inside_lines: Dictionary of lines that are inside polygon
       outside_lines: Dictionary of lines that are outside polygon

       Elements in output dictionaries can be a list of multiple lines.
       One line is a numpy array of vertices.

       Both output dictionaries use the indices of the original line as keys.
       This makes it possible to track which line the new clipped lines
       come from, if one e.g. wants to assign the original attribute values
       to clipped lines.

    This is a wrapper around clip_line_by_polygon
    """

    if check_input:
        # Input checks
        msg = 'Keyword argument "closed" must be boolean'
        if not isinstance(closed, bool):
            raise RuntimeError(msg)

        for i in range(len(lines)):
            try:
                lines[i] = ensure_numeric(lines[i], numpy.float)
            except Exception, e:
                msg = ('Line could not be converted to numeric array: %s'
                       % str(e))
                raise Exception(msg)

            msg = ('Lines must be 2d array of vertices: '
                   'I got %d dimensions' % len(lines[i].shape))
            if not len(lines[i].shape) == 2:
                raise RuntimeError(msg)

        try:
            polygon = ensure_numeric(polygon, numpy.float)
        except Exception, e:
            msg = ('Polygon could not be converted to numeric array: %s'
                   % str(e))
            raise Exception(msg)

        msg = 'Polygon array must be a 2d array of vertices'
        if not len(polygon.shape) == 2:
            raise RuntimeError(msg)

        msg = 'Polygon array must have two columns'
        if not polygon.shape[1] == 2:
            raise RuntimeError(msg)

    # Get polygon extents to quickly rule out lines where all segments
    # are outside and on the same side of its bounding box
    minpx = min(polygon[:, 0])
    maxpx = max(polygon[:, 0])
    minpy = min(polygon[:, 1])
    maxpy = max(polygon[:, 1])
    polygon_bbox = [minpx, maxpx, minpy, maxpy]

    # Get polygon_segments
    polygon_segments = polygon2segments(polygon)

    # Call underlying function
    return _clip_lines_by_polygon(lines,
                                  polygon,
                                  polygon_segments,
                                  polygon_bbox,
                                  closed=closed)


def _clip_lines_by_polygon(lines,
                           polygon,
                           polygon_segments,
                           polygon_bbox,
                           closed=True):
    """Clip multiple lines by polygon

    Underlying function.
    - see clip_lines_by_polygon for details
    """

    # Get bounding box
    minpx = polygon_bbox[0]
    maxpx = polygon_bbox[1]
    minpy = polygon_bbox[2]
    maxpy = polygon_bbox[3]

    inside_line_segments = {}
    outside_line_segments = {}

    # Loop through lines
    M = len(lines)
    for k in range(M):
        line = lines[k]

        # Exclude lines that are fully outside polygon bounding box
        if (max(line[:, 0]) < minpx or  # Everything is to the west
            min(line[:, 0]) > maxpx or  # Everything is to the east
            max(line[:, 1]) < minpy or  # Everything is to the south
            min(line[:, 1]) > maxpy):   # Everything is to the north

            inside_line_segments[k] = []
            outside_line_segments[k] = [line]
            continue

        # Call underlying function for one line and one polygon
        inside, outside = _clip_line_by_polygon(line,
                                                polygon,
                                                polygon_segments,
                                                polygon_bbox,
                                                closed=closed)

        # Record clipped line segments from line k
        inside_line_segments[k] = inside
        outside_line_segments[k] = outside

    return inside_line_segments, outside_line_segments


def clip_line_by_polygon(line, polygon,
                         closed=True,
                         polygon_bbox=None,
                         check_input=True):
    """Clip line segments by polygon

    Input
       line: Sequence of line nodes: [[x0, y0], [x1, y1], ...] or
             the equivalent Nx2 numpy array
       polygon: list or Nx2 array of polygon vertices
       closed: (optional) determine whether points on boundary should be
       regarded as belonging to the polygon (closed = True)
       or not (closed = False) - False is not recommended here
       polygon_bbox: Provide bounding box around polygon if known.
           This is a small optimisation
       check_input: Allows faster execution if set to False

    Outputs
       inside_lines: Clipped lines that are inside polygon
       outside_lines: Clipped lines that are outside polygon

       Both outputs lines take the form of lists of Nx2 numpy arrays,
       i.e. each line is an array of multiple segments

    Example:

        U = [[0,0], [1,0], [1,1], [0,1]]  # Unit square

        # Simple horizontal fully intersecting line
        line = [[-1, 0.5], [2, 0.5]]

        inside_line_segments, outside_line_segments = \
            clip_line_by_polygon(line, polygon)

        print numpy.allclose(inside_line_segments,
                              [[[0, 0.5], [1, 0.5]]])

        print numpy.allclose(outside_line_segments,
                              [[[-1, 0.5], [0, 0.5]],
                               [[1, 0.5], [2, 0.5]]])

    Remarks:
       The assumptions listed in separate_points_by_polygon apply

       Output line segments are listed as separate lines i.e. not joined
    """

    if check_input:
        # Input checks
        msg = 'Keyword argument "closed" must be boolean'
        if not isinstance(closed, bool):
            raise RuntimeError(msg)

        try:
            line = ensure_numeric(line, numpy.float)
        except Exception, e:
            msg = ('Line could not be converted to numeric array: %s'
                   % str(e))
            raise Exception(msg)

        msg = 'Line segment array must be a 2d array of vertices'
        if not len(line.shape) == 2:
            raise RuntimeError(msg)

        msg = 'Line array must have two columns'
        if not line.shape[1] == 2:
            raise RuntimeError(msg)

        try:
            polygon = ensure_numeric(polygon, numpy.float)
        except Exception, e:
            msg = ('Polygon could not be converted to numeric array: %s'
                   % str(e))
            raise Exception(msg)

        msg = 'Polygon array must be a 2d array of vertices'
        if not len(polygon.shape) == 2:
            raise RuntimeError(msg)

        msg = 'Polygon array must have two columns'
        if not polygon.shape[1] == 2:
            raise RuntimeError(msg)

    # Get polygon extents to rule out segments that
    # are outside its bounding box
    if polygon_bbox is None:
        minpx = min(polygon[:, 0])
        maxpx = max(polygon[:, 0])
        minpy = min(polygon[:, 1])
        maxpy = max(polygon[:, 1])
        polygon_bbox = [minpx, maxpx, minpy, maxpy]
    else:
        minpx = polygon_bbox[0]
        maxpx = polygon_bbox[1]
        minpy = polygon_bbox[2]
        maxpy = polygon_bbox[3]

    # Convert polygon to segments
    polygon_segments = polygon2segments(polygon)

    return _clip_line_by_polygon(line,
                                 polygon,
                                 polygon_segments,
                                 polygon_bbox,
                                 closed=closed)


# FIXME (Ole, 14 sep 2012): Will clean this up soon, promise
# pylint: disable=W0613
def _clip_line_by_polygon(line,
                          polygon,
                          polygon_segments,
                          polygon_bbox,
                          closed=True):
    """Clip line segments by polygon

    This is the underlying function
    - see public clip_line_by_polygon() for details
    """

    # Algorithm
    #
    # 1: Find all intersection points between line segments and polygon edges
    # 2: For each line segment
    #    * Calculate distance from first end point to each intersection point
    #    * Sort intersection points by distance
    #    * Cut segment into multiple segments
    # 3: For each new line segment
    #    * Calculate its midpoint
    #    * Determine if it is inside or outside clipping polygon
    # 4: Join adjacent segments into polylines that are either
    #     fully inside or outside polygon
    # 5

    # Get bounding box
    minpx = polygon_bbox[0]
    maxpx = polygon_bbox[1]
    minpy = polygon_bbox[2]
    maxpy = polygon_bbox[3]

    # Lists collecting clipped line segments
    inside_line_segments = []
    outside_line_segments = []

    # Loop through line segments
    M = line.shape[0]
    for k in range(M - 1):
        p0 = line[k, :]
        p1 = line[k + 1, :]
        segment = [p0, p1]

        #-------------
        # Optimisation
        #-------------
        # Skip segments that are outside polygon bounding box

        # In test_engine.py
        # test_polygon_to_roads_interpolation_flood_example with
        # (E_attributes[:-1:100]) took
        # * Without this: 92s
        # * With original optimisation: 61s
        # * With new version: 54s
        if p0[0] < minpx and p1[0] < minpx:  # Entire segment to the west
            segment_is_outside_bbox = True
        elif p0[0] > maxpx and p1[0] > maxpx:  # Entire segment to the east
            segment_is_outside_bbox = True
        elif p0[1] < minpy and p1[1] < minpy:  # Entire segment to the south
            segment_is_outside_bbox = True
        elif p0[1] > maxpy and p1[1] > maxpy:  # Entire segment to the north
            segment_is_outside_bbox = True
        else:
            # Skip segments where both end points are outside polygon
            # bounding box and which don't intersect the bounding box
            segment_is_outside_bbox = True
            if minpx < p0[0] < maxpx or minpy < p0[1] < maxpy:
                # First endpoint is inside bounding box
                segment_is_outside_bbox = False
            elif minpx < p1[0] < maxpx or minpy < p1[1] < maxpy:
                # Second endpoint is inside bounding box
                segment_is_outside_bbox = False
            else:
                # Both end points are outside bounding box, but could be on
                # either side so need to check if segment intersects polygon
                # bounding box.
                corners = numpy.array([[minpx, minpy], [maxpx, minpy],
                                       [maxpx, maxpy], [minpx, maxpy],
                                       [minpx, minpy]])
                for i in range(4):
                    edge = [corners[i, :], corners[i + 1, :]]
                    value = intersection(segment, edge)
                    if value is not None:
                        # Segment intersects polygon bounding box
                        segment_is_outside_bbox = False
                        break
        #-----------------
        # End optimisation
        #-----------------

        # Separate segments that are inside from those outside
        if segment_is_outside_bbox:
            outside_line_segments.append(segment)
        else:
            # Intersect segment with all polygon edges
            # and decide for each sub-segment whether in or out
            values = intersection(segment, polygon_segments)
            mask = -numpy.isnan(values[:, 0])
            V = values[mask]

            # Array for intersections
            intersections = numpy.zeros((len(V) + 2, 2))

            # Include end points
            intersections[0, :] = p0
            intersections[1, :] = p1

            # Add internal intersections
            intersections[2:, :] = V

            # For each intersection, computer distance from first end point
            V = intersections - p0
            distances = (V * V).sum(axis=1)

            # Sort intersections by distance
            idx = numpy.argsort(distances)
            distances = distances[idx]
            intersections = intersections[idx]

            # Remove duplicate points
            duplicates = numpy.zeros(len(distances), dtype=bool)
            duplicates[1:] = distances[1:] - distances[:-1] == 0
            intersections = intersections[-duplicates, :]

            # FIXME (Ole): Next candidate for vectorisation (11/9/2012) below
            # Loop through intersections for this line segment
            #distances = {}
            #for i in range(len(intersections)):
            #    v = p0 - intersections[i]
            #    d = numpy.dot(v, v)
            #    if d in distances:
            #        print i, d, distances[d], intersections[i]
            #        import sys; sys.exit()
            #    distances[d] = intersections[i]  # Don't record duplicates

            # Sort intersections by distance using Schwarzian transform
            #A = zip(distances.keys(), distances.values())
            #A.sort()
            #_, intersections = zip(*A)

            # Separate segment midpoints according to polygon
            # Deliberately ignore boundary as midpoints by definition
            # are fully inside or fully outside.
            intersections = numpy.array(intersections)
            midpoints = (intersections[:-1] + intersections[1:]) / 2
            inside, outside = separate_points_by_polygon(midpoints,
                                                         polygon,
                                                         polygon_bbox,
                                                         check_input=False,
                                                         closed=closed)

            # Form segments and add to the right lists
            for i, idx in enumerate([inside, outside]):
                if len(idx) > 0:
                    segments = numpy.concatenate((intersections[idx, :],
                                                  intersections[idx + 1, :]),
                                                 axis=1)
                    m, n = segments.shape
                    segments = numpy.reshape(segments, (m, n / 2, 2))
                    if i == 0:
                        inside_line_segments.extend(segments.tolist())
                    else:
                        outside_line_segments.extend(segments.tolist())

    # Rejoin adjacent segments and add to result lines
    inside_lines = join_line_segments(inside_line_segments)
    outside_lines = join_line_segments(outside_line_segments)

    return inside_lines, outside_lines


def join_line_segments(segments, rtol=1.0e-12, atol=1.0e-12):
    """Join adjacent line segments

    Input
        segments: List of distinct line segments [[p0, p1], [p2, p3], ...]
        rtol, atol: Optional tolerances passed on to numpy.allclose

    Output
        list of Nx2 numpy arrays each corresponding to a continuous line
        formed from consecutive segments
    """

    lines = []

    if len(segments) == 0:
        return lines

    line = segments[0]
    for i in range(len(segments) - 1):
        if numpy.allclose(segments[i][1], segments[i + 1][0],
                          rtol=rtol, atol=atol):
            # Segments are adjacent
            line.append(segments[i + 1][1])
        else:
            # Segments are disjoint - current line finishes here
            lines.append(numpy.array(line))
            line = segments[i + 1]

    # Finish line
    lines.append(numpy.array(line))

    # Return
    return lines


def line_dictionary_to_geometry(D):
    """Convert dictionary of lines to list of Nx2 arrays

    Input
        D: Dictionary of lines e.g. as produced by clip_lines_by_polygon

    Output:
        List of Nx2 arrays suitable as geometry input to class Vector
    """

    lines = []

    # Ensure reproducibility (FIXME: is this needed?)
    #keys = D.keys()
    #keys.sort()

    # Add line geometries up
    for key in D:
        lines += D[key]

    return lines


#--------------------------------------------------
# Helper functions to generate points inside polygon
#--------------------------------------------------
def generate_random_points_in_bbox(polygon, N, seed=None):
    """Generate random points in polygon bounding box
    """

    # Find outer extent of polygon
    minpx = min(polygon[:, 0])
    maxpx = max(polygon[:, 0])
    minpy = min(polygon[:, 1])
    maxpy = max(polygon[:, 1])

    seed_function(seed)

    points = []
    for _ in range(N):
        x = uniform(minpx, maxpx)
        y = uniform(minpy, maxpy)
        points.append([x, y])

    return numpy.array(points)


def populate_polygon(polygon, number_of_points, seed=None, exclude=None):
    """Populate given polygon with uniformly distributed points.

    Input:
       polygon - list of vertices of polygon
       number_of_points - (optional) number of points
       seed - seed for random number generator (default=None)
       exclude - list of polygons (inside main polygon) from where points
                 should be excluded

    Output:
       points - list of points inside polygon

    Examples:
       populate_polygon( [[0,0], [1,0], [1,1], [0,1]], 5 )
       will return five randomly selected points inside the unit square
    """

    polygon = ensure_numeric(polygon)

    # Find outer extent of polygon
    minpx = min(polygon[:, 0])
    maxpx = max(polygon[:, 0])
    minpy = min(polygon[:, 1])
    maxpy = max(polygon[:, 1])

    # Generate random points until enough are in polygon
    seed_function(seed)
    points = []
    while len(points) < number_of_points:
        x = uniform(minpx, maxpx)
        y = uniform(minpy, maxpy)

        append = False
        if is_inside_polygon([x, y], polygon):
            append = True

            #Check exclusions
            if exclude is not None:
                for ex_poly in exclude:
                    if is_inside_polygon([x, y], ex_poly):
                        append = False

        if append is True:
            points.append([x, y])

    return points


#------------------------------------
# Functionality for line intersection
#------------------------------------

def intersection(line0, line1):
    """Returns intersecting point between two line segments.

    If the lines are parallel or coincide partly (i.e. share a common segment),
    they are considered to not intersect.

    Inputs:
        line0: A simple line segment defined by two end points:
              [[x0, y0], [x1, y1]]

        line1: A collection of line segments vectorised following the format
               line[0, 0, :] = x2
               line[0, 1, :] = y2
               line[1, 0, :] = x3
               line[1, 1, :] = y3

    Output:
        intersections: Nx2 array with intersection points or nan
                       (in case of no intersection)
                       If line1 consisted of just one line,
                       None is returned for backwards compatibility


    Notes

    A vectorised input line can be constructed either as list:
    line1 = [[[0, 24, 0, 15],    # x2
              [12, 0, 24, 0]],   # y2
             [[24, 0, 0, 5],     # x3
              [0, 12, 12, 15]]]  # y3

    or as an array

    line1 = numpy.zeros(16).reshape(2, 2, 4)  # Four segments
    line1[0, 0, :] = [0, 24, 0, 15]   # x2
    line1[0, 1, :] = [12, 0, 24, 0]   # y2
    line1[1, 0, :] = [24, 0, 0, 5]    # x3
    line1[1, 1, :] = [0, 12, 12, 15]  # y3


    To select array of intersections from result, use the following idiom:

    value = intersection(line0, line1)
    mask = -numpy.isnan(value[:, 0])
    v = value[mask]
    """

    line0 = ensure_numeric(line0, numpy.float)
    line1 = ensure_numeric(line1, numpy.float)

    x0, y0 = line0[0, :]
    x1, y1 = line0[1, :]

    # Special treatment of return value if line1 was non vectorised
    if len(line1.shape) == 2:
        one_point = True
        # Broadcast to vectorised version
        line1 = line1.reshape(2, 2, 1)
    else:
        one_point = False

    # Extract vectorised coordinates
    x2 = line1[0, 0, :]
    y2 = line1[0, 1, :]
    x3 = line1[1, 0, :]
    y3 = line1[1, 1, :]

    # Calculate denominator (lines are parallel if it is 0)
    y3y2 = y3 - y2
    x3x2 = x3 - x2
    x1x0 = x1 - x0
    y1y0 = y1 - y0
    x2x0 = x2 - x0
    y2y0 = y2 - y0
    denominator = y3y2 * x1x0 - x3x2 * y1y0

    # Suppress numpy warnings (as we'll be dividing by zero)
    original_numpy_settings = numpy.seterr(invalid='ignore', divide='ignore')

    u0 = (y3y2 * x2x0 - x3x2 * y2y0) / denominator
    u1 = (x2x0 * y1y0 - y2y0 * x1x0) / denominator

    # Restore numpy warnings
    numpy.seterr(**original_numpy_settings)

     # Only points that lie within given line segments are true intersections
    mask = (0.0 <= u0) * (u0 <= 1.0) * (0.0 <= u1) * (u1 <= 1.0)

    # Calculate intersection points
    x = x0 + u0[mask] * x1x0
    y = y0 + u0[mask] * y1y0

    # Return intersection points as N x 2 array
    N = line1.shape[2]
    result = numpy.zeros((N, 2)) * numpy.nan
    result[mask, 0] = x
    result[mask, 1] = y

    # Special treatment of return value if line1 was non vectorised
    if one_point:
        result = result.reshape(2)
        if numpy.any(numpy.isnan(result)):
            return None
        else:
            return result

    # Normal return of Nx2 array of intersections (or nan)
    return result


# Main functions for polygon clipping
# FIXME (Ole): Both can be rigged to return points or lines
# outside any polygon by adding that as the entry in the list returned
def clip_grid_by_polygons(A, geotransform, polygons):
    """Clip raster grid by polygon

    Input
        A: MxN array of grid points
        geotransform: 6-tuple used to locate A geographically
                      (top left x, w-e pixel resolution, rotation,
                       top left y, rotation, n-s pixel resolution)
        polygons: list of polygon geometry objects or list of polygon arrays

    Output
        points_covered: List of (points, values) - one per input polygon.

    Implementing algorithm suggested in
    https://github.com/AIFDR/inasafe/issues/91#issuecomment-7025120

    Note: Grid points are considered to be pixel-registered which means
          that each point represents the center of its grid cell.
          The required half cell shifts are taken care of by the
          function geotransform2axes

          If multiple polygons overlap, the one first encountered will be used
    """

    # Convert raster grid to Nx2 array of points and an N array of pixel values
    ny, nx = A.shape
    x, y = geotransform2axes(geotransform, nx, ny)
    points, values = grid2points(A, x, y)

    # Generate list of points and values that fall inside each polygon
    points_covered = []
    remaining_points = points
    remaining_values = values

    for polygon in polygons:
        #print 'Remaining points', len(remaining_points)

        if hasattr(polygon, 'outer_ring'):
            outer_ring = polygon.outer_ring
            inner_rings = polygon.inner_rings
        else:
            # Assume it is an array
            outer_ring = polygon

        inside, outside = in_and_outside_polygon(remaining_points,
                                                 outer_ring,
                                                 holes=inner_rings,
                                                 closed=True,
                                                 check_input=False)
        # Add features inside this polygon
        points_covered.append((remaining_points[inside],
                               remaining_values[inside]))

        # Select remaining points to clip
        remaining_points = remaining_points[outside]
        remaining_values = remaining_values[outside]

    return points_covered


def clip_lines_by_polygons(lines, polygons, check_input=True, closed=True):
    """Clip multiple lines by multiple polygons

    Args:
        lines: Sequence of polylines: [[p0, p1, ...], [q0, q1, ...], ...]
               where pi and qi are point coordinates (x, y).
        polygons: list of polygons, each an array of vertices
        closed: optional parameter to determine whether lines that fall on
                an polygon boundary should be considered to be inside
                (closed=True), outside (closed=False) or
                undetermined (closed=None). The latter case will speed the
                algorithm up but lines on boundaries may or may not be
                deemed to fall inside the polygon and so will be
                indeterministic

    Returns:
        lines_covered: List of polylines inside a polygon
                       - one per input polygon.


    If multiple polygons overlap, the one first encountered will be used
    """

    if check_input:
        for i in range(len(lines)):
            try:
                lines[i] = ensure_numeric(lines[i], numpy.float)
            except Exception, e:
                msg = ('Line could not be converted to numeric array: %s'
                       % str(e))
                raise Exception(msg)

            msg = 'Lines must be 2d array of vertices'
            if not len(lines[i].shape) == 2:
                raise RuntimeError(msg)

        for i in range(len(polygons)):
            try:
                polygons[i] = ensure_numeric(polygons[i], numpy.float)
            except Exception, e:
                msg = ('Polygon could not be converted to numeric array: %s'
                       % str(e))
                raise Exception(msg)

    # Initialise structures
    lines_covered = []
    remaining_lines = lines

    # Clip lines to polygons
    for polygon in polygons:
    #for i, polygon in enumerate(polygons):
        #print ('Doing polygon %i (%i vertices) of %i with '
        #       '%i lines' % (i, len(polygon),
        #                     len(polygons),
        #                     len(remaining_lines)))
        inside_lines, _ = clip_lines_by_polygon(remaining_lines,
                                                polygon,
                                                check_input=False)
        #print ('- %i segments were inside'
        #       % len(line_dictionary_to_geometry(inside_lines)))

        # Record lines inside this polygon
        lines_covered.append(inside_lines)

        # Use lines outside as remaining lines
        # FIXME (Ole): This optimisation needs some thought
        # as lines are often partially clipped. We also need to keep
        # track of the parent line to get its attributes if we want
        # to go down this road
        #remaining_lines = outside_lines

    return lines_covered


def polygon2segments(polygon):
    """Convert polygon to segments structure suitable for use in intersection

    Args:
        polygon: Nx2 array of polygon vertices

    Returns:
        A collection of line segments (x0, y0) -> (x1, y1) vectorised
        following the format
               line[0, 0, :] = x0
               line[0, 1, :] = y0
               line[1, 0, :] = x1
               line[1, 1, :] = y1

    """

    try:
        polygon = ensure_numeric(polygon, numpy.float)
    except Exception, e:
        msg = ('Polygon could not be converted to numeric array: %s'
               % str(e))
        raise Exception(msg)

    N = polygon.shape[0]  # Number of vertices in polygon

    segments = numpy.zeros(N * 4).reshape(2, 2, N)
    x3 = numpy.zeros(N)
    y3 = numpy.zeros(N)

    x2 = polygon[:, 0]
    y2 = polygon[:, 1]

    x3[:-1] = x2[1:]
    x3[-1] = x2[0]
    y3[:-1] = y2[1:]
    y3[-1] = y2[0]

    segments[0, 0, :] = x2
    segments[0, 1, :] = y2
    segments[1, 0, :] = x3
    segments[1, 1, :] = y3

    return segments
