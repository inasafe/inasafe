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

from safe_extras.parameters.input_list_parameter import InputListParameter


def threshold():
    """Generator for the default threshold parameter.

    :return: List of InputListParameter
    :rtype: list[InputListParameter]
    """
    field = InputListParameter()
    field.name = 'Thresholds [m]'
    field.is_required = True
    field.element_type = float
    field.expected_type = list
    field.ordering = InputListParameter.AscendingOrder
    field.minimum_item_count = 1
    field.maximum_item_count = 3
    field.value = [1.0]  # default value
    field.help_text = tr(
        'Thresholds value to categorize inundated area.')
    field.description = tr(
        'Up to 3 thresholds in meter can be set in an increasing order.')
    return field
