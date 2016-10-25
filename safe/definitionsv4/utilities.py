# coding=utf-8

"""Utilities module for helping definitions retrieval.
"""
from copy import deepcopy
from safe import definitionsv4
from safe.definitionsv4 import (
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
    settings
)
from safe.utilities.i18n import tr

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
    :type replace_null: None, bool

    :returns: List of fields.
    :rtype: list
    """
    fields = []
    if layer_purpose == 'exposure':
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            fields = subcategory['fields'] + subcategory['extra_fields']
        else:
            fields = deepcopy(exposure_fields)
    elif layer_purpose == 'hazard':
        if layer_subcategory:
            subcategory = definition(layer_subcategory)
            fields = subcategory['fields'] + subcategory['extra_fields']
        else:
            fields = deepcopy(hazard_fields)
    elif layer_purpose == 'aggregation':
        fields = deepcopy(aggregation_fields)
    elif layer_purpose == 'impact':
        fields = deepcopy(impact_fields)

    if isinstance(replace_null, bool):
        fields = [
            field for field in fields if field['replace_null'] == replace_null]
        return fields
    else:
        return fields


def get_class_field(layer_purpose):
    """Get class field based on layer_purpose.

    :param layer_purpose: The layer purpose.
    :type layer_purpose: str

    :returns: Class field
    :rtype: dict
    """
    if layer_purpose == 'hazard':
        return hazard_value_field
    elif layer_purpose == 'exposure':
        return exposure_type_field
    elif layer_purpose == 'aggregation':
        return aggregation_name_field
    else:
        return None


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


def get_defaults(field_key):
    """Obtain default value for a field with default value.

    By default it will return label list and default value list
    label: [Setting, Do not use, Custom]
    values: [Value from setting, None, Value from QSetting (if exist)]

    :param field_key: The field's key.
    :type field_key: str

    :returns: Tuple of list. List of labels and list of values.
    """
    labels = [tr('Setting (%s)'), tr('Do not use'), tr('Custom')]
    values = [
        settings.default_values.get(field_key, None),
        None,
        settings.qsetting.get(field_key, None)
    ]

    return labels, values