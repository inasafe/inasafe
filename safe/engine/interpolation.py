"""**Interpolation from hazard to exposure layers.**

Provides interpolation functionality to assign values from one layer instance
to another irrespective of layer types.
"""

import numpy

from safe.common.interpolation2d import interpolate_raster
from safe.common.utilities import verify
from safe.common.utilities import ugettext as tr
from safe.common.numerics import ensure_numeric
from safe.common.geodesy import Point
from safe.common.exceptions import InaSAFEError, BoundsError
from safe.common.polygon import (inside_polygon,
                                 clip_lines_by_polygons, clip_grid_by_polygons)
#from safe.common.polygon import line_dictionary_to_geometry

from safe.storage.vector import Vector, convert_polygons_to_centroids
from safe.storage.utilities import geometrytype2string
from safe.storage.utilities import DEFAULT_ATTRIBUTE
from safe.storage.geometry import Polygon


def assign_hazard_values_to_exposure_data(hazard, exposure,
                                          layer_name=None,
                                          attribute_name=None,
                                          mode='linear'):
    """Assign hazard values to exposure data

    This is the high level wrapper around interpolation functions for different
    combinations of data types.

    Args:
       * hazard: Layer representing the hazard levels
       * exposure: Layer representing the exposure data
       * layer_name: Optional name of returned layer.
             If None (default) the name of the exposure layer is used for
             the returned layer.
       * attribute_name:
             If hazard layer is of type raster, this is the name for new
             attribute in the result containing the hazard level.
             If None (default) the name of hazard is used.
             If hazard layer is of type vector, it is the name of the
             attribute to transfer from the hazard layer into the result.
             If None (default) all attributes are transferred.
        * mode:
             Interpolation mode for raster to point interpolation only

    Returns:
        Layer representing the exposure data with hazard levels assigned.

    Raises:
        Underlying exceptions are propagated

    Note:

        Admissible combinations of input layer types are

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
        Polygon-Raster:  Convert raster to points, clip to polygon,
            assign values and return point data
        Raster-Point:    Bilinear (or constant) interpolation as currently
            implemented
        Raster-Line:     * Not Implemented *
        Raster-Polygon:  Calculate centroids and use Raster - Point algorithm
        Raster-Raster:   Exposure raster is returned as is


        The data type of the resulting layer depends on the combination of
        input types as follows:

        Polygon-Point:   Point data
        Polygon-Line:    N/A
        Polygon-Polygon: N/A
        Polygon-Raster:  Point data
        Raster-Point:    Point data
        Raster-Line:     N/A
        Raster-Polygon:  Polygon data
        Raster-Raster:   Raster data
    """

    # Make sure attribute name can be stored in a shapefile
    if attribute_name is not None and len(attribute_name) > 10:
        msg = ('Specified attribute name "%s"\
         has length = %i. '
               'To fit into a shapefile it must be at most 10 characters '
               'long. How about naming it "%s"?' % (attribute_name,
                                                    len(attribute_name),
                                                    attribute_name[:10]))
        raise InaSAFEError(msg)

    layer_name, attribute_name = check_inputs(hazard, exposure,
                                              layer_name, attribute_name)
    # Raster-Vector
    if hazard.is_raster and exposure.is_vector:
        return interpolate_raster_vector(hazard, exposure,
                                         layer_name=layer_name,
                                         attribute_name=attribute_name,
                                         mode=mode)
    # Raster-Raster
    elif hazard.is_raster and exposure.is_raster:
        return interpolate_raster_raster(hazard, exposure)
    # Vector-Vector
    elif hazard.is_vector and exposure.is_vector:
        return interpolate_polygon_vector(hazard, exposure,
                                          layer_name=layer_name,
                                          attribute_name=attribute_name)
    # Vector-Raster
    elif hazard.is_vector and exposure.is_raster:
        return interpolate_polygon_raster(hazard, exposure,
                                          layer_name=layer_name,
                                          attribute_name=attribute_name)
    # Unknown
    else:
        msg = ('Unknown combination of types for hazard and exposure data. '
               'hazard: %s, exposure: %s' % (str(hazard), str(exposure)))
        raise InaSAFEError(msg)


def check_inputs(hazard, exposure, layer_name, attribute_name):
    """Check inputs and establish default values

    Args:
        * hazard: Hazard layer instance (any type)
        * exposure: Exposure layer instance (any type)
        * layer_name: Name of returned layer or None
        * attribute_name: Name of interpolated attribute or None

    Returns:
        * layer_name
        * attribute_name

    Raises:
        VerificationError
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
                              layer_name=None, attribute_name=None,
                              mode='linear'):
    """Interpolate from raster layer to vector data

    Args:
        * source: Raster data set (grid)
        * target: Vector data set (points or polygons)
        * layer_name: Optional name of returned interpolated layer.
              If None the name of V is used for the returned layer.
        * attribute_name: Name for new attribute.
              If None (default) the name of R is used

    Returns:
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
                                             attribute_name=attribute_name,
                                             mode=mode)
    #elif target.is_line_data:
    # TBA - issue https://github.com/AIFDR/inasafe/issues/36
    #
    elif target.is_polygon_data:
        # Use centroids, in case of polygons
        P = convert_polygons_to_centroids(target)
        R = interpolate_raster_vector_points(source, P,
                                             layer_name=layer_name,
                                             attribute_name=attribute_name)
        # In case of polygon data, restore the polygon geometry
        # Do this setting the geometry of the returned set to
        # that of the original polygon
        R = Vector(data=R.get_data(),
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

    Args:
        * source: Vector data set (polygon)
        * target: Vector data set (points or polygons)  - TBA also lines
        * layer_name: Optional name of returned interpolated layer.
              If None the name of target is used for the returned layer.
        * attribute_name: Name for new attribute.
              If None (default) the name of source is used

    Output
        I: Vector data set; points located as target with values interpolated
           from source

    Note:
        If target geometry is polygon, data will be interpolated to
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
        X = convert_polygons_to_centroids(target)
        P = interpolate_polygon_points(source, X,
                                       layer_name=layer_name,
                                       attribute_name=attribute_name)

        # In case of polygon data, restore the polygon geometry
        # Do this setting the geometry of the returned set to
        # that of the original polygon
        R = Vector(data=P.get_data(),
                   projection=P.get_projection(),
                   geometry=target.get_geometry(as_geometry_objects=True),
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

    Args
        * source: Polygon data set
        * target: Raster data set
        * layer_name: Optional name of returned interpolated layer.
              If None the name of source is used for the returned layer.
        * attribute_name: Name for new attribute.
              If None (default) the name of layer target is used
    Output
        I: Vector data set; points located as target with
           values interpolated from source

    Note:
        Each point in the resulting dataset will have an attribute
        'polygon_id' which refers to the polygon it belongs to.

    """

    # Input checks
    verify(target.is_raster)
    verify(source.is_vector)
    verify(source.is_polygon_data)

    # Run underlying clipping algorithm
    polygon_geometry = source.get_geometry(as_geometry_objects=True)

    # FIXME (Ole): Perhaps refactor so that polygon_geometry can
    # be passed in directly. See issue #324, comment
    #https://github.com/AIFDR/inasafe/issues/324#issuecomment-9440584
    # FIXME (Ole): Not sure if needed, but explicitly make sure
    # exposure raster is *never* scaled here
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

    R = Vector(data=new_attributes,
               projection=source.get_projection(),
               geometry=new_geometry,
               name=layer_name)
    return R


def interpolate_raster_vector_points(source, target,
                                     layer_name=None,
                                     attribute_name=None,
                                     mode='linear'):
    """Interpolate from raster layer to point data

    Args:
        * source: Raster data set (grid)
        * target: Vector data set (points)
        * layer_name: Optional name of returned interpolated layer.
              If None the name of target is used for the returned layer.
        * attribute_name: Name for new attribute.
              If None (default) the name of layer source is used
        * mode: 'linear' or 'constant' - determines whether interpolation
              from grid to points should be bilinear or piecewise constant

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
        # FIXME (Ole): Launder for shape files
        attribute_name = str(attribute_name[:10])

    try:
        values = interpolate_raster(longitudes, latitudes, A,
                                    coordinates, mode=mode)
    except (BoundsError, InaSAFEError), e:
        msg = (tr('Could not interpolate from raster layer %(raster)s to '
                 'vector layer %(vector)s. Error message: %(error)s')
               % {'raster': source.get_name(),
                  'vector': target.get_name(),
                  'error': str(e)})
        raise InaSAFEError(msg)

    # Add interpolated attribute to existing attributes and return
    for i in range(N):
        attributes[i][attribute_name] = values[i]

    return Vector(data=attributes,
                  projection=target.get_projection(),
                  geometry=coordinates,
                  name=layer_name)


def interpolate_polygon_points(source, target,
                               layer_name=None,
                               attribute_name=None):
    """Interpolate from polygon vector layer to point vector data

    Args:
        * source: Vector data set (polygon)
        * target: Vector data set (points)
        * layer_name: Optional name of returned interpolated layer.
              If None the name of target is used for the returned layer.
        * attribute_name: Name for new attribute.
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
    geom = source.get_geometry(as_geometry_objects=True)
    data = source.get_data()
    verify(len(geom) == len(data))

    # Include polygon_id as attribute
    attribute_names.append('polygon_id')
    attribute_names.append(DEFAULT_ATTRIBUTE)

    # Augment point features with empty attributes from polygon
    for a in attributes:
        if attribute_name is None:
            # Use all attributes
            for key in attribute_names:
                a[key] = None
        else:
            # Use only requested attribute
            # FIXME (Ole): Test for this is not finished
            # BUT don't do it....Issue #251
            a[attribute_name] = None

        # Always create default attribute flagging if point was
        # inside any of the polygons
        # FIXME (Ole): Remove as already appended.....
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
        indices = inside_polygon(points, polygon.outer_ring,
                                 holes=polygon.inner_rings)

        for k in indices:
            for key in poly_attr:
                # Assign attributes from polygon to points
                attributes[k][key] = poly_attr[key]
            attributes[k]['polygon_id'] = i  # Store id for associated polygon

    # Create new Vector instance and return
    V = Vector(data=attributes,
               projection=target.get_projection(),
               geometry=original_geometry,
               name=layer_name)
    return V


def interpolate_polygon_lines(source, target,
                              layer_name=None,
                              attribute_name=None):
    """Interpolate from polygon vector layer to line vector data

    Args:
        * source: Vector data set (polygon)
        * target: Vector data set (lines)
        * layer_name: Optional name of returned interpolated layer.
              If None the name of target is used for the returned layer.
        * attribute_name: Name for new attribute.
              If None (default) the name of source is used

    Returns:
        Vector data set of lines inside polygons
           Attributes are combined from polygon they fall into and
           line that was clipped.

           Lines not in any polygon are ignored.
    """

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
    polygon_attributes = source.get_data()
    verify(len(polygons) == len(polygon_attributes))

    # Data structure for resulting line segments
    #clipped_geometry = []
    #clipped_attributes = []

    # Clip line lines to polygons
    lines_covered = clip_lines_by_polygons(lines, polygons)

    # Create one new line data layer with joined attributes
    # from polygons and lines
    new_geometry = []
    new_attributes = []
    for i in range(len(polygons)):
        # Loop over polygons

        for j in lines_covered[i]:
            # Loop over parent lines

            lines = lines_covered[i][j]
            for line in lines:
                # Loop over lines clipped from line j by polygon i

                # Associated polygon and line attributes
                attr = polygon_attributes[i].copy()
                attr.update(line_attributes[j].copy())
                attr['polygon_id'] = i  # Store id for associated polygon
                attr['parent_line_id'] = j  # Store id for parent line
                attr[DEFAULT_ATTRIBUTE] = True

                # Store new line feature
                new_geometry.append(line)
                new_attributes.append(attr)

    R = Vector(data=new_attributes,
               projection=source.get_projection(),
               geometry=new_geometry,
               geometry_type='line',
               name=layer_name)
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


# FIXME (Ole): Not sure this is the place for this function
def make_circular_polygon(centers, radii, attributes=None):
    """Create circular polygon in geographic coordinates

    Args:
        centers: list of (longitude, latitude)
        radii: desired approximate radii in meters (must be
               monotonically ascending).
        Can be either one number or list of numbers
        attributes (optional): Attributes for each center
    Returns
        Vector polygon layer representing circle in WGS84
    """

    if not isinstance(radii, list):
        radii = [radii]

    # FIXME (Ole): Check that radii are monotonically increasing

    circles = []
    new_attributes = []
    for i, center in enumerate(centers):
        p = Point(longitude=center[0], latitude=center[1])
        inner_rings = None
        for radius in radii:
            # Generate circle polygon
            C = p.generate_circle(radius)
            circles.append(Polygon(outer_ring=C, inner_rings=inner_rings))

            # Store current circle and inner ring for next poly
            inner_rings = [C]

            # Carry attributes for center forward
            attr = {}
            if attributes is not None:
                for key in attributes[i]:
                    attr[key] = attributes[i][key]

            # Add radius to this ring
            attr['Radius'] = radius

            new_attributes.append(attr)

    Z = Vector(geometry=circles,  # List with circular polygons
               data=new_attributes,  # Associated attributes
               geometry_type='polygon')

    return Z
