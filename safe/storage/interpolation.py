"""Wrapper around interpolation.

It provides interpolation functionality to Raster and Vector instances
using the underlying interpolation algorithm in interpolate2d.py
"""

# FIXME (Ole): Move all of this to engine

import numpy

import safe.storage.vector  # FIXME: Revisit when interpolate method has been
                            # removed from raster and vector
from safe.common.interpolation2d import interpolate_raster
from safe.common.utilities import verify
from safe.common.utilities import ugettext as _
from safe.common.numerics import ensure_numeric
from safe.common.polygon import (inside_polygon,
                                 clip_line_by_polygon, clip_grid_by_polygons)

from safe.common.exceptions import InaSAFEError
from safe.storage.utilities import geometrytype2string
from safe.storage.utilities import DEFAULT_ATTRIBUTE


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

    if hazard.is_raster and exposure.is_vector:
        return interpolate_raster_vector(hazard, exposure,
                                         layer_name=layer_name,
                                         attribute_name=attribute_name)

    elif hazard.is_raster and exposure.is_raster:
        return interpolate_raster_raster(hazard, exposure)

    elif hazard.is_vector and exposure.is_vector:
        return interpolate_polygon_vector(hazard, exposure,
                                          layer_name=layer_name,
                                          attribute_name=attribute_name)

    elif hazard.is_vector and exposure.is_raster:
        return interpolate_polygon_raster(hazard, exposure,
                                          layer_name=layer_name,
                                          attribute_name=attribute_name)

    else:
        msg = ('Unknown combination of types for hazard and exposure data. '
               'hazard: %s, exposure: %s' % (str(hazard), str(exposure)))
        raise InaSAFEError(msg)


def check_inputs(hazard, exposure, layer_name, attribute_name):
    """Check inputs and establish default values

    """

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

    # Establish default names
    if layer_name is None:
        layer_name = exposure.get_name()

    if hazard.is_raster and attribute_name is None:
        layer_name = hazard.get_name()

    return layer_name, attribute_name


#-------------------------------------------------------------
# Specific functions for each individual kind of interpolation
#-------------------------------------------------------------
def interpolate_raster_vector(source, target,
                              layer_name=None, attribute_name=None):
    """Interpolate from raster layer to vector data

    Input
        source: Raster data set (grid)
        target: Vector data set (points or polygons)
        layer_name: Optional name of returned interpolated layer.
            If None the name of V is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of R is used

    Output
        I: Vector data set; points located as target with values
           interpolated from source

    Note: If target geometry is polygon, data will be interpolated to
    its centroids and the output is a point data set.
    """

    # Input checks
    verify(source.is_raster)
    verify(target.is_vector)

    if target.is_point_data:
        # Interpolate from raster to point data
        R = interpolate_raster_vector_points(source, target,
                                             layer_name=layer_name,
                                             attribute_name=attribute_name)
    #elif target.is_line_data:
    # TBA - issue https://github.com/AIFDR/inasafe/issues/36
    #
    elif target.is_polygon_data:
        # Use centroids, in case of polygons
        P = safe.storage.vector.convert_polygons_to_centroids(target)
        R = interpolate_raster_vector_points(source, P,
                                             layer_name=layer_name,
                                             attribute_name=attribute_name)
        # In case of polygon data, restore the polygon geometry
        # Do this setting the geometry of the returned set to
        # that of the original polygon
        R = safe.storage.vector.Vector(data=R.get_data(),
                                       projection=R.get_projection(),
                                       geometry=target.get_geometry(),
                                       name=R.get_name())
    else:
        msg = ('Unknown datatype for raster2vector interpolation: '
               'I got %s' % str(target))
        raise InaSAFEError(msg)

    # Return interpolated vector layer
    return R


def interpolate_polygon_vector(source, target,
                               layer_name=None, attribute_name=None):
    """Interpolate from polygon vector layer to vector data

    Input
        source: Vector data set (polygon)
        target: Vector data set (points or polygons)  - TBA also lines
        layer_name: Optional name of returned interpolated layer.
            If None the name of target is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of source is used

    Output
        I: Vector data set; points located as target with values interpolated
           from source

    Note: If target geometry is polygon, data will be interpolated to
    its centroids and the output is a point data set.
    """

    # Input checks
    verify(source.is_vector)
    verify(target.is_vector)
    verify(source.is_polygon_data)

    if target.is_point_data:
        R = interpolate_polygon_points(source, target,
                                       layer_name=layer_name,
                                       attribute_name=attribute_name)
    elif target.is_line_data:
        R = interpolate_polygon_lines(source, target,
                                      layer_name=layer_name,
                                      attribute_name=attribute_name)
    elif target.is_polygon_data:
        # Use polygon centroids
        X = safe.storage.vector.convert_polygons_to_centroids(target)
        P = interpolate_polygon_points(source, X,
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
               'I got %s' % str(target))
        raise InaSAFEError(msg)

    # Return interpolated vector layer
    return R


def interpolate_polygon_raster(source, target,
                               layer_name=None, attribute_name=None):
    """Interpolate from polygon layer to raster data

    Input
        source: Polygon data set
        target: Raster data set
        layer_name: Optional name of returned interpolated layer.
            If None the name of source is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of layer target is used
    Output
        I: Vector data set; points located as target with
           values interpolated from source

    Note, each point in the resulting dataset will have an attribute
    'polygon_id' which refers to the polygon it belongs to.

    """

    # Input checks
    verify(target.is_raster)
    verify(source.is_vector)
    verify(source.is_polygon_data)

    # Run underlying clipping algorithm
    polygon_geometry = source.get_geometry()
    polygon_attributes = source.get_data()
    res = clip_grid_by_polygons(target.get_data(),
                                target.get_geotransform(),
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

    R = safe.storage.vector.Vector(data=new_attributes,
                                   projection=source.get_projection(),
                                   geometry=new_geometry,
                                   name=layer_name)
    return R


def interpolate_raster_vector_points(source, target,
                                     layer_name=None,
                                     attribute_name=None):
    """Interpolate from raster layer to point data

    Input
        source: Raster data set (grid)
        target: Vector data set (points)
        layer_name: Optional name of returned interpolated layer.
            If None the name of target is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of layer source is used

    Output
        I: Vector data set; points located as target with values
           interpolated from source

    """

    msg = ('There are no data points to interpolate to. Perhaps zoom out '
           'and try again')
    verify(len(target) > 0, msg)

    # Input checks
    verify(source.is_raster)
    verify(target.is_vector)
    verify(target.is_point_data)

    # FIXME (Ole): Why can we not remove this ???
    # It should now be taken care of in the general input_check above
    # OK - remove when we leave using the form H.interpolate in impact funcs
    if layer_name is None:
        layer_name = target.get_name()

    # Get raster data and corresponding x and y axes
    A = source.get_data(nan=True)
    longitudes, latitudes = source.get_geometry()
    verify(len(longitudes) == A.shape[1])
    verify(len(latitudes) == A.shape[0])

    # Get vector point geometry as Nx2 array
    coordinates = numpy.array(target.get_geometry(),
                              dtype='d',
                              copy=False)
    # Get original attributes
    attributes = target.get_data()

    # Create new attribute and interpolate
    # Remove?
    N = len(target)
    if attribute_name is None:
        attribute_name = source.get_name()

    try:
        values = interpolate_raster(longitudes, latitudes, A,
                                    coordinates, mode='linear')
    except Exception, e:
        msg = (_('Could not interpolate from raster layer %(raster)s to '
                 'vector layer %(vector)s. Error message: %(error)s')
               % {'raster': source.get_name(),
                  'vector': target.get_name(),
                  'error': str(e)})
        raise Exception(msg)

    # Add interpolated attribute to existing attributes and return
    for i in range(N):
        attributes[i][attribute_name] = values[i]

    return safe.storage.vector.Vector(data=attributes,
                         projection=target.get_projection(),
                         geometry=coordinates,
                         name=layer_name)


def interpolate_polygon_points(source, target,
                               layer_name=None,
                               attribute_name=None):
    """Interpolate from polygon vector layer to point vector data

    Input
        source: Vector data set (polygon)
        target: Vector data set (points)
        layer_name: Optional name of returned interpolated layer.
            If None the name of target is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of source is used

    Output
        I: Vector data set; points located as target with values interpolated
        from source
    """

    msg = ('Vector layer to interpolate to must be point geometry. '
           'I got OGR geometry type %s'
           % geometrytype2string(target.geometry_type))
    verify(target.is_point_data, msg)

    msg = ('Name must be either a string or None. I got %s'
           % (str(type(target)))[1:-1])
    verify(layer_name is None or
           isinstance(layer_name, basestring), msg)

    msg = ('Attribute must be either a string or None. I got %s'
           % (str(type(target)))[1:-1])
    verify(attribute_name is None or
           isinstance(attribute_name, basestring), msg)

    attribute_names = source.get_attribute_names()
    if attribute_name is not None:
        msg = ('Requested attribute "%s" did not exist in %s'
               % (attribute_name, attribute_names))
        verify(attribute_name in attribute_names, msg)

    #----------------
    # Start algorithm
    #----------------

    # Extract point features
    points = ensure_numeric(target.get_geometry())
    attributes = target.get_data()
    original_geometry = target.get_geometry()  # Geometry for returned data

    # Extract polygon features
    geom = source.get_geometry()
    data = source.get_data()
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
                      projection=target.get_projection(),
                      geometry=original_geometry,
                      name=layer_name)
    return V


def interpolate_polygon_lines(source, target,
                              layer_name=None,
                              attribute_name=None):
    """Interpolate from polygon vector layer to line vector data

    Input
        source: Vector data set (polygon)
        target: Vector data set (lines)
        layer_name: Optional name of returned interpolated layer.
            If None the name of target is used for the returned layer.
        attribute_name: Name for new attribute.
              If None (default) the name of source is used

    Output
        Vector data set (lines) with values interpolated from source
    """

    #target.write_to_file('line_data.shp')
    #source.write_to_file('poly_data.shp')
    # Remove?
    if attribute_name is None:
        attribute_name = source.get_name()

    # Extract line features
    lines = target.get_geometry()
    line_attributes = target.get_data()
    N = len(target)
    verify(len(lines) == N)
    verify(len(line_attributes) == N)

    # Extract polygon features
    polygons = source.get_geometry()
    poly_attributes = source.get_data()
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
    R = safe.storage.vector.Vector(data=clipped_attributes,
                                   projection=target.get_projection(),
                                   geometry=clipped_geometry,
                                   geometry_type='line',
                                   name=layer_name)
    #R.write_to_file('clipped_and_tagged.shp')
    return R


def interpolate_raster_raster(source, target):
    """Check for alignment and returns target layer as is
    """

    if source.get_geotransform() != target.get_geotransform():
        msg = ('Intergrid interpolation not implemented here. '
               'Make sure rasters are aligned and sampled to '
               'the same resolution')
        raise InaSAFEError(msg)
    else:
        # Rasters are aligned, no need to interpolate
        return target
