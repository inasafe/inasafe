# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Ash Raster Impact on People

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.impact_functions.unit_definitions import \
    parameter_unit_centimetres
from safe_extras.parameters.float_parameter import FloatParameter
from safe.utilities.i18n import tr
from safe_extras.parameters.group_parameter import GroupParameter

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'parameter_definitions.py'
__date__ = '7/13/16'
__copyright__ = 'imajimatika@gmail.com'


def unaffected_threshold():
    """Generate threshold for unaffected region

    :returns: A FloatParameter.
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('Unaffected Threshold')
    field.precision = 2
    field.value = 1
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    field.value = 0.01
    unit_centimetres = parameter_unit_centimetres()
    field.unit = unit_centimetres
    field.allowed_units = [unit_centimetres]
    field.help_text = tr('Unaffected threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Unaffected in '
        'centimetres. A zone is categorized as Unaffected if the '
        'thickness of ash is less than Unaffected Threshold.')
    return field


def very_low_threshold():
    """Generate very low hazard zone threshold parameter

    :returns: A FloatParameter.
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('Very Low Hazard Zone Threshold')
    field.precision = 2
    field.value = 1
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    field.value = 0.1
    unit_centimetres = parameter_unit_centimetres()
    field.unit = unit_centimetres
    field.allowed_units = [unit_centimetres]
    field.help_text = tr('Very Low Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Very Low Hazard Zone in '
        'centimetres. A zone is categorized as Very Low Hazard Zone if the '
        'thickness of ash is more than Unaffected threshold and less than '
        'Very Low Hazard Zone Threshold.')
    return field


def low_threshold():
    """Generate low hazard zone threshold parameter

    :returns: A FloatParameter.
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('Low Hazard Zone Threshold')
    field.precision = 2
    field.value = 2
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    unit_centimetres = parameter_unit_centimetres()
    field.unit = unit_centimetres
    field.allowed_units = [unit_centimetres]
    field.help_text = tr('Low Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Low Hazard Zone in '
        'centimetres. A zone is categorized as Low Hazard Zone if the '
        'thickness of ash is more than Very Low Hazard Zone Threshold and '
        'less than Low Hazard Zone Threshold.')
    return field


def moderate_threshold():
    """Generate moderate hazard zone threshold parameter

    :returns: A FloatParameter.
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('Moderate Hazard Zone Threshold')
    field.precision = 2
    field.value = 5
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    unit_centimetres = parameter_unit_centimetres()
    field.unit = unit_centimetres
    field.allowed_units = [unit_centimetres]
    field.help_text = tr('Moderate Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Moderate Hazard Zone in '
        'centimetres. A zone is categorized as Medium Hazard Zone if the '
        'thickness of ash is more than Low Hazard Zone Threshold and less '
        'than Moderate Hazard Zone Threshold.')
    return field


def high_threshold():
    """Generate high  hazard zone threshold parameter

    :returns: A FloatParameter.
    :rtype: FloatParameter
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('High Hazard Zone Threshold')
    field.precision = 2
    field.value = 10
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    unit_centimetres = parameter_unit_centimetres()
    field.unit = unit_centimetres
    field.allowed_units = [unit_centimetres]
    field.help_text = tr('High Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as High Hazard Zone in '
        'centimetres. A zone is categorized as High Hazard Zone if the '
        'thickness of ash is more than Moderate Hazard Zone Threshold and '
        'less than High Hazard Zone Threshold. If it is more than High Hazard '
        'Threshold then it was considered as Very High Hazard Zone')
    return field


def threshold_group_parameter():
    """Generate group parameter of threshold to define constraints.

    :return: a group parameter
    :rtype: GroupParameter
    """
    field = GroupParameter()
    field.name = 'Hazard Threshold'
    field.is_required = True
    field.help_text = tr('Define thresholds for Ash hazard zones.')
    field.description = tr('Define thresholds for Ash hazard zones.')
    unaffected = unaffected_threshold()
    very_low = very_low_threshold()
    low = low_threshold()
    moderate = moderate_threshold()
    high = high_threshold()
    field.value_map = {
        'unaffected_threshold': unaffected,
        'very_low_threshold': very_low,
        'low_threshold': low,
        'moderate_threshold': moderate,
        'high_threshold': high
    }
    field.value = [
        unaffected,
        very_low,
        low,
        moderate,
        high
    ]

    def threshold_validator(param):
        """Inspect the value of the parameter

        :param param: FloatParameter in validation
        :type param: FloatParameter

        :returns: True if valid
        :rtype: bool
        """
        valid = True
        message = None

        if ((param == unaffected and param.value >= very_low.value) or
                (param == very_low and param.value < unaffected.value)):
            message = tr(
                'Unaffected threshold must less than Very Low threshold')
            valid = False
        if ((param == very_low and param.value >= low.value) or
                (param == low and param.value < very_low.value)):
            message = tr(
                'Very Low threshold must less than Low threshold')
            valid = False
        if ((param == low and param.value >= moderate.value) or
                (param == moderate and param.value < low.value)):
            message = tr(
                'Low threshold must less than Moderate threshold')
            valid = False
        if ((param == moderate and param.value >= high.value) or
                (param == high and param.value < moderate.value)):
            message = tr(
                'Moderate threshold must less than High threshold')
            valid = False

        if not valid:
            raise ValueError(message)
        return valid

    field.custom_validator = threshold_validator
    return field
