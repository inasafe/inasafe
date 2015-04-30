# coding=utf-8
from safe_extras.parameters.input_list_parameter import InputListParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def distance():
    """"Generator for distance field"""
    field = InputListParameter()
    field.name = 'Distances [km]'
    field.is_required = True
    field.minimum_item_count = 1
    field.maximum_item_count = 100
    field.element_type = float
    field.value = [3.0, 5.0, 10.0]
    return field
