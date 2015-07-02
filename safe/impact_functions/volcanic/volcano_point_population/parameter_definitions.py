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
from safe_extras.parameters.input_list_parameter import InputListParameter


def distance():
    field = InputListParameter()
    field.name = 'Distances [km]'
    field.is_required = True
    field.minimum_item_count = 1
    # Rizky: no reason for the number below. It can be any values to describe
    # maximum item count. Feel free to change it when necessary.
    # PS: it was my birthdate
    field.maximum_item_count = 19
    field.element_type = float
    field.ordering = InputListParameter.AscendingOrder
    field.value = [3.0, 5.0, 10.0]
    field.help_text = tr('The list of radii for volcano buffer.')
    field.description = tr(
        'This list contains radii of volcano buffer in increasing order.')
    return field
