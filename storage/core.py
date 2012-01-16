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


def get_metadata_from_layer(layer):
    """Get ows metadata from one layer

    Input
        layer: Layer object. It is assumed that it has the extra attribute
               data_type which is either raster or vector
    """

    # Create empty metadata dictionary
    metadata = {}

    # Metadata specific to layer types
    metadata['layer_type'] = layer.datatype
    if layer.datatype == 'raster':
        geotransform = extract_WGS84_geotransform(layer)
        metadata['geotransform'] = geotransform
        metadata['resolution'] = geotransform2resolution(geotransform,
                                                         # Get both resx
                                                         # and resy
                                                         isotropic=False)
    else:
        metadata['resolution'] = None
        metadata['geotransform'] = None

    # Metadata common to both raster and vector data
    metadata['bounding_box'] = layer.boundingBoxWGS84
    metadata['title'] = layer.title  # This maybe overwritten by keyword
    metadata['id'] = layer.id

    # Extract keywords
    keyword_dict = {}
    if not hasattr(layer, 'keywords'):
        msg = 'No keywords in %s. Submit patch to OWSLib maintainers.' % layer
        raise Exception(msg)
    else:
        for keyword in layer.keywords:
            if keyword is not None:
                for keyword_string in keyword.split(','):
                    if ':' in keyword_string:
                        key, value = keyword_string.strip().split(':')
                        keyword_dict[key] = value
                    else:
                        keyword_dict[keyword_string] = None

    # Add resolution (as a string with one element) so that layer "remembers"
    # its original resolution,
    # FIXME (Ole): What is the best way of collapsing 2D resolution to
    # one number - resx and resy are not always identical!
    if metadata['resolution'] is not None:
        keyword_dict['resolution'] = str(metadata['resolution'][0])

    # FIXME (Ole): The statement below does not raise an Exception,
    # and nothing is written to the log file. See issue #170
    #raise Exception('weird')

    # Record all keywords as part of the metadata and return
    metadata['keywords'] = keyword_dict
    return metadata


def get_metadata(server_url, layer_name=None):
    """Uses OWSLib to get the metadata for a given layer

    Input
        server_url: e.g. http://localhost:8001/geoserver-geonode-dev/ows
        layer_name: Name of layer - must follow the convention workspace:name
                    If None metadata for all layers will be returned as a
                    dictionary with one entry per layer

    Output
        metadata: Dictionary of metadata fields for specified layer or,
                  if layer_name is None, a dictionary of metadata dictionaries
    """

    # Get all metadata from server
    wcs = WebCoverageService(server_url, version='1.0.0')
    wfs = WebFeatureService(server_url, version='1.0.0')

    # Take care of input options
    if layer_name is None:
        layer_names = wcs.contents.keys() + wfs.contents.keys()
    else:
        layer_names = [layer_name]

    # Get metadata for requested layer(s)
    metadata = {}
    for name in layer_names:
        if name in wcs.contents:
            layer = wcs.contents[name]
            layer.datatype = 'raster'  # Monkey patch layer type
        elif name in wfs.contents:
            layer = wfs.contents[name]
            layer.datatype = 'vector'  # Monkey patch layer type
        else:
            msg = ('Layer %s was not found in WxS contents on server %s.\n'
                   'WCS contents: %s\n'
                   'WFS contents: %s\n' % (name, server_url,
                                           wcs.contents, wfs.contents))
            raise Exception(msg)

        metadata[name] = get_metadata_from_layer(layer)

    # Return metadata for one or all layers
    if layer_name is not None:
        return metadata[layer_name]
    else:
        return metadata


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


def download(server_url, layer_name, bbox, resolution=None):
    """Download the source data of a given layer.

    Input
        server_url: String such as 'http://www.aifdr.org:8080/geoserver/ows'
        layer_name: Layer identifier of the form workspace:name,
                    e.g 'geonode:Earthquake_Ground_Shaking'
        bbox: Bounding box for layer. This can either be a string or a list
              with format [west, south, east, north], e.g.
              '87.998242,-8.269822,117.046094,5.097895'
        resolution: Optional argument specifying resolution in case of
                    raster layers.
                    Resolution can be a tuple (resx, resy) signifying the
                    spacing in decimal degrees in the longitude, latitude
                    direction respectively.
                    If resolution is just one number it is used for both resx
                    and resy.
                    If resolution is None, the 'native' resolution of
                    the dataset is used.

    Layer geometry type must be either 'vector' or 'raster'
    """

    # Input checks
    assert isinstance(server_url, basestring)
    try:
        urllib2.urlopen(server_url)
    except Exception, e:
        msg = ('Argument server_url doesn\'t appear to be a valid URL'
               'I got %s. Error message was: %s' % (server_url, str(e)))
        raise Exception(msg)

    msg = ('Expected layer_name to be a basestring. '
           'Instead got %s which is of type %s' % (layer_name,
                                                   type(layer_name)))
    assert isinstance(layer_name, basestring), msg

    msg = ('Argument layer name must have the form'
           'workspace:name. I got %s' % layer_name)
    assert len(layer_name.split(':')) == 2, msg

    if isinstance(bbox, list) or isinstance(bbox, tuple):
        bbox_string = bboxlist2string(bbox)
    elif isinstance(bbox, basestring):
        # Remove spaces if any (GeoServer freaks if string has spaces)
        bbox_string = ','.join([x.strip() for x in bbox.split(',')])
    else:
        msg = ('Bounding box must be a string or a list of coordinates with '
               'format [west, south, east, north]. I got %s' % str(bbox))
        raise Exception(msg)

    # Check integrity of bounding box
    check_bbox_string(bbox_string)

    # Check resolution
    if resolution is not None:

        # Make sure it is a list or a tuple
        if not is_sequence(resolution):
            # Replicate single value twice
            resolution = (resolution, resolution)

        # Check length
        msg = ('Specified resolution must be either a number or a 2-tuple. '
               'I got %s' % str(resolution))
        assert len(resolution) == 2, msg

        # Check floating point
        for res in resolution:
            try:
                float(res)
            except ValueError, e:
                msg = ('Expecting number for resolution, but got %s: %s'
                       % (res, str(e)))
                raise RisikoException(msg)

    # Create REST request and download file
    template = None
    layer_metadata = get_metadata(server_url, layer_name)

    data_type = layer_metadata['layer_type']
    if data_type == 'vector':

        if resolution is not None:
            msg = ('Resolution was requested for Vector layer %s. '
                   'This can only be done for raster layers.' % layer_name)
            raise RisikoException(msg)

        template = WFS_TEMPLATE
        suffix = '.zip'
        download_url = template % (server_url, layer_name, bbox_string)
        thefilename = get_file(download_url, suffix)
        dirname = os.path.dirname(thefilename)
        t = open(thefilename, 'r')
        zf = ZipFile(t)
        namelist = zf.namelist()
        zf.extractall(path=dirname)
        (shpname,) = [name for name in namelist if '.shp' in name]
        filename = os.path.join(dirname, shpname)
    elif data_type == 'raster':

        if resolution is None:
            # Get native resolution and use that
            resolution = layer_metadata['resolution']
            #resolution = (resolution, resolution)  #FIXME (Ole): Make nicer

        # Download raster using specified bounding box and resolution
        template = WCS_TEMPLATE
        suffix = '.tif'
        download_url = template % (server_url, layer_name, bbox_string,
                                   resolution[0], resolution[1])
        filename = get_file(download_url, suffix)

    # Write keywords file
    keywords = layer_metadata['keywords']
    write_keywords(keywords, os.path.splitext(filename)[0] + '.keywords')

    # Instantiate layer from file
    lyr = read_layer(filename)

    # FIXME (Ariel) Don't monkeypatch the layer object
    lyr.metadata = layer_metadata
    return lyr


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


def check_layer(layer, full=False):
    """Verify if an object is a valid Layer.

    If check fails an exception is raised.

    Input
        layer: Layer object
        full: Optional flag controlling whether layer is to be downloaded
              as part of the check.
    """

    from geonode.maps.models import Layer

    msg = ('Was expecting layer object, got None')
    assert layer is not None, msg
    msg = ('Was expecting layer object, got %s' % (type(layer)))
    assert type(layer) is Layer, msg
    msg = ('The layer does not have a valid name: %s' % layer.name)
    assert len(layer.name) > 0, msg
    msg = ('The layer does not have a valid workspace: %s' % layer.workspace)
    assert len(layer.workspace) > 0, msg

    # Get layer metadata
    layer_name = '%s:%s' % (layer.workspace, layer.name)
    metadata = get_metadata(INTERNAL_SERVER_URL, layer_name)
    #try:
    #    metadata = get_metadata(INTERNAL_SERVER_URL, layer_name)
    #except:
    #    # Convert any exception to AssertionError for use in retry loop in
    #    # save_file_to_geonode.
    #    raise AssertionError

    assert 'id' in metadata
    assert 'title' in metadata
    assert 'layer_type' in metadata
    assert 'keywords' in metadata
    assert 'bounding_box' in metadata

    # Get bounding box and download
    bbox = metadata['bounding_box']
    assert len(bbox) == 4

    if full:
        # Check that layer can be downloaded again
        downloaded_layer = download(INTERNAL_SERVER_URL, layer_name, bbox)
        assert os.path.exists(downloaded_layer.filename)

        # Check integrity between Django layer and file
        assert_bounding_box_matches(layer, downloaded_layer.filename)

        # Read layer and verify
        L = read_layer(downloaded_layer.filename)

        # Could do more here
        #print dir(L)
        #print L.keywords  #FIXME(Ole): I don't think keywords are downloaded!
        #print metadata['keywords']


def save_file_to_geonode(filename, user=None, title=None,
                         overwrite=True, check_metadata=True,
                         ignore=None):
    """Save a single layer file to local Risiko GeoNode

    Input
        filename: Layer filename of type as defined in LAYER_TYPES
        user: Django User object
        title: String describing the layer.
               If None or '' the filename will be used.
        overwrite: Boolean variable controlling whether existing layers
                   can be overwritten by this operation. Default is True
        check_metadata: Flag controlling whether metadata is verified.
                        If True (default), an exception will be raised
                        if metada is not available after a number of retries.
                        If False, no check is done making the function faster.
    Output
        layer object
    """

    if ignore is not None and filename == ignore:
        return None

    # Extract fully qualified basename and extension
    basename, extension = os.path.splitext(filename)

    if extension not in LAYER_TYPES:
        msg = ('Invalid file extension in file %s. Valid extensions are '
               '%s' % (filename, str(LAYER_TYPES)))
        raise RisikoException(msg)

    # Try to find a file with a .keywords extension
    # and create a keywords list from there.
    # It is assumed that the keywords are separated
    # by new lines.
    # Empty keyword lines are ignored (as this causes issues downstream)
    keyword_list = []
    keyword_file = basename + '.keywords'
    kw_title = None
    if os.path.exists(keyword_file):
        f = open(keyword_file, 'r')
        for line in f.readlines():

            # Ignore blank lines
            raw_keyword = line.strip()
            if raw_keyword == '':
                continue

            # Strip any spaces after or before the colons if present
            if ':' in raw_keyword:
                keyword = ':'.join([x.strip() for x in raw_keyword.split(':')])

            # Grab title if present
            if 'title' in keyword:
                kw_title = keyword.split(':')[1]

            # FIXME (Ole): Replace spaces by underscores and store keyword.
            # See issue #148
            keyword_list.append(keyword.replace(' ', '_'))
        f.close()

    # Take care of file types
    if extension == '.asc':
        # We assume this is an AAIGrid ASCII file such as those generated by
        # ESRI and convert it to Geotiff before uploading.

        # Create temporary tif file for upload and check that the road is clear
        prefix = os.path.split(basename)[-1]
        upload_filename = unique_filename(prefix=prefix, suffix='.tif')
        upload_basename, extension = os.path.splitext(upload_filename)

        # Copy any metadata files to unique filename
        for ext in ['.sld', '.keywords']:
            if os.path.exists(basename + ext):
                cmd = 'cp %s%s %s%s' % (basename, ext, upload_basename, ext)
                run(cmd)

        # Check that projection file exists
        prjname = basename + '.prj'
        if not os.path.isfile(prjname):
            msg = ('File %s must have a projection file named '
                   '%s' % (filename, prjname))
            raise RisikoException(msg)

        # Convert ASCII file to GeoTIFF
        R = read_layer(filename)
        R.write_to_file(upload_filename)
    else:
        # The specified file is the one to upload
        upload_filename = filename

    # Use file name or keywords to derive title if not specified
    if title is None or title == '':
        # FIXME (Ole): If we set title to anything but the filename,
        # we get the upload test to fail. See issue #180
        # Clean this up after issue #180 has been addressed
        title = os.path.split(basename)[-1]

        # FIXME (Ole): This is what we want (issue #180)
        #if kw_title is None:
        #    title = os.path.split(basename)[-1]
        #else:
        #    title = kw_title

        # FIXME (Ole): This is just a work-around for now
        if kw_title is None:
            layer_title = os.path.split(basename)[-1]
        else:
            layer_title = kw_title
    else:
        layer_title = title

    # Attempt to upload the layer
    try:
        # Upload
        layer = file_upload(upload_filename,
                            user=user,
                            title=title,
                            keywords=keyword_list,
                            overwrite=overwrite)

        # FIXME (Ole): This workaround should be revisited.
        #              This fx means that keywords can't have spaces
        #              Really need a generic way of getting this kind of
        #              info in and out of GeoNode. See issue #148
        layer.keywords = ' '.join(keyword_list)
        layer.save()
    except Exception, e:
        # Layer did not upload. Convert GeoNodeException to RisikoException
        raise RisikoException(e)
    else:

        #print
        #print 'layer', layer
        #print 'name', layer.name
        #print 'title', layer.title
        #print 'id', layer.id

        # FIXME (Ole): Why are layer.name and layer.title equal?
        #              See issue #180
        #logmsg = ('Uploaded "%s" with name "%s" and title "%s".'
        #          % (basename, layer.name, layer.title))
        logmsg = ('Uploaded "%s" with name "%s" and title "%s".'
                  % (basename, layer.name, layer_title))

        if not check_metadata:
            logmsg += ' Did not explicitly verify metadata.'
            logger.info(logmsg)
            return layer
        else:
            # Check metadata and return layer object
            logmsg += ' Metadata veried.'
            ok = False
            for i in range(4):
                try:
                    check_layer(layer)
                except Exception, errmsg:
                    logger.debug('Metadata for layer %s not yet ready - '
                                 'trying again. Error message was: %s'
                                 % (layer.name, errmsg))
                    time.sleep(0.3)
                else:
                    ok = True
                    break
            if ok:
                logger.info(logmsg)
                return layer
            else:
                msg = ('Could not confirm that layer %s was uploaded '
                       'correctly: %s' % (layer, errmsg))
                raise Exception(msg)
    finally:
        # Clean up generated tif files in either case
        if extension == '.asc':
            os.remove(upload_filename)
            os.remove(upload_filename + '.aux.xml')


def save_directory_to_geonode(directory,
                              user=None,
                              title=None,
                              overwrite=True,
                              check_metadata=True,
                              ignore=None):
    """Upload a directory of spatial data files to GeoNode

    Input
        directory: Valid root directory for layer files
        user: Django User object
        overwrite: Boolean variable controlling whether existing layers
                   can be overwritten by this operation. Default is True
        check_metadata: See save_file_to_geonode
        ignore: None or list of filenames to ignore
    Output
        list of layer objects
    """

    if ignore is None:
        ignore = []

    msg = ('Argument %s to save_directory_to_geonode is not a valid directory.'
           % directory)
    assert os.path.isdir(directory), msg

    layers = []
    for root, _, files in os.walk(directory):
        for short_filename in files:
            if short_filename in ignore:
                continue

            _, extension = os.path.splitext(short_filename)
            filename = os.path.join(root, short_filename)

            # Attempt upload only if extension is recognised
            if extension in LAYER_TYPES:
                try:
                    layer = save_to_geonode(filename,
                                            user=user,
                                            title=title,
                                            overwrite=overwrite,
                                            check_metadata=check_metadata)

                except Exception, e:
                    msg = ('Filename "%s" could not be uploaded. '
                           'Error was: %s' % (filename, str(e)))
                    raise RisikoException(msg)
                else:
                    layers.append(layer)

    # Return layers that successfully uploaded
    return layers


def save_to_geonode(incoming, user=None, title=None,
                    overwrite=True, check_metadata=True,
                    ignore=None):
    """Save a files to local Risiko GeoNode

    Input
        incoming: Either layer file or directory
        user: Django User object
        title: If specified, it will be applied to all files. If None or ''
               filenames will be used to infer titles.
        overwrite: Boolean variable controlling whether existing layers
                   can be overwritten by this operation. Default is True
        check_metadata: See save_file_to_geonode
        ignore: None or list of filenames to ignore

        FIXME (Ole): WxS contents does not reflect the renaming done
                     when overwrite is False. This should be reported to
                     the geonode-dev mailing list

    Output
        layer object or list of layer objects
    """

    msg = ('First argument to save_to_geonode must be a string. '
           'I got %s' % incoming)
    assert isinstance(incoming, basestring), msg

    if os.path.isdir(incoming):
        # Upload all valid layer files in this dir recursively
        layers = save_directory_to_geonode(incoming, title=title, user=user,
                                           overwrite=overwrite,
                                           check_metadata=check_metadata,
                                           ignore=ignore)
        return layers
    elif os.path.isfile(incoming):
        # Upload single file (using its name as title)
        layer = save_file_to_geonode(incoming, title=title, user=user,
                                     overwrite=overwrite,
                                     check_metadata=check_metadata,
                                     ignore=ignore)
        return layer
    else:
        msg = 'Argument %s was neither a file or a directory' % incoming
        raise RisikoException(msg)
