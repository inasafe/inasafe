# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Flood Vector on Building QGIS IF

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.utilities.i18n import tr

from safe_extras.parameters.string_parameter import StringParameter
from safe_extras.parameters.float_parameter import FloatParameter


def evacuation_percentage():
    """Generator for the default evaluation percentage parameter.
    :return: List of Float parameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = 'Evacuation Percentage'
    field.is_required = True
    field.maximum_allowed_value = 100
    field.minimum_allowed_value = 0
    field.value = 1
    field.precision = 2
    field.help_text = tr('Percentage value of affected population.')
    field.description = tr(
        'The value in percentage of the population that '
        'represent the number of people needed to be evacuated.')
    return field


def affected_field():
    """Generate affected field parameter

    :return: list of StringParameter
    :rtype: list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Affected Field'
    field.is_required = True
    field.value = 'FLOODPRONE'  # default value
    return field


def affected_value():
    """Generate affected value parameter

    :return: list of String Parameter
    :rtype: list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Affected Value'
    field.is_required = True
    field.value = 'YES'  # default value
    return field
