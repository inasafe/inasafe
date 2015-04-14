# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Flood Vector on Building QGIS IF

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.string_parameter import StringParameter
from safe_extras.parameters.list_parameter import ListParameter
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.dict_parameter import DictParameter


def x_coefficient():
    """Generator for the x coefficient field parameter."""
    field = FloatParameter()
    field.name = 'x'
    field.value = 0.62275231  # default value
    return field


def y_coefficient():
    """Generator for the y coefficient field parameter."""
    field = FloatParameter()
    field.name = 'y'
    field.value = 8.03314466  # default value
    return field


def displacement_rate():
    """Generator for the displacement rate field parameter."""
    field = DictParameter()
    field.name = 'displacement_rate'
    field.expected_type = dict
    field.value = {}
    field.value.update(
        {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1.0,
         7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0})
    return field


def mmi_range():
    """Generator for the MMI range field"""
    field = ListParameter()
    field.name = 'mmi_range'
    field.expected_type = list
    field.value = []
    field.value.extend([2, 3, 4, 5, 6, 7, 8, 9])
    return field


def step():
    """Generator for the step field"""
    field = FloatParameter()
    field.name = 'step'
    field.value = 0.5
    return field


def tolerance():
    """Generator for the tolerance field"""
    field = FloatParameter()
    field.name = 'tolerance'
    field.value = 0.01
    return field


def displaced_people():
    """Generator for the displaced people field"""
    field = BooleanParameter()
    field.name = 'calculate_displaced_people'
    field.value = True
    return field


def default_provenance():
    """The provenance for the default values.

    :return: default provenance.
    :rtype: StringParameter
    """
    prov_string = StringParameter()
    prov_string.name = 'provenance'
    prov_string.value = 'The minimum needs are based on Perka 7/2008.'
    return prov_string
