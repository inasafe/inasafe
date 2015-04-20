# coding=utf-8
__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.string_parameter import StringParameter


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


def affected_field():
    """Generate affected field parameter

    :return: list of StringParameter
    :rtype: list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Affected Field'
    field.is_required = True
    field.value = 'affected'
    return field


def affected_value():
    """Generate affected value parameter

    :return: list of String Parameter
    :rtype: list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Affected Value'
    field.is_required = True
    field.value = 'FLOODPRONE'
    return field
