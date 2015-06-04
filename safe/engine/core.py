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
from safe.utilities.utilities import replace_accentuated_characters
from safe.engine.utilities import REQUIRED_KEYWORDS


# The LOGGER is intialised in utilities.py by init
import logging
LOGGER = logging.getLogger('InaSAFE')


def check_data_integrity(layer_objects):
    """Check list of layer objects

    :param layer_objects: List of InaSAFE layer instances
    :type layer_objects: list

    :raises: Exceptions for a range of errors

    This function checks that
    * Layers have correct keywords
    * That they have the same georeferences
    """

    # Link to documentation
    inasafe_url = 'http://inasafe.org/en/developer-docs/'
    instructions = (
        'Please add keywords as <keyword>:<value> pairs  in the .xml '
        'file. For more information please read the sections on impact '
        'functions and keywords in the InaSAFE website: %s' % inasafe_url)

    # Set default values for projection and geo_transform.
    # Enforce DEFAULT (WGS84).
    # Choosing 'None' will use value of first layer.
    reference_projection = Projection(DEFAULT_PROJECTION)
    geo_transform = None

    for layer in layer_objects:
        # Check that critical keywords exist and are non empty
        keywords = layer.get_keywords()
        for keyword in REQUIRED_KEYWORDS:
            message = (
                'Layer %s did not have required keyword "%s". %s' % (
                    layer.name, keyword, instructions))
            verify(keyword in keywords, message)

            value = keywords[keyword]
            message = (
                'No value found for keyword "%s" in layer %s. %s' % (
                    keyword, layer.name, instructions))
            verify(value, message)

        # Ensure that projection is consistent across all layers
        if reference_projection is None:
            reference_projection = layer.projection
        else:
            message = (
                'Projections in input layer %s is not as expected:\n'
                'projection: %s\n default: %s' % (
                    layer, layer.projection, reference_projection))
            verify(reference_projection == layer.projection, message)

        # FIXME (Ariel): Make this configurable by the frontend choice?
        # Relax tolerance requirements to have GeoNode compatibility
        # tolerance = 10e-12
        tolerance = 10e-7

        # Ensure that geo_transform and dimensions is consistent across
        # all *raster* layers
        if layer.is_raster:
            if geo_transform is None:
                geo_transform = layer.get_geotransform()
            else:
                message = (
                    'Geotransforms in input raster layers are different:\n'
                    '%s\n%s' % (geo_transform, layer.get_geotransform()))
                verify(
                    numpy.allclose(
                        geo_transform,
                        layer.get_geotransform(),
                        rtol=tolerance),
                    message)

        # In case of vector layers, we just check that they are non-empty
        # FIXME (Ole): Not good as nasty error is raised in cases where
        # there are no buildings in the hazard area. Need to be more graceful
        # See e.g. shakemap dated 20120227190230
        if layer.is_vector:
            message = (
                'There are no vector data features. Perhaps zoom out or pan '
                'to the study area and try again')
            verify(len(layer) > 0, message)

    # Check that arrays are aligned.
    refname = None
    for layer in layer_objects:
        if layer.is_raster:
            if refname is None:
                refname = layer.get_name()
                layer_rows = layer.rows
                layer_columns = layer.columns

            message = (
                'Rasters are not aligned!\n'
                'Raster %s has %i rows but raster %s has %i rows\n'
                'Refer to issue #102' % (
                    layer.get_name(), layer.rows, refname, layer_rows))
            verify(layer.rows == layer_rows, message)

            message = (
                'Rasters are not aligned!\n'
                'Raster %s has %i columns but raster %s has %i columns\n'
                'Refer to issue #102' % (
                    layer.get_name(), layer.columns, refname, layer_columns))
            verify(layer.columns == layer_columns, message)


def calculate_impact(
        layers, impact_function, extent=None, check_integrity=True):
    """Calculate impact levels as a function of list of input layers

    :param layers: List of Raster and Vector layer objects to be used for
        analysis.
    :type layers: list

    :param impact_function: An instance of impact function.
    :type impact_function: safe.impact_function.base.ImpactFunction

    :param extent: List of [xmin, ymin, xmax, ymax] the coordinates of the
        bounding box.
    :type extent: list

    :param check_integrity: If true, perform checking of input data integrity
    :type check_integrity: bool

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
            layers, impact_function))

    # Input checks
    if check_integrity:
        check_data_integrity(layers)

    # Set extent if it is provided
    if extent is not None:
        impact_function.requested_extent = extent

    # Start time
    start_time = datetime.now()

    # Pass input layers to plugin
    result_layer = impact_function.run(layers)

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
    for layer_purpose in ['hazard', 'exposure']:
        layer = extract_layers(layers, 'layer_purpose', layer_purpose)
        keywords = layer[0].get_keywords()
        not_specified = tr('Not specified')
        if 'title' in keywords:
            title = keywords['title']
        else:
            title = not_specified

        if 'source' in keywords:
            source = keywords['source']
        else:
            source = not_specified

        if 'hazard' in keywords:
            subcategory = keywords['hazard']
        elif 'exposure' in keywords:
            subcategory = keywords['exposure']
        else:
            subcategory = not_specified

        result_layer.keywords['%s_title' % layer_purpose] = title
        result_layer.keywords['%s_source' % layer_purpose] = source
        result_layer.keywords['%s_subcategory' % layer_purpose] = subcategory

    result_layer.keywords['elapsed_time'] = elapsed_time_sec
    result_layer.keywords['time_stamp'] = time_stamp[:19]  # remove decimal
    result_layer.keywords['host_name'] = host_name
    result_layer.keywords['user'] = user

    msg = 'Impact function %s returned None' % str(impact_function)
    verify(result_layer is not None, msg)

    # Set the filename : issue #1648
    # EXP + On + Haz + DDMMMMYYYY + HHhMM.SS.EXT
    # FloodOnBuildings_12March2015_10h22.04.shp
    exp = result_layer.keywords['exposure_subcategory'].title()
    haz = result_layer.keywords['hazard_subcategory'].title()
    date = end_time.strftime('%d%B%Y').decode('utf8')
    time = end_time.strftime('%Hh%M.%S').decode('utf8')
    prefix = u'%sOn%s_%s_%s-' % (haz, exp, date, time)
    prefix = replace_accentuated_characters(prefix)

    # Write result and return filename
    if result_layer.is_raster:
        extension = '.tif'
        # use default style for raster
    else:
        extension = '.shp'
        # use default style for vector

    # Check if user directory is specified
    settings = QSettings()
    default_user_directory = settings.value(
        'inasafe/defaultUserDirectory', defaultValue='')

    if default_user_directory:
        output_filename = unique_filename(
            dir=default_user_directory,
            prefix=prefix,
            suffix=extension)
    else:
        output_filename = unique_filename(
            prefix=prefix, suffix=extension)

    result_layer.filename = output_filename
    result_layer.write_to_file(output_filename)

    # Establish default name (layer1 X layer1 x impact_function)
    if not result_layer.get_name():
        default_name = ''
        for layer in layers:
            default_name += layer.name + ' X '

        if hasattr(impact_function, 'plugin_name'):
            default_name += impact_function.plugin_name
        else:
            # Strip trailing 'X'
            default_name = default_name[:-2]

        result_layer.set_name(default_name)

    # FIXME (Ole): If we need to save style as defined by the impact_function
    # this is the place

    # Return layer object
    return result_layer
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
