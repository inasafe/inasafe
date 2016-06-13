"""IO module for reading and writing of files

   This module provides functionality to read and write
   raster and vector layers from numerical data.
"""

import os

from qgis.core import QgsVectorLayer, QgsRasterLayer

from vector import Vector
from raster import Raster
from safe.common.utilities import verify, VerificationError
from safe.common.exceptions import BoundingBoxError, ReadLayerError

# FIXME (Ole): make logging work again
import logging
logger = logging.getLogger('inasafe')


def read_layer(filename):
    """Read spatial layer from file.
    This can be either raster or vector data.
    """

    _, ext = os.path.splitext(filename)
    if ext in ['.asc', '.tif', '.nc']:
        return Raster(filename)
    elif ext in ['.shp', '.sqlite']:
        return Vector(filename)
    else:
        msg = ('Could not read %s. '
               'Extension "%s" has not been implemented' % (filename, ext))
        raise ReadLayerError(msg)


def read_qgis_layer(filename, base_name=None):
    """Read layer from file and return as QgsMapLayer

    :param filename: the layer filename
    :type filename: str

    :return: QGIS Layer
    :rtype: QgsMapLayer
    """
    if base_name:
        _, ext = os.path.splitext(filename)
    else:
        base_name, ext = os.path.splitext(filename)
    vector_extension = [
        '.shp', '.sqlite', '.json']
    raster_extension = ['.asc', '.tif', '.nc']

    if ext in vector_extension:
        return QgsVectorLayer(filename, base_name, 'ogr')
    elif ext in raster_extension:
        return QgsRasterLayer(filename, base_name)
    else:
        msg = ('Could not read %s. '
               'Extension "%s" has not been implemented' % (filename, ext))
        raise ReadLayerError(msg)


def write_raster_data(data, projection, geotransform, filename, keywords=None):
    """Write array to raster file with specified metadata and one data layer

    Args:
        * data: Numpy array containing grid data
        * projection: WKT projection information
        * geotransform: 6 digit vector
                        (top left x, w-e pixel resolution, rotation,
                         top left y, rotation, n-s pixel resolution).
                         See e.g. http://www.gdal.org/gdal_tutorial.html
        * filename: Output filename
        * keywords: Optional dictionary

    Note:
        The only format implemented is GTiff and the extension must be .tif
    """

    R = Raster(data, projection, geotransform, keywords=keywords)
    R.write_to_file(filename)


def write_vector_data(data, projection, geometry, filename, keywords=None):
    """Write point data and any associated attributes to vector file

    Args:
        * data: List of N dictionaries each with M fields where
                M is the number of attributes.
                A value of None is acceptable.
        * projection: WKT projection information
        * geometry: List of points or polygons.
        * filename: Output filename
        * keywords: Optional dictionary

    Note
        The only format implemented is GML and SHP so the extension
        must be either .gml or .shp

    # FIXME (Ole): When the GML driver is used,
    #              the spatial reference is not stored.
    #              I suspect this is a bug in OGR.

    Background:
        * http://www.gdal.org/ogr/ogr_apitut.html (last example)
        * http://invisibleroads.com/tutorials/gdal-shapefile-points-save.html
    """

    V = Vector(data, projection, geometry, keywords=keywords)
    V.write_to_file(filename)


def get_bounding_box(filename):
    """Get bounding box for specified raster or vector file

    Args:
        * filename

    Returns:
        * bounding box as python list of numbers [West, South, East, North]
    """

    layer = read_layer(filename)
    return layer.get_bounding_box()


def bboxstring2list(bbox_string):
    """Convert bounding box string to list

    Args:
        * bbox_string: String of bounding box coordinates of the form 'W,S,E,N'

    Returns:
        * bbox: List of floating point numbers with format [W, S, E, N]
    """

    msg = ('Bounding box must be a string with coordinates following the '
           'format 105.592,-7.809,110.159,-5.647\n'
           'Instead I got %s of type %s.' % (str(bbox_string),
                                             type(bbox_string)))
    verify(isinstance(bbox_string, basestring), msg)

    fields = bbox_string.split(',')
    msg = ('Bounding box string must have 4 coordinates in the form '
           '"W,S,E,N". I got bbox == "%s"' % bbox_string)
    try:
        verify(len(fields) == 4, msg)
    except VerificationError:
        raise BoundingBoxError(msg)

    for x in fields:
        try:
            float(x)
        except ValueError, e:
            msg = ('Bounding box %s contained non-numeric entry %s, '
                   'original error was "%s".' % (bbox_string, x, e))
            raise BoundingBoxError(msg)

    return [float(x) for x in fields]
