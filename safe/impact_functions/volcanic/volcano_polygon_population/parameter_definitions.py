# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Volcano Polygon on Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe_extras.parameters.string_parameter import StringParameter


def hazard_zone_attribute():
    field = StringParameter()
    field.name = 'Hazard Zone Attribute'
    field.is_required = True
    field.value = 'KRB'
    return field


def volcano_name_attribute():
    field = StringParameter()
    field.name = 'Volcano Name Attribute'
    field.is_required = True
    field.value = 'NAME'
    return field
