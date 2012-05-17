"""Wrapper around interpolation.

It provides interpolation functionality to Raster and Vector instances
using the underlying interpolation algorithm in interpolate2d.py
"""

import numpy
from engine.interpolation2d import interpolate_raster
from storage.vector import Vector
from storage.vector import convert_polygons_to_centroids
from storage.utilities import verify


def interpolate_raster_vector_points(R, V, attribute_name=None):
    """Interpolate from raster layer to point data

    Input
        R: Raster data set (grid)
        V: Vector data set (points)
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

    values = interpolate_raster(longitudes, latitudes, A,
                                coordinates, mode='linear')

    # Add interpolated attribute to existing attributes and return
    for i in range(N):
        attributes[i][attribute_name] = values[i]

    return Vector(data=attributes,
                  projection=V.get_projection(),
                  geometry=coordinates,
                  name=V.get_name())


def interpolate_raster_vector(R, V, attribute_name=None):
    """Interpolate from raster layer to vector data

    Input
        R: Raster data set (grid)
        V: Vector data set (points or polygons)
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

    # FIXME (Ole): In case of polygon data, we should return a polygon
    #              Do this setting the geometry of the returned set to
    #              the original polygon
    return interpolate_raster_vector_points(R, P,
                                            attribute_name=attribute_name)
