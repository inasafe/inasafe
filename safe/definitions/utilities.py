# coding=utf-8
"""Utilities module for helping definitions retrieval."""

from copy import deepcopy

from safe import definitions
from safe.definitions import fields
from safe.definitions import (
    layer_purposes,
    hazard_all,
    exposure_all,
    hazard_category_all,
    aggregation_fields,
    impact_fields,
    aggregation_name_field,
    hazard_value_field,
    exposure_type_field,
    exposure_fields,
    hazard_fields,
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    layer_purpose_exposure_summary
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def purposes_for_layer(layer_geometry_key):
    """Get purposes of a layer geometry id.

    :param layer_geometry_key: The geometry id
    :type layer_geometry_key: str

    :returns: List of suitable layer purpose.
    :rtype: list
    """
    return_value = []
    for layer_purpose in layer_purposes:
        layer_geometry_keys = [
            i['key'] for i in layer_purpose['allowed_geometries']]
        if layer_geometry_key in layer_geometry_keys:
            return_value.append(layer_purpose['key'])

    return sorted(return_value)


def hazards_for_layer(layer_geometry_key, hazard_category_key=None):
    """Get hazard categories form layer_geometry_key.

    :param layer_geometry_key: The geometry id
    :type layer_geometry_key: str

    :param hazard_category_key: The hazard category
    :type hazard_category_key: str

    :returns: List of hazard
    :rtype: list
    """
    result = []
    for hazard in hazard_all:
        if layer_geometry_key in hazard.get('allowed_geometries'):
            result.append(hazard)

    return sorted(result, key=lambda k: k['key'])


def exposures_for_layer(layer_geometry_key):
    """Get hazard categories form layer_geometry_key

    :param layer_geometry_key: The geometry key
    :type layer_geometry_key: str

    :returns: List of hazard
    :rtype: list
    """
    result = []
    for exposure in exposure_all:
        if layer_geometry_key in exposure.get('allowed_geometries'):
            result.append(exposure)

    return sorted(result, key=lambda k: k['key'])


def hazard_categories_for_layer():
    """Get hazard categories

    :returns: List of hazard_categories
    :rtype: list
    """
    return sorted(hazard_category_all, key=lambda k: k['key'])


def get_layer_modes(subcategory):
    """Return all sorted layer modes from exposure or hazard.

    :param subcategory: Hazard or Exposure key.
    :type subcategory: str

    :returns: List of layer modes definition.
    :rtype: list
    """
    layer_modes = definition(subcategory)['layer_modes']
    return sorted(layer_modes, key=lambda k: k['key'])


def hazard_units(hazard):
    """Helper to get unit of a hazard.

    :param hazard: Hazard type.
    :type hazard: str

    :returns: List of hazard units.
    :rtype: list
    """
    units = definition(hazard)['continuous_hazard_units']
    return sorted(units, key=lambda k: k['key'])


def exposure_units(exposure):
    """Helper to get unit of an exposure.

    :param exposure: Exposure type.
    :type exposure: str

    :returns: List of exposure units.
    :rtype: list
    """
    units = definition(exposure)['units']
    return sorted(units, key=lambda k: k['key'])


def get_classifications(subcategory_key):
    """Get hazard or exposure classifications.

    :param subcategory_key: The hazard or exposure key
    :type subcategory_key: str

    :returns: List of hazard or exposure classifications
    :rtype: list
    """
    classifications = definition(subcategory_key)['classifications']
    return sorted(classifications, key=lambda k: k['key'])


def get_fields(layer_purpose, layer_subcategory=None, replace_null=None):
    """Get all field based on the layer purpose.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :param replace_null: If None all fields are returned, if True only if
        it's True, if False only if it's False.
    :type replace_null: None or bool

    :returns: List of fields.
    :rtype: list
    """
    fields_for_purpose = []
    if layer_purpose == layer_purpose_exposure['key']:
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            fields_for_purpose += subcategory['compulsory_fields']
            fields_for_purpose += subcategory['fields']
            fields_for_purpose += subcategory['extra_fields']
        else:
            fields_for_purpose = deepcopy(exposure_fields)
    elif layer_purpose == layer_purpose_hazard['key']:
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            fields_for_purpose += subcategory['compulsory_fields']
            fields_for_purpose += subcategory['fields']
            fields_for_purpose += subcategory['extra_fields']
        else:
            fields_for_purpose = deepcopy(hazard_fields)
    elif layer_purpose == layer_purpose_aggregation['key']:
        fields_for_purpose = deepcopy(aggregation_fields)
    elif layer_purpose == layer_purpose_exposure_summary['key']:
        fields_for_purpose = deepcopy(impact_fields)

    if isinstance(replace_null, bool):
        fields_for_purpose = [
            f for f in fields_for_purpose
            if f.get('replace_null') == replace_null]
        return fields_for_purpose
    else:
        return fields_for_purpose


def get_compulsory_fields(layer_purpose, layer_subcategory=None):
    """Get compulsory field based on layer_purpose and layer_subcategory

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :returns: Compulsory field
    :rtype: dict
    """
    if not layer_subcategory:
        if layer_purpose == 'hazard':
            return hazard_value_field
        elif layer_purpose == 'exposure':
            return exposure_type_field
        elif layer_purpose == 'aggregation':
            return aggregation_name_field
        else:
            return None
    else:
        return definition(layer_subcategory).get('compulsory_fields')[0]


def get_non_compulsory_fields(layer_purpose, layer_subcategory=None):
    """Get non compulsory field based on layer_purpose and layer_subcategory.

    Used for get field in InaSAFE Fields step in wizard.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :returns: Compulsory fields
    :rtype: list
    """
    all_fields = get_fields(
        layer_purpose, layer_subcategory, replace_null=False)
    compulsory_field = get_compulsory_fields(
        layer_purpose, layer_subcategory)
    if compulsory_field in all_fields:
        all_fields.remove(compulsory_field)
    return all_fields


def definition(keyword):
    """Given a keyword, try to get a definition dict for it.

    .. versionadded:: 3.2

    Definition dicts are defined in keywords.py. We try to return
    one if present, otherwise we return none. Using this method you
    can present rich metadata to the user e.g.

    keyword = 'layer_purpose'
    kio = safe.utilities.keyword_io.Keyword_IO()
    definition = kio.definition(keyword)
    print definition

    :param keyword: A keyword key.
    :type keyword: str

    :returns: A dictionary containing the matched key definition
        from definitions, otherwise None if no match was found.
    :rtype: dict, None
    """

    for item in dir(definitions):
        if not item.startswith("__"):
            var = getattr(definitions, item)
            if isinstance(var, dict):
                if var.get('key') == keyword:
                    return var
    return None


def get_allowed_geometries(layer_purpose_key):
    """Helper function to get all possible geometry

    :param layer_purpose_key: A layer purpose key.
    :type layer_purpose_key: str

    :returns: List of all allowed geometries.
    :rtype: list
    """
    preferred_order = [
        'point',
        'line',
        'polygon',
        'raster'
    ]
    allowed_geometries = set()
    all_layer_type = []
    if layer_purpose_key == layer_purpose_hazard['key']:
        all_layer_type = hazard_all
    elif layer_purpose_key == layer_purpose_exposure['key']:
        all_layer_type = exposure_all

    for layer in all_layer_type:
        for allowed_geometry in layer['allowed_geometries']:
            allowed_geometries.add(allowed_geometry)

    allowed_geometries = list(allowed_geometries)
    allowed_geometries_definition = []
    for allowed_geometry in allowed_geometries:
        allowed_geometries_definition.append(definition(allowed_geometry))

    # Adapted from http://stackoverflow.com/a/15650556/1198772
    order_dict = {color: index for index, color in enumerate(preferred_order)}
    allowed_geometries_definition.sort(key=lambda x: order_dict[x["key"]])

    return allowed_geometries_definition


def all_default_fields():
    """Helper to retrieve all fields which has default value.

    :returns: List of default fields.
    :rtype: list
    """
    default_fields = []
    for item in dir(fields):
        if not item.startswith("__"):
            var = getattr(definitions, item)
            if isinstance(var, dict):
                if var.get('replace_null', False):
                    default_fields.append(var)
    return default_fields


def postprocessor_output_field(postprocessor_definition):
    """Extract postprocessor output field definition.

    :param postprocessor_definition: Postprocessor definition
    :type postprocessor_definition: dict

    :return: Field definition of postprocessor output
    :rtype: dict
    """
    return postprocessor_definition['output'].items()[0][1]['value']


def default_classification_thresholds(classification, unit=None):
    """Helper to get default thresholds from classification and unit.

    :param classification: Classification definition.
    :type classification: dict

    :param unit: Unit key definition.
    :type unit: basestring

    :returns: Dictionary with key = the class key and value = list of
        default numeric minimum and maximum value.
    :rtype: dict
    """
    thresholds = {}
    for hazard_class in classification['classes']:
        if isinstance(hazard_class['numeric_default_min'], dict):
            min_value = hazard_class['numeric_default_min'][unit]
        else:
            min_value = hazard_class['numeric_default_min']
        if isinstance(hazard_class['numeric_default_max'], dict):
            max_value = hazard_class['numeric_default_max'][unit]
        else:
            max_value = hazard_class['numeric_default_max']
        thresholds[hazard_class['key']] = [min_value, max_value]

    return thresholds


def default_classification_value_maps(classification):
    """Helper to get default value maps from classification.

    :param classification: Classification definition.
    :type classification: dict

    :returns: Dictionary with key = the class key and value = default strings.
    :rtype: dict
    """
    value_maps = {}
    for hazard_class in classification['classes']:
        value_maps[hazard_class['key']] = hazard_class.get(
            'string_defaults', [])

    return value_maps
