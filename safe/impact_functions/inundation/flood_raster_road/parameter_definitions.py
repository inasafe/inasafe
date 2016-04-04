# coding=utf-8
from safe.impact_functions.unit_definitions import parameter_unit_metres

__author__ = 'lucernae'
__date__ = '11/04/15'

import sys

from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.string_parameter import StringParameter
from safe.utilities.i18n import tr


def road_type_field():
    """Generate road type field parameter

    :return: list of StringParameter
    :rtype: list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Road Type Field'
    field.is_required = True
    field.value = 'TYPE'
    return field


def min_threshold():
    """Generator for the default threshold parameter.

    :return: List of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = 'Minimum Thresholds [m]'
    field.is_required = True
    field.precision = 2
    field.value = 1.0  # default value
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr(
        'Minimum value of hazard considered as inundated.')
    field.description = tr(
        'The depth of flood in meter as threshold.')
    return field


def max_threshold():
    """Generator for the default threshold parameter.

    :return: List of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = 'Maximum Thresholds [m]'
    field.is_required = True
    field.precision = 2
    field.value = sys.float_info.max  # default value
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr(
        'Maximum value of hazard considered as inundated.')
    field.description = tr(
        'The depth of flood in meter as threshold.')
    return field
