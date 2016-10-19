# coding=utf-8

"""Utilities module for helping definitions retrieval.
"""
from safe import definitionsv4
from safe.definitionsv4 import (
    layer_purposes,
    hazard_all,
    exposure_all,
    hazard_category_all,
    aggregation_fields,
    impact_fields,
    hazard_class_field,
    exposure_class_field,
    aggregation_name_field,
    hazard_value_field,
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

    :returns: List of layer modes defintion.
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


def get_hazard_classifications(hazard_key):
    """Get hazard classifications.

    :param hazard_key: The hazard key
    :type hazard_key: str

    :returns: List of hazards_classifications
    :rtype: list
    """
    classifications = definition(hazard_key)['classifications']
    return sorted(classifications, key=lambda k: k['key'])


def get_fields(layer_purpose, layer_subcategory):
    """Get all field based on the layer purpose.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :param layer_subcategory: Exposure or hazard value.
    :type layer_subcategory: str

    :returns: List of fields.
    :rtype: list
    """
    fields = []
    subcategory = definition(layer_subcategory)
    if layer_purpose == 'exposure':
        fields = subcategory['fields'] + subcategory['extra_fields']
        fields.remove(exposure_class_field)
    elif layer_purpose == 'hazard':
        fields = subcategory['fields'] + subcategory['extra_fields']
        try:
            fields.remove(hazard_class_field)
        except ValueError:
            pass
        try:
            fields.remove(hazard_value_field)
        except ValueError:
            pass
    elif layer_purpose == 'aggregation':
        fields = aggregation_fields
        fields.remove(aggregation_name_field)
    elif layer_purpose == 'impact':
        fields = impact_fields

    return fields


def get_class_field_key(layer_purpose):
    """Get class field based on layer_purpose.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :returns: Class field key.
    :rtype: str
    """
    if layer_purpose == 'hazard':
        return hazard_class_field['key']
    elif layer_purpose == 'exposure':
        return exposure_class_field['key']
    elif layer_purpose == 'aggregation':
        return aggregation_name_field['key']
    else:
        return ''


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

    for item in dir(definitionsv4):
        if not item.startswith("__"):
            var = getattr(definitionsv4, item)
            if isinstance(var, dict):
                if var.get('key') == keyword:
                    return var
    return None
