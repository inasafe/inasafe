# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Flood Vector on Building QGIS IF

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe_extras.parameters.string_parameter import StringParameter


def affected_field():
    """"Generator for selection of affected field parameter."""
    field = StringParameter()
    field.name = 'Affected Field'
    field.is_required = True
    field.value = 'affected'  # default value
    return field


def affected_value():
    """Generator for parameter stating what values constitute 'affected'."""
    field = StringParameter()
    field.name = 'Affected Value'
    field.is_required = True
    field.value = '1'  # default value
    return field


def road_type_field():
    """Generate road type field parameter

    :return: StringParameter
    :rtype: StringParameter
    """
    field = StringParameter()
    field.name = 'Road Type Field'
    field.is_required = True
    field.value = 'TYPE'
    return field
