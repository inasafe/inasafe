# coding=utf-8
import numpy
from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.dict_parameter import DictParameter
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.input_list_parameter import InputListParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def theta():
    field = FloatParameter()
    field.name = 'Theta'
    field.is_required = True
    field.precision = 3
    field.value = 11.067
    return field


def beta():
    field = FloatParameter()
    field.name = 'Beta'
    field.is_required = True
    field.precision = 3
    field.value = 0.106
    return field


def displacement_rate():
    field = DictParameter()
    field.is_required = True
    field.name = 'Displacement Rate'
    field.minimum_item_count = 0
    field.maximum_item_count = 20
    field.element_type = float
    field.value = {
        1: 0.0,
        1.5: 0.0,
        2: 0.0,
        2.5: 0.0,
        3: 0.0,
        3.5: 0.0,
        4: 0.0,
        4.5: 0.0,
        5: 0.0,
        5.5: 0.0,
        6: 1.0,
        6.5: 1.0,
        7: 1.0,
        7.5: 1.0,
        8: 1.0,
        8.5: 1.0,
        9: 1.0,
        9.5: 1.0,
        10: 1.0}
    return field


def mmi_range():
    field = InputListParameter()
    field.name = 'MMI Range'
    field.is_required = True
    field.minimum_item_count = 1
    field.maximum_item_count = 100
    field.element_type = float
    field.value = numpy.arange(2, 10, 0.5).tolist()
    return field


def step():
    field = FloatParameter()
    field.name = 'Step'
    field.is_required = True
    field.precision = 2
    field.value = 0.25
    return field


def tolerance():
    field = FloatParameter()
    field.name = 'Tolerance'
    field.is_required = True
    field.precision = 2
    field.value = 0.01
    return field


def calculate_displaced_people():
    field = BooleanParameter()
    field.name = 'Calculate Displaced People'
    field.is_required = True
    field.value = True
    return field
