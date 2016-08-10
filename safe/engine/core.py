# coding=utf-8
"""Computational engine for InaSAFE core.

Provides the function calculate_impact()
"""

import numpy
import logging

from safe.storage.projection import Projection
from safe.storage.projection import DEFAULT_PROJECTION
from safe.common.utilities import verify


# The LOGGER is initialised in utilities.py by init
LOGGER = logging.getLogger('InaSAFE')

# Mandatory keywords that must be present in layers
REQUIRED_KEYWORDS = ['layer_purpose', 'layer_mode']


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
