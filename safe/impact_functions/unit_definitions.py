# coding=utf-8
from safe.definitionsv4.definitions_v3 import (
    unit_generic,
    unit_metres,
    unit_mmi,
    unit_percentage,
    unit_centimetres
)
from safe_extras.parameters.unit import Unit

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '11/06/15'


def convert_to_parameter_unit(unit_definition):
    unit = Unit()
    unit.name = unit_definition.get('name')
    unit.plural = unit_definition.get('plural_name')
    unit.abbreviation = unit_definition.get('abbreviation')
    unit.description = unit_definition.get('description')
    return unit


def parameter_unit_generic():
    return convert_to_parameter_unit(unit_generic)


def parameter_unit_metres():
    return convert_to_parameter_unit(unit_metres)


def parameter_unit_mmi():
    return convert_to_parameter_unit(unit_mmi)


def parameter_unit_percentage():
    return convert_to_parameter_unit(unit_percentage)


def parameter_unit_centimetres():
    return convert_to_parameter_unit(unit_centimetres)
