"""Wrapper around interpolation.

It provides interpolation functionality to Raster and Vector instances
using the underlying interpolation algorithm in interpolate2d.py
"""

import numpy

import safe.storage.vector
from safe.common.interpolation2d import interpolate_raster
from safe.common.utilities import verify
from safe.common.utilities import ugettext as _
from safe.common.numerics import ensure_numeric
from safe.common.polygon import (inside_polygon,
                                 clip_line_by_polygon, clip_grid_by_polygons)

from safe.common.exceptions import InaSAFEError

from utilities import geometrytype2string
from utilities import DEFAULT_ATTRIBUTE


# FIXME (Ole): Move to engine
# FIXME (Ole): Add mode parameter too
def assign_hazard_values_to_exposure_data(hazard, exposure,
                                          layer_name=None,
                                          attribute_name=None):
    """Assign hazard values to exposure data

    This is the high level wrapper around interpolation functions for different
    combinations of data types.

    Args
       hazard: Layer representing the hazard levels
       exposure: Layer representing the exposure data
       layer_name: Optional name of returned layer.
          If None (default) the name of the exposure layer is used for
          the returned layer.
       attribute_name:
         If hazard layer is of type raster, this is the name for new attribute
         in the result containing the hazard level.
         If hazard layer is of type vector, it is the name of the attribute
         to transfer from the hazard layer into the result.
         If None (default) the name of hazard is used

    Raises: Underlying exceptions are propagated

    Returns:
    Layer representing the exposure data with hazard levels assigned.
    The data type depends on the combination of input types as follows:

    Polygon-Point:   Point data
    Polygon-Line:    N/A
    Polygon-Polygon: N/A
    Polygon-Raster:  Point data
    Raster-Point:    Point data
    Raster-Line:     N/A
    Raster-Polygon:  Polygon data
    Raster-Raster:   Raster data


    Note:

    Admissible combinations are

           Exposure |  Raster     Polygon    Line     Point
    Hazard          |
    -------------------------------------------------------
    Polygon         |  Y          Y          Y        Y
    Raster          |  Y          Y          Y        Y

    with the following methodologies used:

    Polygon-Point:   Clip points to polygon and assign polygon attributes
       to them.
    Polygon-Line:    * Not Implemented *
    Polygon-Polygon: * Not Implemented *
    Polygon-Raster:  Convert raster to points, clip to polygon, assign values
       and return point data
    Raster-Point:    Bilinear (or constant) interpolation as currently
       implemented
    Raster-Line:     * Not Implemented *
    Raster-Polygon:  Calculate centroids and use Raster - Point algorithm
    Raster-Raster:   Exposure raster is returned as is

    """

    layer_name, attribute_name = check_inputs(hazard, exposure,
                                              layer_name, attribute_name)

    if hazard.is_raster:
        if exposure.is_vector:
            return interpolate_raster_vector(hazard, exposure,
                                             layer_name=layer_name,
                                             attribute_name=attribute_name)
        elif exposure.is_raster:
            return interpolate_raster_raster(hazard, exposure)
        else:
            pass
    elif hazard.is_vector and hazard.is_polygon_data:
        if exposure.is_vector:
            return interpolate_polygon_vector(hazard, exposure,
                                              layer_name=layer_name,
                                              attribute_name=attribute_name)
        elif exposure.is_raster:
            return interpolate_polygon_raster(hazard, exposure,
                                              layer_name=layer_name,
                                              attribute_name=attribute_name)
        else:
            pass
    else:
        pass


def check_inputs(hazard, exposure, layer_name, attribute_name):
    """Check inputs and establish default values

    """

    # FIXME: Push type checking into separate function input_checks
    # Also take care of None values there
    msg = ('Projections must be the same: I got %s and %s'
           % (hazard.projection, exposure.projection))
    verify(hazard.projection == exposure.projection, msg)

    msg = ('Parameter attribute_name must be either a string or None. '
           'I got %s' % (str(type(exposure)))[1:-1])
    verify(attribute_name is None
           or isinstance(attribute_name, basestring), msg)

    msg = ('Parameter layer_name must be either a string or None. '
           'I got %s' % (str(type(exposure)))[1:-1])
    verify(layer_name is None
           or isinstance(layer_name, basestring), msg)

    # FIXME: Still need to establish names here
    return layer_name, attribute_name


#-------------------------------------------------------------
# Specific functions for each individual kind of interpolation
#-------------------------------------------------------------

# FIXME (Ole): Rename arguments to source, target instead of R, V, X, ...
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

    if V.is_point_data:
        # Interpolate from raster to point data
        R = interpolate_raster_vector_points(R, V,
                                             layer_name=layer_name,
                                             attribute_name=attribute_name)
    #elif V.is_line_data:
    # TBA - issue https://github.com/AIFDR/inasafe/issues/36
    #
    elif V.is_polygon_data:
        # Use centroids, in case of polygons
        P = safe.storage.vector.convert_polygons_to_centroids(V)
        R = interpolate_raster_vector_points(R, P,
                                             layer_name=layer_name,
                                             attribute_name=attribute_name)
        # In case of polygon data, restore the polygon geometry
        # Do this setting the geometry of the returned set to
        # that of the original polygon
        R = safe.storage.vector.Vector(data=R.get_data(),
                         projection=R.get_projection(),
                         geometry=V.get_geometry(),
                         name=R.get_name())
    else:
        msg = ('Unknown datatype for raster2vector interpolation: '
               'I got %s' % str(V))
        raise InaSAFEError(msg)

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

    if X.is_point_data:
        R = interpolate_polygon_points(V, X,
                                       layer_name=layer_name,
                                       attribute_name=attribute_name)
    elif X.is_line_data:
        R = interpolate_polygon_lines(V, X,
                                      layer_name=layer_name,
                                      attribute_name=attribute_name)
    elif X.is_polygon_data:
        # Use polygon centroids
        X = safe.storage.vector.convert_polygons_to_centroids(X)
        P = interpolate_polygon_points(V, X,
                                       layer_name=layer_name,
                                       attribute_name=attribute_name)

        # In case of polygon data, restore the polygon geometry
        # Do this setting the geometry of the returned set to
        # that of the original polygon
        R = safe.storage.vector.Vector(data=P.get_data(),
                                       projection=P.get_projection(),
                                       geometry=X.get_geometry(),
                                       name=P.get_name())
    else:
        msg = ('Unknown datatype for polygon2vector interpolation: '
               'I got %s' % str(X))
        raise InaSAFEError(msg)

    # Return interpolated vector layer
    return R


def interpolate_polygon_raster(P, R, layer_name=None, attribute_name=None):
    """Interpolate from polygon layer to raster data

    Input
        P: Polygon data set
        R: Raster data set
        layer_name: Optional name of returned interpolated layer.
            If None the name of P is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of layer R is used
    Output
        I: Vector data set; points located as R with values interpolated from P

    Note, each point in the resulting dataset will have an attribute
    'polygon_id' which refers to the polygon it belongs to.

    """

    # Input checks
    verify(R.is_raster)
    verify(P.is_vector)
    verify(P.is_polygon_data)

    if layer_name is None:
        layer_name = P.get_name()

    if attribute_name is None:
        attribute_name = R.get_name()

    # Run underlying clipping algorithm
    polygon_geometry = P.get_geometry()
    polygon_attributes = P.get_data()
    res = clip_grid_by_polygons(R.get_data(),
                                R.get_geotransform(),
                                polygon_geometry)

    # Create one new point layer with interpolated attributes
    new_geometry = []
    new_attributes = []
    for i, (geometry, values) in enumerate(res):

        # For each polygon assign attributes to points that fall inside it
        for j, geom in enumerate(geometry):
            attr = polygon_attributes[i].copy()  # Attributes for this polygon
            attr[attribute_name] = values[j]  # Attribute value from grid cell
            attr['polygon_id'] = i  # Store id for associated polygon

            new_attributes.append(attr)
            new_geometry.append(geom)

    V = safe.storage.vector.Vector(data=new_attributes,
                                   projection=P.get_projection(),
                                   geometry=new_geometry,
                                   name=layer_name)
    return V



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

    return safe.storage.vector.Vector(data=attributes,
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
    V = safe.storage.vector.Vector(data=attributes,
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
    V = safe.storage.vector.Vector(data=clipped_attributes,
                                   projection=X.get_projection(),
                                   geometry=clipped_geometry,
                                   geometry_type='line',
                                   name=layer_name)
    #V.write_to_file('clipped_and_tagged.shp')
    return V


def interpolate_raster_raster(hazard, exposure):
    """Check for alignment and returns exposure layer as is
    """

    if hazard.get_geotransform() != exposure.get_geotransform():
        msg = ('Intergrid interpolation not implemented here. '
               'Make sure rasters are aligned and sampled to '
               'the same resolution')
        raise InaSAFEError(msg)
    else:
        # Rasters are aligned, no need to interpolate
        return exposure

