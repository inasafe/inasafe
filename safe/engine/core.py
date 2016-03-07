# coding=utf-8
"""Computational engine for InaSAFE core.

Provides the function calculate_impact()
"""

import numpy
from datetime import datetime
import logging

from PyQt4.QtCore import QSettings

from safe.common.exceptions import RadiiException
from safe.gis.geodesy import Point
from safe.storage.geometry import Polygon
from safe.storage.projection import Projection
from safe.storage.projection import DEFAULT_PROJECTION
from safe.common.utilities import unique_filename, verify
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.utilities.utilities import replace_accentuated_characters


# The LOGGER is initialised in utilities.py by init
LOGGER = logging.getLogger('InaSAFE')

# Mandatory keywords that must be present in layers
REQUIRED_KEYWORDS = ['layer_purpose', 'layer_mode']
REQUIRED_HAZARD_KEYWORDS = ['hazard', 'hazard_category']
REQUIRED_EXPOSURE_KEYWORDS = ['exposure']


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

    for safe_layer in layer_objects:
        # Check that critical keywords exist and are non empty
        keywords = safe_layer.keywords
        for keyword in REQUIRED_KEYWORDS:
            message = (
                'Layer %s did not have required keyword "%s". %s' % (
                    safe_layer.name, keyword, instructions))
            verify(keyword in keywords, message)

            value = keywords[keyword]
            message = (
                'No value found for keyword "%s" in layer %s. %s' % (
                    keyword, safe_layer.name, instructions))
            verify(value, message)

        # Ensure that projection is consistent across all layers
        if reference_projection is None:
            reference_projection = safe_layer.projection
        else:
            message = (
                'Projections in input layer %s is not as expected:\n'
                'projection: %s\n default: %s' % (
                    safe_layer,
                    safe_layer.layer.projection,
                    reference_projection))
            verify(
                reference_projection == safe_layer.layer.projection, message)

        # FIXME (Ariel): Make this configurable by the frontend choice?
        # Relax tolerance requirements to have GeoNode compatibility
        # tolerance = 10e-12
        tolerance = 10e-7

        # Ensure that geo_transform and dimensions is consistent across
        # all *raster* layers
        if safe_layer.layer.is_raster:
            if geo_transform is None:
                geo_transform = safe_layer.layer.get_geotransform()
            else:
                message = (
                    'Geotransforms in input raster layers are different:\n'
                    '%s\n%s' % (
                        geo_transform, safe_layer.layer.get_geotransform()))
                verify(
                    numpy.allclose(
                        geo_transform,
                        safe_layer.layer.get_geotransform(),
                        rtol=tolerance),
                    message)

        # In case of vector layers, we just check that they are non-empty
        # FIXME (Ole): Not good as nasty error is raised in cases where
        # there are no buildings in the hazard area. Need to be more graceful
        # See e.g. shakemap dated 20120227190230
        if safe_layer.layer.is_vector:
            message = (
                'There are no vector data features. Perhaps zoom out or pan '
                'to the study area and try again')
            verify(len(safe_layer.layer) > 0, message)

    # Check that arrays are aligned.
    refname = None
    for safe_layer in layer_objects:
        if safe_layer.layer.is_raster:
            if refname is None:
                refname = safe_layer.name
                layer_rows = safe_layer.layer.rows
                layer_columns = safe_layer.layer.columns

            message = (
                'Rasters are not aligned!\n'
                'Raster %s has %i rows but raster %s has %i rows\n'
                'Refer to issue #102' % (
                    safe_layer.name,
                    safe_layer.layer.rows,
                    refname,
                    layer_rows))
            verify(safe_layer.layer.rows == layer_rows, message)

            message = (
                'Rasters are not aligned!\n'
                'Raster %s has %i columns but raster %s has %i columns\n'
                'Refer to issue #102' % (
                    safe_layer.name,
                    safe_layer.layer.columns,
                    refname,
                    layer_columns))
            verify(safe_layer.layer.columns == layer_columns, message)


def calculate_impact(impact_function):
    """Calculate impact levels as a function of list of input layers

    :param impact_function: An instance of impact function.
    :type impact_function: safe.impact_function.base.ImpactFunction

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
    layers = [impact_function.hazard, impact_function.exposure]
    # Input checks
    if impact_function.requires_clipping:
        check_data_integrity(layers)

    # Start time
    start_time = datetime.now()

    # Run IF
    result_layer = impact_function.run_analysis()

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

    # Get input layer sources
    # NOTE: We assume here that there is only one of each
    #       If there are more only the first one is used
    for layer in layers:
        keywords = layer.keywords
        not_specified = tr('Not specified')

        layer_purpose = keywords.get('layer_purpose', not_specified)
        title = keywords.get('title', not_specified)
        source = keywords.get('source', not_specified)

        if layer_purpose == 'hazard':
            category = keywords['hazard']
        elif layer_purpose == 'exposure':
            category = keywords['exposure']
        else:
            category = not_specified

        result_layer.keywords['%s_title' % layer_purpose] = title
        result_layer.keywords['%s_source' % layer_purpose] = source
        result_layer.keywords['%s' % layer_purpose] = category

    result_layer.keywords['elapsed_time'] = elapsed_time_sec
    result_layer.keywords['time_stamp'] = time_stamp[:19]  # remove decimal
    result_layer.keywords['host_name'] = impact_function.host_name
    result_layer.keywords['user'] = impact_function.user

    msg = 'Impact function %s returned None' % str(impact_function)
    verify(result_layer is not None, msg)

    # Set the filename : issue #1648
    # EXP + On + Haz + DDMMMMYYYY + HHhMM.SS.EXT
    # FloodOnBuildings_12March2015_10h22.04.shp
    exp = result_layer.keywords['exposure'].title()
    haz = result_layer.keywords['hazard'].title()
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

    # Return layer object
    return result_layer


def buffer_points(centers, radii, hazard_zone_attribute, data_table=None):
    """Buffer points for each center with defined radii.

    If the data_table is defined, then the data will also be copied to the
    result. This function is used for making buffer of volcano point hazard.

    :param centers: All center of each point (longitude, latitude)
    :type centers: list

    :param radii: Desired approximate radii in kilometers (must be
        monotonically ascending). Can be either one number or list of numbers
    :type radii: int, list

    :param hazard_zone_attribute: The name of the attributes representing
        hazard zone.
    :type hazard_zone_attribute: str

    :param data_table: Data for each center (optional)
    :type data_table: list

    :return: Vector polygon layer representing circle in WGS84
    :rtype: Vector
    """
    if not isinstance(radii, list):
        radii = [radii]

    # Check that radii are monotonically increasing
    monotonically_increasing_flag = all(
        x < y for x, y in zip(radii, radii[1:]))
    if not monotonically_increasing_flag:
        raise RadiiException(RadiiException.suggestion)

    circles = []
    new_data_table = []
    for i, center in enumerate(centers):
        p = Point(longitude=center[0], latitude=center[1])
        inner_rings = None
        for radius in radii:
            # Generate circle polygon
            circle = p.generate_circle(radius * 1000)
            circles.append(Polygon(outer_ring=circle, inner_rings=inner_rings))

            # Store current circle and inner ring for next poly
            inner_rings = [circle]

            # Carry attributes for center forward (deep copy)
            row = {}
            if data_table is not None:
                for key in data_table[i]:
                    row[key] = data_table[i][key]

            # Add radius to this ring
            row[hazard_zone_attribute] = radius

            new_data_table.append(row)

    circular_polygon = Vector(
        geometry=circles,  # List with circular polygons
        data=new_data_table,  # Associated attributes
        geometry_type='polygon')

    return circular_polygon
