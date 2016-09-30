# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Flood Polygon
on Roads Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.fields import road_class_field
from safe.definitionsv4.exposure import exposure_road
from safe.definitionsv4.hazard import hazard_category_multiple_event, \
    hazard_flood
from safe.definitionsv4 import flood_vector_hazard_classes
from safe.definitionsv4.hazard_category import hazard_category_single_event, \
    hazard_category_multiple_event
from safe.definitionsv4.layer_geometry import layer_geometry_line, \
    layer_geometry_polygon
from safe.common.utilities import OrderedDict
from safe.defaults import road_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class FloodPolygonRoadsMetadata(ImpactFunctionMetadata):
    """Metadata for FloodVectorRoadsExperimentalFunction.

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
            'id': 'FloodVectorRoadsExperimentalFunction',
            'name': tr('Polygon flood on roads'),
            'impact': tr('Be flooded'),
            'title': tr('Be flooded'),
            'function_type': 'qgis2.0',
            'author': 'Dmitry Kolesov',
            'date_implemented': 'N/A',
            'overview': tr('N/A'),
            'detailed_description': tr('N/A'),
            'hazard_input': tr(''),
            'exposure_input': tr(''),
            'output': tr(''),
            'actions': tr(''),
            'limitations': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_units': '',
            'legend_notes': '',
            'legend_title': tr('Road inundated status'),
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': [hazard_flood],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        flood_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_line],
                    'exposure_types': [exposure_road],
                    'exposure_units': [],
                    'exposure_class_fields': [road_class_field],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([
                ('postprocessors', OrderedDict([
                    ('RoadType', road_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
