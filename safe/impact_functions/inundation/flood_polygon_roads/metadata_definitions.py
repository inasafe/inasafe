# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Flood Polygon
on Roads Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.defaults import road_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.definitions import (
    layer_mode_classified,
    layer_geometry_polygon,
    layer_geometry_line,
    hazard_flood,
    hazard_category_single_event,
    flood_vector_hazard_classes,
    exposure_road,
    layer_mode_none,
    road_type_field,
    affected_value,
    affected_field
)


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
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [hazard_category_single_event],
                    'hazard_types': [hazard_flood],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        flood_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': [affected_field, affected_value]
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
                # This field of the  hazard layer contains information
                # about inundated areas
                ('affected_field', 'affected'),
                # This value in 'affected_field' of the hazard layer
                # marks the areas as inundated
                ('affected_value', '1'),
                ('postprocessors', OrderedDict([
                    ('RoadType', road_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
