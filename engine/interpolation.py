"""Wrapper around interpolation.

It provides interpolation functionality to Raster and Vector instances
using the underlying interpolation algorithm in interpolate2d.py
"""

import numpy
from engine.interpolation2d import interpolate_raster
from storage.vector import Vector
from storage.vector import convert_polygons_to_centroids
from storage.utilities import verify


def interpolate_raster_vector_points(R, V, name=None):
    """Interpolate from raster layer to point data

    Input
        R: Raster data set (grid)
        V: Vector data set (points)
        name: Name for new attribute.
              If None (default) the name of R is used

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

    # Interpolate and create new attribute
    N = len(V)
    attributes = []
    if name is None:
        name = R.get_name()

    values = interpolate_raster(longitudes, latitudes, A,
                                coordinates, mode='linear')

    # Create list of dictionaries for this attribute and return
    for i in range(N):
        attributes.append({name: values[i]})

    return Vector(data=attributes, projection=V.get_projection(),
                  geometry=coordinates)


def interpolate_raster_vector(R, V, name=None):
    """Interpolate from raster layer to vector data

    Input
        R: Raster data set (grid)
        V: Vector data set (points or polygons)
        name: Name for new attribute.
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

    return interpolate_raster_vector_points(R, P, name=name)
