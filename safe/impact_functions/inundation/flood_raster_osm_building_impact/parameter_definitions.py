# coding=utf-8

__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.float_parameter import FloatParameter


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
