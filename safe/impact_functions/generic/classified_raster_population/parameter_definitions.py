# coding=utf-8
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
    return field