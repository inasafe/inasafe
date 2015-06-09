# coding=utf-8
from safe.utilities.i18n import tr
from safe_extras.parameters.float_parameter import FloatParameter


def low_hazard_class():
    """Parameter definition.

    :returns: Low Hazard Class parameter
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.name = 'Low Hazard Class'
    field.element_type = float
    field.value = 1.0
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
    field.help_text = tr('Medium Hazard class value.')
    field.description = tr(
        'The value of hazard categorized as Medium Hazard class.')
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
    field.help_text = tr('High Hazard class value.')
    field.description = tr(
        'The value of hazard categorized as High Hazard class.')
    return field
