# coding=utf-8

__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.string_parameter import StringParameter

def threshold():
    """Generator for the default threshold parameter.

    :return: List of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = 'Thresholds [m]'
    field.is_required = True
    field.precision = 2
    field.value = 1.0  # default value
    return field


def hazard_level_name():
    """Generator for the default threshold parameter.

    :return: List of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = StringParameter()
    field.name = 'Hazard Level Name'
    field.is_required = True
    field.value = 'depth'
    return field