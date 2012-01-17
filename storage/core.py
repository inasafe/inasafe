"""IO module for reading and writing of files

   This module provides functionality to read and write
   raster and vector layers from numerical data.
"""

import os
import time
import numpy
import urllib2
import tempfile
import contextlib
from zipfile import ZipFile

from vector import Vector
from raster import Raster
from utilities import is_sequence
from utilities import LAYER_TYPES
from utilities import WCS_TEMPLATE
from utilities import WFS_TEMPLATE
from utilities import unique_filename
from utilities import write_keywords
from utilities import extract_WGS84_geotransform
from utilities import geotransform2resolution

import logging
logger = logging.getLogger('risiko')

#INTERNAL_SERVER_URL = os.path.join(settings.GEOSERVER_BASE_URL, 'ows')


def read_layer(filename):
    """Read spatial layer from file.
    This can be either raster or vector data.
    """

    _, ext = os.path.splitext(filename)
    if ext in ['.asc', '.tif']:
        return Raster(filename)
    elif ext in ['.shp', '.gml']:
        return Vector(filename)
    else:
        msg = ('Could not read %s. '
               'Extension "%s" has not been implemented' % (filename, ext))
        raise Exception(msg)


def write_raster_data(data, projection, geotransform, filename, keywords=None):
    """Write array to raster file with specified metadata and one data layer

    Input:
        data: Numpy array containing grid data
        projection: WKT projection information
        geotransform: 6 digit vector
                      (top left x, w-e pixel resolution, rotation,
                       top left y, rotation, n-s pixel resolution).
                       See e.g. http://www.gdal.org/gdal_tutorial.html
        filename: Output filename
        keywords: Optional dictionary

    Note: The only format implemented is GTiff and the extension must be .tif
    """

    R = Raster(data, projection, geotransform, keywords=keywords)
    R.write_to_file(filename)


def write_vector_data(data, projection, geometry, filename, keywords=None):
    """Write point data and any associated attributes to vector file

    Input:
        data: List of N dictionaries each with M fields where
              M is the number of attributes.
              A value of None is acceptable.
        projection: WKT projection information
        geometry: List of points or polygons.
        filename: Output filename
        keywords: Optional dictionary

    Note: The only format implemented is GML and SHP so the extension
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

    Input:
        filename

    Output:
        bounding box as python list of numbers [West, South, East, North]
    """

    layer = read_layer(filename)
    return layer.get_bounding_box()


def bboxlist2string(bbox, decimals=6):
    """Convert bounding box list to comma separated string

    Input
        bbox: List of coordinates of the form [W, S, E, N]
    Output
        bbox_string: Format 'W,S,E,N' - each will have 6 decimal points
    """

    msg = 'Got string %s, but expected bounding box as a list' % str(bbox)
    assert not isinstance(bbox, basestring), msg

    try:
        bbox = list(bbox)
    except:
        msg = 'Could not coerce bbox %s into a list' % str(bbox)
        raise Exception(msg)

    msg = ('Bounding box must have 4 coordinates [W, S, E, N]. '
           'I got %s' % str(bbox))
    assert len(bbox) == 4, msg

    for x in bbox:
        try:
            float(x)
        except ValueError, e:
            msg = ('Bounding box %s contained non-numeric entry %s, '
                   'original error was "%s".' % (bbox, x, e))
            raise AssertionError(msg)

    # Make template of the form '%.5f,%.5f,%.5f,%.5f'
    template = (('%%.%if,' % decimals) * 4)[:-1]

    # Assign numbers and return
    return template % tuple(bbox)


def bboxstring2list(bbox_string):
    """Convert bounding box string to list

    Input
        bbox_string: String of bounding box coordinates of the form 'W,S,E,N'
    Output
        bbox: List of floating point numbers with format [W, S, E, N]
    """

    msg = ('Bounding box must be a string with coordinates following the '
           'format 105.592,-7.809,110.159,-5.647\n'
           'Instead I got %s of type %s.' % (str(bbox_string),
                                             type(bbox_string)))
    assert isinstance(bbox_string, basestring), msg

    fields = bbox_string.split(',')
    msg = ('Bounding box string must have 4 coordinates in the form '
           '"W,S,E,N". I got bbox == "%s"' % bbox_string)
    assert len(fields) == 4, msg

    for x in fields:
        try:
            float(x)
        except ValueError, e:
            msg = ('Bounding box %s contained non-numeric entry %s, '
                   'original error was "%s".' % (bbox_string, x, e))
            raise AssertionError(msg)

    return [float(x) for x in fields]


def get_bounding_box_string(filename):
    """Get bounding box for specified raster or vector file

    Input:
        filename

    Output:
        bounding box as python string 'West, South, East, North'
    """

    return bboxlist2string(get_bounding_box(filename))


def get_geotransform(server_url, layer_name):
    """Constructs the geotransform based on the WCS service.

    Should only be called be rasters / WCS layers.

    Returns:
        geotransform is a vector of six numbers:

         (top left x, w-e pixel resolution, rotation,
          top left y, rotation, n-s pixel resolution).

        We should (at least) use elements 0, 1, 3, 5
        to uniquely determine if rasters are aligned

    """

    metadata = get_metadata(server_url, layer_name)
    return metadata['geotransform']


def get_layer_descriptors(url):
    """Get layer information for use with the plugin system

    The keywords are parsed and added to the metadata dictionary
    if they conform to the format "identifier:value".

    NOTE: Keywords will overwrite metadata with same keys. A notable
          example is title which is currently in use.

    Input
        url: The wfs url
        version: The version of the wfs xml expected

    Output
        A list of (lists of) dictionaries containing the metadata for
        each layer of the following form:

        [['geonode:lembang_schools',
          {'layer_type': 'vector',
           'category': 'exposure',
           'subcategory': 'building',
           'title': 'lembang_schools'}],
         ['geonode:shakemap_padang_20090930',
          {'layer_type': 'raster',
           'category': 'hazard',
           'subcategory': 'earthquake',
           'title': 'shakemap_padang_20090930'}]]

    """

    # FIXME (Ole): I don't like the format, but it permeates right
    #              through to the HTTPResponses in views.py, so
    #              I am not sure if it can be changed. My problem is
    #
    #              1: A dictionary of metadata entries would be simpler
    #              2: The keywords should have their own dictionary to avoid
    #                 danger of keywords overwriting other metadata
    #
    #              I have raised this in ticket #126

    # Get all metadata from owslib
    metadata = get_metadata(url)

    # Create exactly the same structure that was produced by the now obsolete
    # get_layers_metadata. FIXME: However, this is subject to issue #126
    x = []
    for key in metadata:
        # Get all metadata
        md = metadata[key]

        # Create new special purpose entry
        block = {}
        block['layer_type'] = md['layer_type']
        block['title'] = md['title']

        # Copy keyword data into this block possibly overwriting data
        for kw in md['keywords']:
            block[kw] = md['keywords'][kw]

        x.append([key, block])

    return x


def get_file(download_url, suffix):
    """Download a file from an HTTP server.
    """

    tempdir = '/tmp/%s' % str(time.time())
    os.mkdir(tempdir)
    t = tempfile.NamedTemporaryFile(delete=False,
                                    suffix=suffix,
                                    dir=tempdir)

    with contextlib.closing(urllib2.urlopen(download_url)) as f:
        data = f.read()

    if '<ServiceException>' in data:
        msg = ('File download failed.\n'
               'URL: %s\n'
               'Error message: %s' % (download_url, data))
        raise Exception(msg)

    # Write and return filename
    t.write(data)
    filename = os.path.abspath(t.name)
    return filename


def check_bbox_string(bbox_string):
    """Check that bbox string is valid
    """

    msg = 'Expected bbox as a string with format "W,S,E,N"'
    assert isinstance(bbox_string, basestring), msg

    # Use checks from string to list conversion
    # FIXME (Ole): Would be better to separate the checks from the conversion
    # and use those checks directly.
    minx, miny, maxx, maxy = bboxstring2list(bbox_string)

    # Check semantic integrity
    msg = ('Western border %.5f of bounding box %s was out of range '
           'for longitudes ([-180:180])' % (minx, bbox_string))
    assert -180 <= minx <= 180, msg

    msg = ('Eastern border %.5f of bounding box %s was out of range '
           'for longitudes ([-180:180])' % (maxx, bbox_string))
    assert -180 <= maxx <= 180, msg

    msg = ('Southern border %.5f of bounding box %s was out of range '
           'for latitudes ([-90:90])' % (miny, bbox_string))
    assert -90 <= miny <= 90, msg

    msg = ('Northern border %.5f of bounding box %s was out of range '
           'for latitudes ([-90:90])' % (maxy, bbox_string))
    assert -90 <= maxy <= 90, msg

    msg = ('Western border %.5f was greater than or equal to eastern border '
           '%.5f of bounding box %s' % (minx, maxx, bbox_string))
    assert minx < maxx, msg

    msg = ('Southern border %.5f was greater than or equal to northern border '
           '%.5f of bounding box %s' % (miny, maxy, bbox_string))
    assert miny < maxy, msg


def dummy_save(filename, title, user, metadata=''):
    """Take a file-like object and uploads it to a GeoNode
    """
    return 'http://dummy/data/geonode:' + filename + '_by_' + user.username


#--------------------------------------------------------------------
# Functionality to upload layers to GeoNode and check their integrity
#--------------------------------------------------------------------

class RisikoException(Exception):
    pass


def console_log():
    """Reconfigure logging to output to the console.
    """

    for _module in ["risiko"]:
        _logger = logging.getLogger(_module)
        _logger.addHandler(logging.StreamHandler())
        _logger.setLevel(logging.INFO)


def run(cmd, stdout=None, stderr=None):
    """Run command with stdout and stderr optionally redirected

    The logfiles are only kept in case the command fails.
    """

    # Build command
    msg = 'Argument cmd must be a string. I got %s' % cmd
    assert isinstance(cmd, basestring), msg

    s = cmd
    if stdout is not None:
        msg = 'Argument stdout must be a string or None. I got %s' % stdout
        assert isinstance(stdout, basestring), msg
        s += ' > %s' % stdout

    if stderr is not None:
        msg = 'Argument stderr must be a string or None. I got %s' % stdout
        assert isinstance(stderr, basestring), msg
        s += ' 2> %s' % stderr

    # Run command
    err = os.system(s)

    if err != 0:
        msg = 'Command "%s" failed with errorcode %i. ' % (cmd, err)
        if stdout:
            msg += 'See logfile %s for stdout details' % stdout
        if stderr is not None:
            msg += 'See logfile %s for stderr details' % stderr
        raise Exception(msg)
    else:
        # Clean up
        if stdout is not None:
            os.remove(stdout)
        if stderr is not None:
            os.remove(stderr)


def assert_bounding_box_matches(layer, filename):
    """Verify that GeoNode layer has the same bounding box as filename
    """

    # Check integrity
    assert hasattr(layer, 'geographic_bounding_box')
    assert isinstance(layer.geographic_bounding_box, basestring)

    # Exctract bounding bounding box from layer handle
    s = 'POLYGON(('
    i = layer.geographic_bounding_box.find(s) + len(s)
    assert i > len(s)

    j = layer.geographic_bounding_box.find('))')
    assert j > i

    bbox_string = str(layer.geographic_bounding_box[i:j])
    A = numpy.array([[float(x[0]), float(x[1])] for x in
                     (p.split() for p in bbox_string.split(','))])
    south = min(A[:, 1])
    north = max(A[:, 1])
    west = min(A[:, 0])
    east = max(A[:, 0])
    bbox = [west, south, east, north]

    # Check correctness of bounding box against reference
    ref_bbox = get_bounding_box(filename)

    msg = ('Bounding box from layer handle "%s" was not as expected.\n'
           'Got %s, expected %s' % (layer.name, bbox, ref_bbox))
    assert numpy.allclose(bbox, ref_bbox, rtol=1.0e-6, atol=1.0e-8), msg
