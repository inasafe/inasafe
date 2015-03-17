# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Flood Raster Impact on OSM Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.string_parameter import StringParameter


def target_field():
    """Generator for the flooded target field parameter."""
    field = StringParameter()
    field.name = 'Target Field'
    field.is_required = True
    field.help_text = (
        'This field of impact layer marks inundated roads by \'1\' value')
    field.description = (
        'This field of impact layer marks inundated roads by \'1\' value. '
        'This is the longer description of this parameter.')
    field.value = 'INUNDATED'  # default value
    return field


def affected_field():
    """"Generator for selection of affected field parameter."""
    field = StringParameter()
    field.name = 'Affected Field'
    field.is_required = True
    field.help_text = (
        'This field of the  hazard layer contains information about inundated '
        'areas')
    field.description = (
        'This field of the  hazard layer contains information about inundated '
        'areas. This is the longer description of this parameter.')
    field.value = 'affected'  # default value
    return field


def affected_value():
    """Generator for parameter stating what values constitute 'affected'."""
    field = StringParameter()
    field.name = 'Affected Value'
    field.is_required = True
    field.help_text = (
        'This value in \'affected_field\' of the hazard layer marks the areas '
        'as inundated')
    field.description = (
        'This value in \'affected_field\' of the hazard layer marks the areas '
        'as inundated. This is the longer description of this parameter.')
    field.value = '1'  # default value
    return field


def building_type_field():
    field = BooleanParameter()
    field.name = 'Building Type Field'
    field.is_required = True
    field.value = True
    return field
