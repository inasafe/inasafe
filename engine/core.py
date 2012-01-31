"""Computational engine for Risk in a Box core.

Provides the function calculate_impact()
"""

import os
import sys
import numpy

from storage.projection import Projection
from storage.projection import DEFAULT_PROJECTION
from storage.utilities import unique_filename
from storage.utilities import bbox_intersection
from storage.utilities import buffered_bounding_box
from storage.utilities import is_sequence
from storage.core import bboxlist2string, bboxstring2list
from storage.core import check_bbox_string
from storage.core import read_layer
from utilities import REQUIRED_KEYWORDS

import logging
logger = logging.getLogger('risiko')


def calculate_impact(layers, impact_fcn,
                     comment=''):
    """Calculate impact levels as a function of list of input layers

    Input
        FIXME (Ole): For the moment we take only a list with two
        elements containing one hazard level one exposure level

        layers: List of Raster and Vector layer objects to be used for analysis

        impact_fcn: Function of the form f(layers)
        comment:

    Output
        filename of resulting impact layer (GML). Comment is embedded as
        metadata. Filename is generated from input data and date.

    Note
        The admissible file types are tif and asc/prj for raster and
        gml or shp for vector data

    Assumptions
        1. All layers are in WGS84 geographic coordinates
        2. Layers are equipped with metadata such as names and categories
    """

    # Input checks
    check_data_integrity(layers)

    # Get an instance of the passed impact_fcn
    impact_function = impact_fcn()

    # Pass input layers to plugin
    F = impact_function.run(layers)

    msg = 'Impact function %s returned None' % str(impact_function)
    assert F is not None, msg

    # Write result and return filename
    if F.is_raster:
        extension = '.tif'
        # use default style for raster
    else:
        extension = '.shp'
        # use default style for vector

    output_filename = unique_filename(suffix=extension)
    F.filename = output_filename
    F.write_to_file(output_filename)

    # Establish default name (layer1 X layer1 x impact_function)
    if not F.get_name():
        default_name = ''
        for layer in layers:
            default_name += layer.name + ' X '

        if hasattr(impact_function, 'plugin_name'):
            default_name += impact_function.plugin_name
        else:
            # Strip trailing 'X'
            default_name = default_name[:-2]

        F.set_name(default_name)

    # FIXME (Ole): If we need to save style as defined by the impact_function
    #              this is the place

    # Return layer object
    return F


def check_data_integrity(layer_files):
    """Read list of layer files and verify that that they have correct keywords
    as well as the same projection and georeferencing.
    """

    # Link to documentation
    manpage = ('http://risiko_dev.readthedocs.org/en/latest/usage/'
               'plugins/development.html')
    instructions = ('Please add keywords as <keyword>:<value> pairs '
                    ' in the .keywords file. For more information '
                    'please read the sections on impact functions '
                    'and keywords in the manual: %s' % manpage)

    # Set default values for projection and geotransform.
    # Enforce DEFAULT (WGS84).
    # Choosing 'None' will use value of first layer.
    reference_projection = Projection(DEFAULT_PROJECTION)
    geotransform = None
    coordinates = None

    for layer in layer_files:

        # Check that critical keywords exist and are non empty
        keywords = layer.get_keywords()
        for kw in REQUIRED_KEYWORDS:
            msg = ('Layer %s did not have required keyword "%s". '
                   '%s' % (layer.name, kw, instructions))
            assert kw in keywords, msg

            val = keywords[kw]
            msg = ('No value found for keyword "%s" in layer %s. '
                   '%s' % (kw, layer.name, instructions))
            assert val, msg

        # Ensure that projection is consistent across all layers
        if reference_projection is None:
            reference_projection = layer.projection
        else:
            msg = ('Projections in input layer %s is not as expected:\n'
                   'projection: %s\n'
                   'default:    %s'
                   '' % (layer, layer.projection, reference_projection))
            assert reference_projection == layer.projection, msg

        # Ensure that geotransform and dimensions is consistent across
        # all *raster* layers
        if layer.is_raster:
            if geotransform is None:
                geotransform = layer.get_geotransform()
            else:
                msg = ('Geotransforms in input raster layers are different: '
                       '%s %s' % (geotransform, layer.get_geotransform()))
                # FIXME (Ole): Use high tolerance until we find out
                # why geoserver changes resolution (issue #102)
                assert numpy.allclose(geotransform,
                                      layer.get_geotransform(),
                                      rtol=1.0e-1), msg

        # In either case of vector layers, we check that the coordinates
        # are the same
        if layer.is_vector:
            if coordinates is None:
                coordinates = layer.get_geometry()
            else:
                msg = ('Coordinates in input vector layers are different: '
                       '%s %s' % (coordinates, layer.get_geometry()))
                assert numpy.allclose(coordinates,
                                      layer.get_geometry()), msg

            msg = ('There are no data points to interpolate to. '
                   'Perhaps zoom out or pan to the study area '
                   'and try again')
            assert len(layer) > 0, msg

    # Check that arrays are aligned.
    #
    # We have observerd Geoserver resolution changes - see ticket:102
    # https://github.com/AIFDR/riab/issues/102
    #
    # However, both rasters are now downloaded with exactly the same
    # parameters since we have made bbox and resolution variable in ticket:103
    # https://github.com/AIFDR/riab/issues/103
    #
    # So if they are still not aligned, we raise an Exception

    # First find the minimum dimensions
    M = N = sys.maxint
    refname = ''
    for layer in layer_files:
        if layer.is_raster:
            if layer.rows < M:
                refname = layer.get_name()
                M = layer.rows
            if layer.columns < N:
                refname = layer.get_name()
                N = layer.columns

    # Then check for alignment
    for layer in layer_files:
        if layer.is_raster:
            data = layer.get_data()

            msg = ('Rasters are not aligned!\n'
                   'Raster %s has %i rows but raster %s has %i rows\n'
                   'Refer to issue #102' % (layer.get_name(),
                                            layer.rows,
                                            refname, M))
            assert layer.rows == M, msg

            msg = ('Rasters are not aligned!\n'
                   'Raster %s has %i columns but raster %s has %i columns\n'
                   'Refer to issue #102' % (layer.get_name(),
                                            layer.columns,
                                            refname, N))
            assert layer.columns == N, msg


# FIXME (Ole): This may be obsolete now
# def get_common_resolution(haz_metadata, exp_metadata):
#     """Determine common resolution for raster layers

#     Input
#         haz_metadata: Metadata for hazard layer
#         exp_metadata: Metadata for exposure layer

#     Output
#         raster_resolution: Common resolution or None
# (in case of vector layers)
#     """

#     # Determine resolution in case of raster layers
#     haz_res = exp_res = None
#     if haz_metadata['layer_type'] == 'raster':
#         haz_res = haz_metadata['resolution']

#     if exp_metadata['layer_type'] == 'raster':
#         exp_res = exp_metadata['resolution']

#     # Determine common resolution in case of two raster layers
#     if haz_res is None or exp_res is None:
#         # This means native resolution will be used
#         raster_resolution = None
#     else:
#         # Take the minimum
#         resx = min(haz_res[0], exp_res[0])
#         resy = min(haz_res[1], exp_res[1])

#         raster_resolution = (resx, resy)

#     return raster_resolution


def get_bounding_boxes(haz_data, exp_data, req_bbox):
    """Check and get appropriate bounding boxes for input layers

    Input
        haz_data: Filename or layer object for hazard layer
        exp_data: Filename or layer object for exposure layer
        req_bbox: Bounding box (string as requested by HTML POST, or list)

    Output
        intersection_bbox: Common bounding box which is simply the intersection
                           among hazard, exposure and viewport bounds.
    """

    # Input checks
    if isinstance(haz_data, basestring):
        haz_layer = read_layer(haz_data)
    else:
        haz_layer = haz_data
    msg = 'Input data "%s" was not a valid spatial object' % str(haz_layer)
    assert (hasattr(haz_layer, 'is_riab_spatial_object') and
            haz_layer.is_riab_spatial_object), msg

    if isinstance(exp_data, basestring):
        exp_layer = read_layer(exp_data)
    else:
        exp_layer = exp_data
    msg = 'Input data "%s" was not a valid spatial object' % str(exp_layer)
    assert (hasattr(exp_layer, 'is_riab_spatial_object') and
            exp_layer.is_riab_spatial_object), msg

    try:
        vpt_bbox = list(req_bbox)
    except:
        msg = ('Invalid bounding box %s (%s). It must be a sequence of the '
               'form [west, south, east, north]' % (str(req_bbox),
                                                    type(req_bbox)))
        raise Exception(msg)

    # Get bounding boxes for layers
    haz_bbox = haz_layer.get_bounding_box()
    exp_bbox = exp_layer.get_bounding_box()

    # New bounding box for data common to hazard, exposure and viewport
    # Download only data within this intersection
    intersection_bbox = bbox_intersection(vpt_bbox, haz_bbox, exp_bbox)
    if intersection_bbox is None:
        # Bounding boxes did not overlap
        msg = ('Bounding boxes of hazard data [%s], exposure data [%s] '
               'and viewport [%s] did not overlap, so no computation was '
               'done. Please make sure you pan to where the data is and '
               'that hazard and exposure data overlaps.'
               % (bboxlist2string(haz_bbox, decimals=3),
                  bboxlist2string(exp_bbox, decimals=3),
                  bboxlist2string(vpt_bbox, decimals=3)))
        logger.info(msg)
        raise Exception(msg)

    # Grow hazard bbox to buffer this common bbox in case where
    # hazard is raster and exposure is vector
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # FIXME (Ole): Move this into the caller
    #if (haz_metadata['layer_type'] == 'raster' and
    #    exp_metadata['layer_type'] == 'vector'):#
    #
    #    haz_res = haz_metadata['resolution']
    #    haz_bbox = buffered_bounding_box(intersection_bbox, haz_res)
    #else:
    #    haz_bbox = intersection_bbox

    # Usually the intersection bbox is used for both exposure layer and result
    #exp_bbox = imp_bbox = intersection_bbox

    return intersection_bbox, None


# FIXME (Ole): This needs to be rewritten as it
# directly depends on ows metadata
# def get_linked_layers(main_layers):
#     """Get list of layers that are required by main layers

#     Input
#        main_layers: List of layers of the form (server, layer_name,
#                                                 bbox, metadata)
#     Output
#        new_layers: New layers flagged by the linked keywords in main layers


#     Algorithm will recursively pull layers from new layers if their
#     keyword linked exists and points to available layers.
#     """

#     # FIXME: I don't think the naming is very robust.
#     # Main layer names and workspaces come from the app, while
#     # we just use the basename from the keywords for the linked layers.
#     # Not sure if the basename will always work as layer name.

#     new_layers = []
#     for server, name, bbox, metadata in main_layers:

#         workspace, layername = name.split(':')

#         keywords = metadata['keywords']
#         if 'linked' in keywords:
#             basename, _ = os.path.splitext(keywords['linked'])

#             # FIXME (Ole): Geoserver converts names to lowercase @#!!
#             basename = basename.lower()

#             new_layer = '%s:%s' % (workspace, basename)
#             if new_layer == name:
#                 msg = 'Layer %s linked to itself' % name
#                 raise Exception(msg)

#             try:
#                 new_metadata = get_metadata(server, new_layer)
#             except Exception, e:
#                 msg = ('Linked layer %s could not be found: %s'
#                        % (basename, str(e)))
#                 logger.info(msg)
#                 #raise Exception(msg)
#             else:
#                 new_layers.append((server, new_layer, bbox, new_metadata))

#     # Recursively search for linked layers required by the newly added layers
#     if len(new_layers) > 0:
#         new_layers += get_linked_layers(new_layers)

#     # Return list of new layers
#     return new_layers
