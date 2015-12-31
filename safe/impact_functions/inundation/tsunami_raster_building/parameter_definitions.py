# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Parameter definition for
Tsunami Raster Impact on OSM Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe'
__filename__ = 'parameter_definitions'
__date__ = '12/31/15'
__copyright__ = 'imajimatika@gmail.com'

from safe.impact_functions.unit_definitions import parameter_unit_metres
from safe_extras.parameters.float_parameter import FloatParameter
from safe.utilities.i18n import tr


def threshold():
    """Generator for the default threshold parameter.

    :return: List of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.name = tr('Thresholds [m]')
    field.is_required = True
    field.precision = 2
    field.value = 1.0  # default value
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr(
        'Threshold value to categorize inundated area.')
    field.description = tr(
        'Hazard value above the threshold in meter will be considered '
        'inundated.')
    return field