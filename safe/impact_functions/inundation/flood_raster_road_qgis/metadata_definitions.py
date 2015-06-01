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

from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.defaults import road_type_postprocessor
from safe.utilities.i18n import tr
from safe.common.utilities import OrderedDict
from safe.definitions import (
    layer_mode_none,
    layer_mode_continuous,
    layer_geometry_raster,
    layer_geometry_line,
    hazard_flood,
    hazard_category_single_event,
    exposure_road,
    unit_metres,
    unit_feet,
    hazard_tsunami,
    road_type_field
)


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
            'id': 'FloodRasterRoadsQGISFunction',
            'name': tr('Raster flood on roads (QGIS)'),
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
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [hazard_category_single_event],
                    'hazard_types': [hazard_flood, hazard_tsunami],
                    'continuous_hazard_units': [unit_feet, unit_metres],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_none,
                    'layer_geometries': [layer_geometry_line],
                    'exposure_types': [exposure_road],
                    'exposure_units': [],
                    'additional_keywords': [road_type_field]
                }
            },
            'parameters': OrderedDict([
                # This field of the exposure layer contains
                # information about road types
                ('road_type_field', 'TYPE'),
                ('min threshold [m]', 1.0),
                ('max threshold [m]', float('inf')),
                ('postprocessors', OrderedDict([
                    ('RoadType', road_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
