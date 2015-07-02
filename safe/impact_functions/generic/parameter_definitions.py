# coding=utf-8
from safe.impact_functions.generic.utilities import increasing_validator
from safe.impact_functions.unit_definitions import parameter_unit_generic
from safe.utilities.i18n import tr
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.group_parameter import GroupParameter
from safe_extras.parameters.string_parameter import StringParameter

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '11/06/15'


def categorical_hazards():

    field = GroupParameter()
    field.must_scroll = False
    field.name = 'Categorical hazards'
    field.is_required = True
    field.help_text = tr('Hazard classes values.')
    field.description = tr(
        'Describe the value of each hazard class. Each value should be '
        'greater value than previous one.')
    field.value = [
        low_hazard_class(),
        medium_hazard_class(),
        high_hazard_class()
    ]

    field.custom_validator = increasing_validator
    return field


def low_hazard_class():
    """Parameter definition.

    :returns: Low Hazard Class parameter
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.name = 'Low Hazard Class'
    field.element_type = float
    field.value = 1.0
    unit_generic = parameter_unit_generic()
    field.unit = unit_generic
    field.allowed_units = [unit_generic]
    field.help_text = tr('Low Hazard class value.')
    field.description = tr(
        'The value of hazard categorized as Low Hazard class.')
    return field


def medium_hazard_class():
    """Parameter definition.

    :returns: Medium Hazard Class parameter
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.name = 'Medium Hazard Class'
    field.element_type = float
    field.value = 2.0
    unit_generic = parameter_unit_generic()
    field.unit = unit_generic
    field.allowed_units = [unit_generic]
    field.help_text = tr('Medium Hazard class value.')
    field.description = tr(
        'The value of hazard categorized as Medium Hazard class')
    return field


def high_hazard_class():
    """Parameter definition.

    :returns: High Hazard Class parameter
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.name = 'High Hazard Class'
    field.element_type = float
    field.value = 3.0
    unit_generic = parameter_unit_generic()
    field.unit = unit_generic
    field.allowed_units = [unit_generic]
    field.help_text = tr('High Hazard class value.')
    field.description = tr(
        'The value of hazard categorized as High Hazard class')
    return field
