# coding=utf-8
"""Computational engine for InaSAFE core.

Provides the function calculate_impact()
"""

import numpy
from datetime import datetime
from socket import gethostname
import getpass
from PyQt4.QtCore import QSettings

from safe.storage.projection import Projection
from safe.storage.projection import DEFAULT_PROJECTION
from safe.impact_functions.core import extract_layers
from safe.common.utilities import unique_filename, verify
from safe.utilities.i18n import tr
from safe.engine.utilities import REQUIRED_KEYWORDS


# The LOGGER is intialised in utilities.py by init
import logging
LOGGER = logging.getLogger('InaSAFE')


def calculate_impact(layers, impact_fcn, extent=None, check_integrity=True):
    """Calculate impact levels as a function of list of input layers

    Input
        layers: List of Raster and Vector layer objects to be used for analysis

        impact_fcn: Function of the form f(layers)

        extent:     List of [xmin, ymin, xmax, ymax]
                    the coordinates of the bounding box.

        check_integrity:    If true, perform checking of input data integrity

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

    LOGGER.debug(
        'calculate_impact called with:\nLayers: %s\nFunction:%s' % (
            layers, impact_fcn))

    # Input checks
    if check_integrity:
        check_data_integrity(layers)

    # Get an instance of the passed impact_fcn
    impact_function = impact_fcn()
    # Set extent if it is provided
    if extent is not None:
        impact_function.set_extent(extent)

    # Start time
    start_time = datetime.now()

    # Pass input layers to plugin
    F = impact_function.run(layers)

    # End time
    end_time = datetime.now()

    # Elapsed time
    elapsed_time = end_time - start_time
    # Don's use this - see https://github.com/AIFDR/inasafe/issues/394
    # elapsed_time_sec = elapsed_time.total_seconds()
    elapsed_time_sec = elapsed_time.seconds + (elapsed_time.days * 24 * 3600)

    # Eet current time stamp
    # Need to change : to _ because : is forbidden in keywords
    time_stamp = end_time.isoformat('_')

    # Get user
    user = getpass.getuser().replace(' ', '_')

    # Get host
    host_name = gethostname()

    # Get input layer sources
    # NOTE: We assume here that there is only one of each
    #       If there are more only the first one is used
    for cat in ['hazard', 'exposure']:
        L = extract_layers(layers, 'category', cat)
        keywords = L[0].get_keywords()
        not_specified = tr('Not specified')
        if 'title' in keywords:
            title = keywords['title']
        else:
            title = not_specified

        if 'source' in keywords:
            source = keywords['source']
        else:
            source = not_specified

        if 'subcategory' in keywords:
            subcategory = keywords['subcategory']
        else:
            subcategory = not_specified

        F.keywords['%s_title' % cat] = title
        F.keywords['%s_source' % cat] = source
        F.keywords['%s_subcategory' % cat] = subcategory

    F.keywords['elapsed_time'] = elapsed_time_sec
    F.keywords['time_stamp'] = time_stamp[:19]  # remove decimal part
    F.keywords['host_name'] = host_name
    F.keywords['user'] = user

    msg = 'Impact function %s returned None' % str(impact_function)
    verify(F is not None, msg)

    # Set the filename
    # EXP + On + Haz + DDMMMMYYYY + HHhMM.SS.EXT
    # FloodOnBuildings_12March2015_10h22.04.shp
    exp = F.keywords['exposure_subcategory'].title()
    haz = F.keywords['hazard_subcategory'].title()
    date = end_time.strftime('%d%B%Y').decode('utf8')
    time = end_time.strftime('%Hh%M.%S').decode('utf8')
    prefix = '%sOn%s_%s_%s-' % (haz, exp, date, time)

    # Write result and return filename
    if F.is_raster:
        extension = '.tif'
        # use default style for raster
    else:
        extension = '.shp'
        # use default style for vector

    # Check if user directory is specified
    settings = QSettings()
    default_user_directory = settings.value('inasafe/defaultUserDirectory', None, type=str)

    if default_user_directory:
        # encode to UTF-8 : http://gis.stackexchange.com/questions/53920/ogr-createlayer-returns-typeerror
        output_filename = unique_filename(
            dir=default_user_directory,
            prefix=prefix,
            suffix=extension).encode('utf-8')
    else:
        output_filename = unique_filename(prefix=prefix, suffix=extension)

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
    # this is the place

    # Return layer object
    return F


def check_data_integrity(layer_objects):
    """Check list of layer objects

    Input
        layer_objects: List of InaSAFE layer instances

    Output
        Nothing

    Raises
        Exceptions for a range of errors

    This function checks that
    * Layers have correct keywords
    * That they have the same georeferences
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

    for layer in layer_objects:

        # Check that critical keywords exist and are non empty
        keywords = layer.get_keywords()
        for kw in REQUIRED_KEYWORDS:
            msg = ('Layer %s did not have required keyword "%s". '
                   '%s' % (layer.name, kw, instructions))
            verify(kw in keywords, msg)

            val = keywords[kw]
            msg = ('No value found for keyword "%s" in layer %s. '
                   '%s' % (kw, layer.name, instructions))
            verify(val, msg)

        # Ensure that projection is consistent across all layers
        if reference_projection is None:
            reference_projection = layer.projection
        else:
            msg = ('Projections in input layer %s is not as expected:\n'
                   'projection: %s\n'
                   'default:    %s'
                   '' % (layer, layer.projection, reference_projection))
            verify(reference_projection == layer.projection, msg)

        # FIXME (Ariel): Make this configurable by the frontend choice?
        # Relax tolerance requirements to have GeoNode compatibility
        # tolerance = 10e-12
        tolerance = 10e-7

        # Ensure that geotransform and dimensions is consistent across
        # all *raster* layers
        if layer.is_raster:
            if geotransform is None:
                geotransform = layer.get_geotransform()
            else:
                msg = ('Geotransforms in input raster layers are different:\n'
                       '%s\n%s' % (geotransform, layer.get_geotransform()))
                verify(numpy.allclose(geotransform,
                                      layer.get_geotransform(),
                                      rtol=tolerance), msg)

        # In case of vector layers, we just check that they are non-empty
        # FIXME (Ole): Not good as nasty error is raised in cases where
        # there are no buildings in the hazard area. Need to be more graceful
        # See e.g. shakemap dated 20120227190230
        if layer.is_vector:
            msg = ('There are no vector data features. '
                   'Perhaps zoom out or pan to the study area '
                   'and try again')
            verify(len(layer) > 0, msg)

    # Check that arrays are aligned.

    refname = None
    for layer in layer_objects:
        if layer.is_raster:

            if refname is None:
                refname = layer.get_name()
                M = layer.rows
                N = layer.columns

            msg = ('Rasters are not aligned!\n'
                   'Raster %s has %i rows but raster %s has %i rows\n'
                   'Refer to issue #102' % (layer.get_name(),
                                            layer.rows,
                                            refname, M))
            verify(layer.rows == M, msg)

            msg = ('Rasters are not aligned!\n'
                   'Raster %s has %i columns but raster %s has %i columns\n'
                   'Refer to issue #102' % (layer.get_name(),
                                            layer.columns,
                                            refname, N))
            verify(layer.columns == N, msg)

# FIXME (Ole): This needs to be rewritten as it
# directly depends on ows metadata. See issue #54
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
#                 LOGGER.info(msg)
#                 # raise Exception(msg)
#             else:
#                 new_layers.append((server, new_layer, bbox, new_metadata))

#     # Recursively search for linked layers required by the newly added layers
#     if len(new_layers) > 0:
#         new_layers += get_linked_layers(new_layers)

#     # Return list of new layers
#     return new_layers
