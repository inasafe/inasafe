# coding=utf-8
__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.string_parameter import StringParameter

def target_field_value():
    """Generate target field value parameter with default field value

    :return: StringParameter
    :rtype: StringParameter
    """
    field = StringParameter()
    field.name = 'Target Field Value'
    field.is_required = True
    field.value = 'FLOODED'
    return field


def road_type_field():
    """Generate road type field parameter

    :return: StringParameter
    :rtype: StringParameter
    """
    field = StringParameter()
    field.name = 'Road Type Field'
    field.is_required = True
    field.value = 'TYPE'
    return field


def affected_field():
    """Generate affected field parameter

    :return: StringParameter
    :rtype: StringParameter
    """
    field = StringParameter()
    field.name = 'Affected Field'
    field.is_required = True
    field.help_text = (
        'This field of the  hazard layer contains information about inundated '
        'areas')
    field.description = (
        'This field of the  hazard layer contains information about inundated '
        'areas. This is the longer description of this parameter.')
    field.value = 'affected'
    return field


def affected_value():
    """Generate affected value parameter

    :return: String Parameter
    :rtype: StringParameter
    """
    field = StringParameter()
    field.name = 'Affected Value'
    field.is_required = True
    field.value = '1'
    return field
