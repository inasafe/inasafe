# coding=utf-8
from safe_extras.parameters.integer_parameter import IntegerParameter

__author__ = 'lucernae'
__date__ = '11/04/15'


def low_threshold():
    """Generate low threshold parameter

    :return: list of IntegerParameter
    :rtype: list[IntegerParameter]
    """
    field = IntegerParameter()
    field.is_required = True
    field.name = 'Low Threshold'
    field.value = 6
    return field


def medium_threshold():
    """Generate medium threshold parameter

    :return: list of IntegerParameter
    :rtype: list[IntegerParameter]
    """
    field = IntegerParameter()
    field.is_required = True
    field.name = 'Medium Threshold'
    field.value = 7
    return field


def high_threshold():
    """Generate high threshold parameter

    :return: list of IntegerParameter
    :rtype: list[IntegerParameter]
    """
    field = IntegerParameter()
    field.is_required = True
    field.name = 'High Threshold'
    field.value = 8
    return field
