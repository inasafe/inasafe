# coding=utf-8

"""Definitions relating to minimum-needs."""

import re
import sys

from qgis.PyQt.QtCore import QVariant

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


"""
Minimum needs definition are taken from user.
Because of this, minimum needs field definition needs to be generated
dynamically to avoid namespace clash. It is also need to be able to link to
original-user-defined definition of minimum needs, so the definition of the
unit can be referenced.
"""

# namespace prefix for field key and field name
minimum_needs_namespace = 'minimum_needs'


def _normalize_field_name(value):
    """Normalizing value string used as key and field name.

    :param value: String to normalize
    :type value: str

    :return: normalized string
    :rtype: str
    """
    # Replace non word/letter character
    return_value = re.sub(r'[^\w\s-]+', '', value)
    # Replaces whitespace with underscores
    return_value = re.sub(r'\s+', '_', return_value)
    return return_value.lower()


def _initializes_minimum_needs_fields():
    """Initialize minimum needs fields.

    Minimum needs definitions are taken from currently used profile.
    """
    needs_profile = NeedsProfile()
    needs_profile.load()
    fields = []

    needs_parameters = needs_profile.get_needs_parameters()

    for need_parameter in needs_parameters:
        if isinstance(need_parameter, ResourceParameter):
            format_args = {
                'namespace': minimum_needs_namespace,
                'key': _normalize_field_name(need_parameter.name),
                'name': need_parameter.name,
                'field_name': _normalize_field_name(need_parameter.name),
            }

            key = u'{namespace}__{key}_count_field'.format(**format_args)
            name = u'{name}'.format(**format_args)
            field_name = u'{namespace}__{field_name}'.format(**format_args)
            field_type = QVariant.LongLong  # See issue #4039
            length = 11  # See issue #4039
            precision = 0
            absolute = True
            replace_null = False
            description = need_parameter.description

            field_definition = {
                'key': key,
                'name': name,
                'field_name': field_name,
                'type': field_type,
                'length': length,
                'precision': precision,
                'absolute': absolute,
                'description': description,
                'replace_null': replace_null,
                'unit_abbreviation': need_parameter.unit.abbreviation,
                # Link to need_parameter
                'need_parameter': need_parameter
            }
            fields.append(field_definition)
    return fields


def minimum_needs_field(field_key):
    """Get minimum needs field from a given key.

    :param field_key: Field key
    :type field_key: str

    :return: Field definition
    :rtype: dict
    """
    for field in minimum_needs_fields:
        if field_key == field['key']:
            return field
    return None


def minimum_needs_parameter(field=None, parameter_name=None):
    """Get minimum needs parameter from a given field.

    :param field: Field provided
    :type field: dict

    :param parameter_name: Need parameter's name
    :type parameter_name: str

    :return: Need paramter
    :rtype: ResourceParameter
    """
    try:
        if field['key']:
            for need_field in minimum_needs_fields:
                if need_field['key'] == field['key']:
                    return need_field['need_parameter']
    except (TypeError, KeyError):
        # in case field is None or field doesn't contain key.
        # just pass
        pass

    if parameter_name:
        for need_field in minimum_needs_fields:
            if need_field['need_parameter'].name == parameter_name:
                return need_field['need_parameter']
    return None


minimum_needs_fields = _initializes_minimum_needs_fields()

# assign all minimum needs fields to this module, so it can be recognized at
# runtime


def _declare_minimum_fields():
    """Declaring minimum needs so it can be recognized in module level import.

    Useful so it can be recognized by safe.definitions.utilities.definition
    """
    for field in minimum_needs_fields:
        setattr(sys.modules[__name__], field['key'], field)


_declare_minimum_fields()
