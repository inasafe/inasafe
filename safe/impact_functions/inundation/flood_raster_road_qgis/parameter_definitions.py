# coding=utf-8

__author__ = 'lucernae'
__date__ = '11/04/15'


import sys
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.string_parameter import StringParameter


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
    return field
