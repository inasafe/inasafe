# coding=utf-8
from safe.impact_functions.generic.utilities import increasing_validator
from safe.utilities.i18n import tr
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.group_parameter import GroupParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def categorical_thresholds():

    field = GroupParameter()
    field.must_scroll = False
    field.name = 'Categorical thresholds'
    field.is_required = True
    field.help_text = tr('Hazard classes thresholds.')
    field.description = tr(
        'Describe the upper thresholds of each hazard class. Each threshold '
        'should be greater value than previous one.')
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
    field.name = 'Low Hazard Threshold'
    field.element_type = float
    field.value = 0.34
    field.help_text = tr('Low Hazard class thresholds.')
    field.description = tr(
        'Threshold value of hazard categorized as Low Hazard class.')
    return field


def medium_hazard_class():
    """Parameter definition.

    :returns: Medium Hazard Class parameter
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.name = 'Medium Hazard Threshold'
    field.element_type = float
    field.value = 0.67
    field.help_text = tr('Medium Hazard class threshold.')
    field.description = tr(
        'Threshold value of hazard categorized as Medium Hazard class. It '
        'should be greater than Low Hazard Thresholds')
    return field


def high_hazard_class():
    """Parameter definition.

    :returns: High Hazard Class parameter
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.name = 'High Hazard Threshold'
    field.element_type = float
    field.value = 1.0
    field.help_text = tr('High Hazard class threshold.')
    field.description = tr(
        'Threshold value of hazard categorized as High Hazard class. It '
        'should be greater than Medium Hazard Thresholds')
    return field
