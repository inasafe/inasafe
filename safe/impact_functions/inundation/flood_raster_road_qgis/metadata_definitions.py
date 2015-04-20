# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Raster Impact on Roads

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'metadata_definitions.py'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

from safe.definitions import (
    hazard_definition,
    hazard_flood,
    hazard_tsunami,
    unit_metres_depth,
    unit_feet_depth,
    layer_raster_continuous,
    exposure_definition,
    exposure_road,
    unit_road_type_type,
    layer_vector_line)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.inundation.flood_raster_road_qgis\
    .parameter_definitions import \
    road_type_field, min_threshold, max_threshold
from safe.defaults import road_type_postprocessor
from safe.utilities.i18n import tr
from safe.common.utilities import OrderedDict


class FloodRasterRoadsExperimentalMetadata(ImpactFunctionMetadata):
    """Metadata for FloodRasterRoadsExperimentalFunction

    .. versionadded:: 2.1

    We only need to re-implement as_dict(), all other behaviours
    are inherited from the abstract base class.
    """

    @staticmethod
    def as_dict():
        """Return metadata as a dictionary.

        This is a static method. You can use it to get the metadata in
        dictionary format for an impact function.

        :returns: A dictionary representing all the metadata for the
            concrete impact function.
        :rtype: dict
        """
        dict_meta = {
            'id': 'FloodRasterRoadsExperimentalFunction',
            'name': tr('Flood Raster Roads Experimental Function'),
            'impact': tr('Be flooded in given thresholds'),
            'title': tr('Be flooded in given thresholds'),
            'function_type': 'qgis2.0',
            'author': 'Dmitry Kolesov',
            'date_implemented': 'N/A',
            'overview': tr('N/A'),
            'detailed_description': '',
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [
                        hazard_flood,
                        hazard_tsunami
                    ],
                    'units': [
                        unit_metres_depth,
                        unit_feet_depth
                    ],
                    'layer_constraints': [layer_raster_continuous]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_road],
                    'units': [unit_road_type_type],
                    'layer_constraints': [layer_vector_line]
                }
            },
            'parameters': OrderedDict([
                # This field of the exposure layer contains
                # information about road types
                ('road_type_field', road_type_field()),
                ('min threshold', min_threshold()),
                ('max threshold', max_threshold()),
                ('postprocessors', OrderedDict([
                    ('RoadType', road_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
