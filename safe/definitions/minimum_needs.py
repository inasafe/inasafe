# coding=utf-8

"""Definitions relating to minimum-needs."""
import re
import sys

from safe.common.minimum_needs import MinimumNeeds
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitions.constants import qvariant_whole_numbers
from safe.definitions.fields import default_field_length
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe_extras.parameters.unit import Unit

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
    # We need to add some parameters for:
    # - weekly hygiene packs for woman
    # - additional rice for pregnant and lactating women
    # TODO: find out how it will nicely fits in the architecture
    weekly_hygiene_packs = ResourceParameter()
    weekly_hygiene_packs.name = MinimumNeeds.Weekly_hygiene_packs
    weekly_hygiene_packs.minimum_allowed_value = 0.00
    weekly_hygiene_packs.maximum_allowed_value = 100.00
    weekly_hygiene_packs.frequency = 'weekly'
    # The formula:
    # displaced_female * 0.7937 * (week/intended_day_use)
    weekly_hygiene_packs.value = 0.7937

    additional_rice_for_woman = ResourceParameter()
    additional_rice_for_woman.name = MinimumNeeds.Additional_rice
    rice_unit = Unit()
    rice_unit.abbreviation = 'kg'
    additional_rice_for_woman.unit = rice_unit
    additional_rice_for_woman.frequency = 'weekly'
    # The formula:
    # displaced_female * 2 * (0.033782 + 0.01281)
    additional_rice_for_woman.value = 2 * (0.033782 + 0.01281)

    needs_parameters += [weekly_hygiene_packs, additional_rice_for_woman]

    for need_parameter in needs_parameters:
        if isinstance(need_parameter, ResourceParameter):
            format_args = {
                'namespace': minimum_needs_namespace,
                'key': _normalize_field_name(need_parameter.name),
                'name': need_parameter.name,
                'field_name': _normalize_field_name(need_parameter.name),
            }

            key = '{namespace}__{key}_count_field'.format(**format_args)
            name = '{name}'.format(**format_args)
            field_name = '{namespace}__{field_name}'.format(
                **format_args)
            field_type = qvariant_whole_numbers
            length = default_field_length
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

# Specific grouping for female minimum needs
female_minimum_needs_fields = [
    _field for _field in minimum_needs_fields if
    (
        _field['need_parameter'].name == MinimumNeeds.Weekly_hygiene_packs or
        _field['need_parameter'].name == MinimumNeeds.Additional_rice
    )]
