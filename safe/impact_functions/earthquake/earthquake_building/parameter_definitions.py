# coding=utf-8
from safe.impact_functions.unit_definitions import parameter_unit_mmi
from safe.utilities.i18n import tr
from safe_extras.parameters.integer_parameter import IntegerParameter

__author__ = 'lucernae'
__date__ = '11/04/15'


def low_threshold():
    """Generate low threshold parameter

    :return: list of IntegerParameter
    :rtype: list[IntegerParameter]
    """
    field = IntegerParameter()
    field.is_required = True
    field.name = 'Low Threshold'
    field.value = 6
    field.minimum_allowed_value = 1
    field.maximum_allowed_value = 10
    unit_mmi = parameter_unit_mmi()
    field.unit = unit_mmi
    field.allowed_units = [unit_mmi]
    field.help_text = tr('Low Hazard class threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Low Hazard class in MMI '
        'scale.')
    return field


def medium_threshold():
    """Generate medium threshold parameter

    :return: list of IntegerParameter
    :rtype: list[IntegerParameter]
    """
    field = IntegerParameter()
    field.is_required = True
    field.name = 'Medium Threshold'
    field.value = 7
    field.minimum_allowed_value = 1
    field.maximum_allowed_value = 10
    unit_mmi = parameter_unit_mmi()
    field.unit = unit_mmi
    field.allowed_units = [unit_mmi]
    field.help_text = tr('Medium Hazard class threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Medium Hazard class in MMI '
        'scale.')
    return field


def high_threshold():
    """Generate high threshold parameter

    :return: list of IntegerParameter
    :rtype: list[IntegerParameter]
    """
    field = IntegerParameter()
    field.is_required = True
    field.name = 'High Threshold'
    field.value = 8
    field.minimum_allowed_value = 1
    field.maximum_allowed_value = 10
    unit_mmi = parameter_unit_mmi()
    field.unit = unit_mmi
    field.allowed_units = [unit_mmi]
    field.help_text = tr('High Hazard class threshold.')
    field.description = tr(
        'The threshold of hazard categorized as High Hazard class in MMI '
        'scale.')
    return field
