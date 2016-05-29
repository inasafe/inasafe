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

# This file should be used in each tsunami IF.


def low_threshold():
    """Generate low hazard zone threshold parameter

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('Low Hazard Zone Threshold')
    field.precision = 2
    field.value = 1
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr('Low Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Low Hazard Zone in meter. A '
        'zone is categorized as Low Hazard Zone if the depth of tsunami '
        'inundation is less than Low Hazard Zone Threshold.')
    return field


def medium_threshold():
    """Generate moderate hazard zone threshold parameter

    :return: list of FloatParameter
    :rtype: list[FloatParameter]
    """
    field = FloatParameter()
    field.is_required = True
    field.name = tr('Moderate Hazard Zone Threshold')
    field.precision = 2
    field.value = 3
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr('Moderate Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as Moderate Hazard Zone in '
        'meter. A zone is categorized as Medium Hazard Zone if the depth of '
        'tsunami inundation is more than Low Hazard Zone Threshold and less '
        'than Medium Hazard Zone Threshold.')
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
    field.value = 8
    field.minimum_allowed_value = 0
    field.maximum_allowed_value = 100
    unit_metres = parameter_unit_metres()
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.help_text = tr('High Hazard Zone threshold.')
    field.description = tr(
        'The threshold of hazard categorized as High Hazard Zone in '
        'meter. A zone is categorized as High Hazard Zone if the depth of '
        'tsunami inundation is more than Medium Hazard Zone Threshold and '
        'less than High Hazard Zone Threshold. '
        'A zone that has more than High Hazard Zone Threshold is categorized '
        'as Very High Hazard Zone.')
    return field
