# coding=utf-8
from safe_extras.parameters.string_parameter import StringParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def hazard_zone_attribute():
    field = StringParameter()
    field.name = 'Hazard Zone Attribute'
    field.is_required = True
    field.value = 'KRB'
    return field


def volcano_name_attribute():
    field = StringParameter()
    field.name = 'Volcano Name Attribute'
    field.is_required = True
    field.value = 'NAME'
    return field
