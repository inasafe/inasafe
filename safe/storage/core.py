"""IO module for reading and writing of files

   This module provides functionality to read and write
   raster and vector layers from numerical data.
"""

import os

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
    elif ext in ['.shp', '.gml']:
        return Vector(filename)
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


def bboxlist2string(bbox, decimals=6):
    """Convert bounding box list to comma separated string

    Args:
        * bbox: List of coordinates of the form [W, S, E, N]

    Returns:
        * bbox_string: Format 'W,S,E,N' - each will have 6 decimal points
    """

    msg = 'Got string %s, but expected bounding box as a list' % str(bbox)
    verify(not isinstance(bbox, basestring), msg)

    try:
        bbox = list(bbox)
    except:
        msg = 'Could not coerce bbox %s into a list' % str(bbox)
        raise BoundingBoxError(msg)

    msg = ('Bounding box must have 4 coordinates [W, S, E, N]. '
           'I got %s' % str(bbox))
    try:
        verify(len(bbox) == 4, msg)
    except VerificationError:
        raise BoundingBoxError(msg)

    for x in bbox:
        try:
            float(x)
        except ValueError, e:
            msg = ('Bounding box %s contained non-numeric entry %s, '
                   'original error was "%s".' % (bbox, x, e))
            raise BoundingBoxError(msg)

    # Make template of the form '%.5f,%.5f,%.5f,%.5f'
    template = (('%%.%if,' % decimals) * 4)[:-1]

    # Assign numbers and return
    return template % tuple(bbox)


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


def get_bounding_box_string(filename):
    """Get bounding box for specified raster or vector file

    Args:
        * filename

    Returns:
        * bounding box as python string 'West, South, East, North'
    """

    return bboxlist2string(get_bounding_box(filename))


def check_bbox_string(bbox_string):
    """Check that bbox string is valid
    """

    msg = 'Expected bbox as a string with format "W,S,E,N"'
    verify(isinstance(bbox_string, basestring), msg)

    # Use checks from string to list conversion
    # FIXME (Ole): Would be better to separate the checks from the conversion
    # and use those checks directly.
    minx, miny, maxx, maxy = bboxstring2list(bbox_string)

    # Check semantic integrity
    msg = ('Western border %.5f of bounding box %s was out of range '
           'for longitudes ([-180:180])' % (minx, bbox_string))
    verify(-180 <= minx <= 180, msg)

    msg = ('Eastern border %.5f of bounding box %s was out of range '
           'for longitudes ([-180:180])' % (maxx, bbox_string))
    verify(-180 <= maxx <= 180, msg)

    msg = ('Southern border %.5f of bounding box %s was out of range '
           'for latitudes ([-90:90])' % (miny, bbox_string))
    verify(-90 <= miny <= 90, msg)

    msg = ('Northern border %.5f of bounding box %s was out of range '
           'for latitudes ([-90:90])' % (maxy, bbox_string))
    verify(-90 <= maxy <= 90, msg)

    msg = ('Western border %.5f was greater than or equal to eastern border '
           '%.5f of bounding box %s' % (minx, maxx, bbox_string))
    verify(minx < maxx, msg)

    msg = ('Southern border %.5f was greater than or equal to northern border '
           '%.5f of bounding box %s' % (miny, maxy, bbox_string))
    verify(miny < maxy, msg)
