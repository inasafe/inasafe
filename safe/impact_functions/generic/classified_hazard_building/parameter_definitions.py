# coding=utf-8
from safe_extras.parameters.float_parameter import FloatParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def low_hazard_class():
    field = FloatParameter()
    field.name = 'Low Hazard Class'
    field.is_required = True
    field.precision = 1
    field.value = 1.0
    return field


def medium_hazard_class():
    field = FloatParameter()
    field.name = 'Medium Hazard Class'
    field.is_required = True
    field.precision = 1
    field.value = 2.0
    return field


def high_hazard_class():
    field = FloatParameter()
    field.name = 'High Hazard Class'
    field.is_required = True
    field.precision = 1
    field.value = 3.0
    return field
