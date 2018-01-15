# coding=utf-8

"""Definitions relating to pre-processing."""

import logging
import os

from safe.definitions.exposure import exposure_place
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_nearby_places,
    layer_purpose,
    layer_purpose_earthquake_contour,
)
from safe.gis.raster.contour import create_smooth_contour
from safe.processors import (
    function_process,
)
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


def check_nearby_preprocessor(impact_function):
    """Checker for the nearby preprocessor.

    :param impact_function: Impact function to check.
    :type impact_function: ImpactFunction

    :return: If the preprocessor can run.
    :rtype: bool
    """
    hazard_key = layer_purpose_hazard['key']
    earthquake_key = hazard_earthquake['key']
    exposure_key = layer_purpose_exposure['key']
    place_key = exposure_place['key']
    if impact_function.hazard.keywords.get(hazard_key) == earthquake_key:
        if impact_function.exposure.keywords.get(exposure_key) == place_key:
            return True
    return False


def fake_nearby_preprocessor(impact_function):
    """Fake nearby preprocessor.

    We can put here the function to generate contours or nearby places.

    It must return a layer with a specific layer_purpose.

    :return: The output layer.
    :rtype: QgsMapLayer
    """
    _ = impact_function  # NOQA
    from safe.test.utilities import load_test_vector_layer
    fake_layer = load_test_vector_layer(
        'gisv4',
        'impacts',
        'building-points-classified-vector.geojson',
        clone_to_memory=True)
    return fake_layer


pre_processors_nearby_places = {
    'key': 'pre_processor_nearby_places',
    'name': tr('Nearby Places Pre Processor'),
    'description': tr('A fake pre processor.'),
    'condition': check_nearby_preprocessor,
    'process': {
        'type': function_process,
        'function': fake_nearby_preprocessor,
    },
    'output': {
        'type': 'layer',
        'key': layer_purpose,
        'value': layer_purpose_nearby_places,
    }
}


def check_earthquake_contour_preprocessor(impact_function):
    """Checker for the contour preprocessor.

    :param impact_function: Impact function to check.
    :type impact_function: ImpactFunction

    :return: If the preprocessor can run.
    :rtype: bool
    """
    hazard_key = impact_function.hazard.keywords.get('hazard')
    is_earthquake = hazard_key == hazard_earthquake['key']

    if is_earthquake and is_raster_layer(impact_function.hazard):
        return True
    else:
        return False


def earthquake_contour_preprocessor(impact_function):
    """Preprocessor to create contour from an earthquake

    :param impact_function: Impact function to run.
    :type impact_function: ImpactFunction

    :return: The contour layer.
    :rtype: QgsMapLayer
    """
    contour_path = create_smooth_contour(impact_function.hazard)

    if os.path.exists(contour_path):
        from safe.gis.tools import load_layer
        return load_layer(contour_path, tr('Contour'), 'ogr')[0]


pre_processor_earthquake_contour = {
    'key': 'pre_processor_earthquake_contour',
    'name': tr('Earthquake Contour Pre Processor'),
    'description': tr(
        'A pre processor to create contour from a hazard earthquake.'),
    'condition': check_earthquake_contour_preprocessor,
    'process': {
        'type': function_process,
        'function': earthquake_contour_preprocessor,
    },
    'output': {
        'type': 'layer',
        'key': layer_purpose,
        'value': layer_purpose_earthquake_contour,
    }
}
