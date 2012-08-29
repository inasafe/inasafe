"""Wrapper around interpolation.

It provides interpolation functionality to Raster and Vector instances
using the underlying interpolation algorithm in interpolate2d.py
"""

import numpy
from safe.storage.vector import Vector
from safe.storage.vector import convert_polygons_to_centroids
from safe.common.interpolation2d import interpolate_raster
from safe.common.utilities import verify
from safe.common.utilities import ugettext as _
from safe.common.numerics import ensure_numeric
from safe.common.polygon import inside_polygon, clip_line_by_polygon

from utilities import geometrytype2string
from utilities import DEFAULT_ATTRIBUTE


def interpolate_raster_vector(R, V, layer_name=None, attribute_name=None):
    """Interpolate from raster layer to vector data

    Input
        R: Raster data set (grid)
        V: Vector data set (points or polygons)
        layer_name: Optional name of returned interpolated layer.
            If None the name of V is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of R is used

    Output
        I: Vector data set; points located as V with values interpolated from R

    Note: If target geometry is polygon, data will be interpolated to
    its centroids and the output is a point data set.
    """

    # Input checks
    verify(R.is_raster)
    verify(V.is_vector)

    if V.is_polygon_data:
        # Use centroids, in case of polygons
        P = convert_polygons_to_centroids(V)
    else:
        P = V

    # Interpolate from raster to point data
    R = interpolate_raster_vector_points(R, P,
                                         layer_name=layer_name,
                                         attribute_name=attribute_name)
    if V.is_polygon_data:
        # In case of polygon data, restore the polygon geometry
        # Do this setting the geometry of the returned set to
        # that of the original polygon
        R = Vector(data=R.get_data(),
                   projection=R.get_projection(),
                   geometry=V.get_geometry(),
                   name=R.get_name())

    # Return interpolated vector layer
    return R


def interpolate_polygon_vector(V, X,
                               layer_name=None, attribute_name=None):
    """Interpolate from polygon vector layer to vector data

    Input
        V: Vector data set (polygon)
        X: Vector data set (points or polygons)  - TBA also lines
        layer_name: Optional name of returned interpolated layer.
            If None the name of X is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of V is used

    Output
        I: Vector data set; points located as X with values interpolated from V

    Note: If target geometry is polygon, data will be interpolated to
    its centroids and the output is a point data set.
    """

    # Input checks
    verify(V.is_vector)
    verify(X.is_vector)
    verify(V.is_polygon_data)

    if layer_name is None:
        layer_name = V.get_name()

    if X.is_polygon_data:
        # Use centroids, in case of polygons
        X = convert_polygons_to_centroids(X)
    elif X.is_line_data:
        return interpolate_polygon_lines(V, X,
                                         layer_name=layer_name,
                                         attribute_name=attribute_name)

    return interpolate_polygon_points(V, X,
                                      layer_name=layer_name,
                                      attribute_name=attribute_name)


#-------------------------------------------------------------
# Specific functions for each individual kind of interpolation
#-------------------------------------------------------------
def interpolate_raster_vector_points(R, V,
                                     layer_name=None,
                                     attribute_name=None):
    """Interpolate from raster layer to point data

    Input
        R: Raster data set (grid)
        V: Vector data set (points)
        layer_name: Optional name of returned interpolated layer.
            If None the name of V is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of layer R is used

    Output
        I: Vector data set; points located as V with values interpolated from R

    """

    msg = ('There are no data points to interpolate to. Perhaps zoom out '
           'and try again')
    verify(len(V) > 0, msg)

    # Input checks
    verify(R.is_raster)
    verify(V.is_vector)
    verify(V.is_point_data)

    if layer_name is None:
        layer_name = V.get_name()

    # Get raster data and corresponding x and y axes
    A = R.get_data(nan=True)
    longitudes, latitudes = R.get_geometry()
    verify(len(longitudes) == A.shape[1])
    verify(len(latitudes) == A.shape[0])

    # Get vector point geometry as Nx2 array
    coordinates = numpy.array(V.get_geometry(),
                              dtype='d',
                              copy=False)
    # Get original attributes
    attributes = V.get_data()

    # Create new attribute and interpolate
    N = len(V)
    if attribute_name is None:
        attribute_name = R.get_name()

    try:
        values = interpolate_raster(longitudes, latitudes, A,
                                    coordinates, mode='linear')
    except Exception, e:
        msg = (_('Could not interpolate from raster layer %(raster)s to '
                 'vector layer %(vector)s. Error message: %(error)s')
               % {'raster': R.get_name(),
                  'vector': V.get_name(),
                  'error': str(e)})
        raise Exception(msg)

    # Add interpolated attribute to existing attributes and return
    for i in range(N):
        attributes[i][attribute_name] = values[i]

    return Vector(data=attributes,
                  projection=V.get_projection(),
                  geometry=coordinates,
                  name=layer_name)


def interpolate_polygon_points(V, X,
                               layer_name=None,
                               attribute_name=None):
    """Interpolate from polygon vector layer to point vector data

    Input
        V: Vector data set (polygon)
        X: Vector data set (points)
        layer_name: Optional name of returned interpolated layer.
            If None the name of X is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of V is used

    Output
        I: Vector data set; points located as X with values interpolated from V
    """

    msg = ('Vector layer to interpolate to must be point geometry. '
           'I got OGR geometry type %s'
           % geometrytype2string(X.geometry_type))
    verify(X.is_point_data, msg)

    msg = ('Name must be either a string or None. I got %s'
           % (str(type(X)))[1:-1])
    verify(layer_name is None or
           isinstance(layer_name, basestring), msg)

    msg = ('Attribute must be either a string or None. I got %s'
           % (str(type(X)))[1:-1])
    verify(attribute_name is None or
           isinstance(attribute_name, basestring), msg)

    attribute_names = V.get_attribute_names()
    if attribute_name is not None:
        msg = ('Requested attribute "%s" did not exist in %s'
               % (attribute_name, attribute_names))
        verify(attribute_name in attribute_names, msg)

    #----------------
    # Start algorithm
    #----------------

    # Extract point features
    points = ensure_numeric(X.get_geometry())
    attributes = X.get_data()
    original_geometry = X.get_geometry()  # Geometry for returned data

    # Extract polygon features
    geom = V.get_geometry()
    data = V.get_data()
    verify(len(geom) == len(data))

    # Augment point features with empty attributes from polygon
    for a in attributes:
        if attribute_name is None:
            # Use all attributes
            for key in attribute_names:
                a[key] = None
        else:
            # Use only requested attribute
            # FIXME (Ole): Test for this is not finished
            a[attribute_name] = None

        # Always create default attribute flagging if point was
        # inside any of the polygons
        a[DEFAULT_ATTRIBUTE] = None

    # Traverse polygons and assign attributes to points that fall inside
    for i, polygon in enumerate(geom):
        if attribute_name is None:
            # Use all attributes
            poly_attr = data[i]
        else:
            # Use only requested attribute
            poly_attr = {attribute_name: data[i][attribute_name]}

        # Assign default attribute to indicate points inside
        poly_attr[DEFAULT_ATTRIBUTE] = True

        # Clip data points by polygons and add polygon attributes
        indices = inside_polygon(points, polygon)
        for k in indices:
            for key in poly_attr:
                # Assign attributes from polygon to points
                attributes[k][key] = poly_attr[key]

    # Create new Vector instance and return
    V = Vector(data=attributes,
               projection=X.get_projection(),
               geometry=original_geometry,
               name=layer_name)
    return V


def interpolate_polygon_lines(V, X,
                              layer_name=None,
                              attribute_name=None):
    """Interpolate from polygon vector layer to line vector data

    Input
        V: Vector data set (polygon)
        X: Vector data set (lines)
        layer_name: Optional name of returned interpolated layer.
            If None the name of X is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of V is used

    Output
        Vector data set (lines) with values interpolated from V
    """

    #X.write_to_file('line_data.shp')
    #V.write_to_file('poly_data.shp')
    if attribute_name is None:
        attribute_name = V.get_name()

    # Extract line features
    lines = X.get_geometry()
    line_attributes = X.get_data()
    N = len(X)
    verify(len(lines) == N)
    verify(len(line_attributes) == N)

    # Extract polygon features
    polygons = V.get_geometry()
    poly_attributes = V.get_data()
    verify(len(polygons) == len(poly_attributes))

    # Data structure for resulting line segments
    clipped_geometry = []
    clipped_attributes = []

    # Clip line lines to polygons
    for i, polygon in enumerate(polygons):
        for j, line in enumerate(lines):
            inside, outside = clip_line_by_polygon(line, polygon)

            # Create new attributes
            # FIXME (Ole): Not done single specified polygon
            #              attribute
            inside_attributes = {}
            outside_attributes = {}
            for key in line_attributes[j]:
                inside_attributes[key] = line_attributes[j][key]
                outside_attributes[key] = line_attributes[j][key]

            for key in poly_attributes[i]:
                inside_attributes[key] = poly_attributes[i][key]
                outside_attributes[key] = None

            # Always create default attribute flagging if segment was
            # inside any of the polygons
            inside_attributes[DEFAULT_ATTRIBUTE] = True
            outside_attributes[DEFAULT_ATTRIBUTE] = False

            # Assign new attribute set to clipped lines
            for segment in inside:
                clipped_geometry.append(segment)
                clipped_attributes.append(inside_attributes)

            for segment in outside:
                clipped_geometry.append(segment)
                clipped_attributes.append(outside_attributes)

    # Create new Vector instance and return
    V = Vector(data=clipped_attributes,
               projection=X.get_projection(),
               geometry=clipped_geometry,
               geometry_type='line',
               name=layer_name)
    #V.write_to_file('clipped_and_tagged.shp')
    return V
