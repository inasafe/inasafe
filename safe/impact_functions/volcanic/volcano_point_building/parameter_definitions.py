# coding=utf-8
from safe_extras.parameters.input_list_parameter import InputListParameter
from safe_extras.parameters.string_parameter import StringParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def distance():
    field = InputListParameter()
    field.name = 'Distances [km]'
    field.is_required = True
    field.minimum_item_count = 1
    field.maximum_item_count = 100
    field.element_type = float
    field.value = [3.0, 5.0, 10.0]
    return field


def volcano_name_attribute():
    field = StringParameter()
    field.name = 'Volcano Name Attribute'
    field.is_required = True
    field.value = 'NAME'
    return field
