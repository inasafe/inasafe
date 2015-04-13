# coding=utf-8
__author__ = 'lucernae'
__date__ = '11/04/15'

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
    field.value = '1'
    return field
