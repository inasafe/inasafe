# coding=utf-8
from safe.utilities.i18n import tr
from safe_extras.parameters.unit import Unit

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '11/06/15'


def parameter_unit_generic():
    unit = Unit()
    unit.name = tr('generic')
    unit.plural = tr('generics')
    unit.abbreviation = tr('generic')
    unit.description = tr(
        'Impact function with generic unit means it can accept the value '
        'regardless of any unit the data represents')
    return unit


def parameter_unit_metres():
    unit = Unit()
    unit.name = tr('meter')
    unit.plural = tr('metres')
    unit.abbreviation = tr('m')
    unit.description = tr('Length in meter.')
    return unit


def parameter_unit_mmi():
    unit = Unit()
    unit.name = tr('MMI')
    unit.plural = tr('MMI')
    unit.abbreviation = tr('MMI')
    unit.description = tr(
        'MMI stands for Modified Mercalli Intensity Scale, to measure the '
        'intensity of earthquake.')
    return unit


def parameter_unit_percentage():
    unit = Unit()
    unit.name = tr('percentage')
    unit.plural = tr('percentages')
    unit.abbreviation = tr('%%')
    unit.description = tr(
        'Percentage values ranges from 0 to 100. It represents a ratio of '
        'hundred.')
    return unit
