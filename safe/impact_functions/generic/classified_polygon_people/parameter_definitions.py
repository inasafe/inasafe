# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Flood Vector on Building QGIS IF

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Samweli Twesa Mwakisambwe "Samweli" <smwltwesa6@gmail.com>'
__date__ = '8/5/15'


from safe_extras.parameters.string_parameter import StringParameter


def area_id():
    """Generate area population parameter

    :return: list of String Parameter
    :rtype list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Area Id'
    field.is_required = True
    field.value = 'id'
    return field


def area_population():
    """Generate area population parameter

    :return: list of String Parameter
    :rtype list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Population'
    field.is_required = True
    field.value = 'population'
    return field


def area_type_field():
    """Generate land cover type field parameter

    :return: list of StringParameter
    :rtype: list[StringParameter]
    """
    field = StringParameter()
    field.name = 'Area Type Field'
    field.is_required = True
    field.value = 'type'
    return field




