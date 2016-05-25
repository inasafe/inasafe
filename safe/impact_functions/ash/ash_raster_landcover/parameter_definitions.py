# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Tsunami Raster Impact on OSM Buildings

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


__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/24/16'


def unaffected_threshold():
    """Generate threshold for unaffected region

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
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

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
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

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
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

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
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

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
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
