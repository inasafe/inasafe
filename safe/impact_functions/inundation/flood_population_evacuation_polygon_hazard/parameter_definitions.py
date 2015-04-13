# coding=utf-8
__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.float_parameter import FloatParameter


def evaluation_percentage():
    """Generator for the default evaluation percentage parameter.
    :return: List of Float parameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = 'Evacuation Percentage'
    field.is_required = True
    field.maximum_allowed_value = 100
    field.minimum_allowed_value = 0
    field.value = 1
    field.precision = 2
    return field
