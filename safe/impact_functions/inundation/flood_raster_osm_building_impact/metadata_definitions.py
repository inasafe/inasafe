# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Raster Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.common.utilities import OrderedDict
from safe.defaults import building_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.inundation.flood_raster_osm_building_impact\
    .parameter_definitions import threshold
from safe.utilities.i18n import tr
from safe.definitions import (
    layer_mode_classified,
    layer_mode_continuous,
    layer_geometry_polygon,
    layer_geometry_point,
    layer_geometry_raster,
    hazard_flood,
    hazard_category_single_event,
    hazard_category_multiple_event,
    exposure_structure,
    unit_metres,
    unit_feet,
    structure_class_field
)

__author__ = "lucernae"


class FloodRasterBuildingMetadata(ImpactFunctionMetadata):
    """Metadata for Flood Raster Building Impact Function.

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
        title = tr('Buildings affected by flood')
        dict_meta = {
            'id': 'FloodRasterBuildingFunction',
            'name': tr('Raster flood on buildings'),
            'impact': tr('Be flooded'),
            'title': tr('Be flooded'),
            'function_type': 'old-style',
            # should be a list, but we can do it later.
            'author': 'Ole Nielsen and Kristy van Putten',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of (flood or tsunami) inundation '
                'on building footprints originating from OpenStreetMap '
                '(OSM) with hazard in raster format.'),
            'detailed_description': tr(
                'The inundation status is calculated for each building '
                '(using the centroid if it is a polygon) based on the '
                'flood threshold. The threshold can be configured in '
                'impact function options.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents flood '
                'depth (in meters).'),
            'exposure_input': tr(
                'Vector polygon or point layer extracted from OSM where '
                'each feature represents the footprint of a building.'),
            'output': tr(
                'Vector layer contains building is estimated to be '
                'flooded and the breakdown of the building by type.'),
            'actions': tr(
                'Provide details about where critical infrastructure '
                'might be flooded.'),
            'limitations': [
                tr('This function only flags buildings as impacted or not '
                   'either based on a fixed threshold')
            ],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_notes': '',
            'map_title': title,
            'layer_name': title,
            'legend_title': tr('Flooded structure status'),
            'legend_units': tr('(flooded, wet, or dry)'),
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': [hazard_flood],
                    'continuous_hazard_units': [unit_feet, unit_metres],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [
                        layer_geometry_point,
                        layer_geometry_polygon
                    ],
                    'exposure_types': [exposure_structure],
                    'exposure_units': [],
                    'exposure_class_fields': [structure_class_field],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([
                ('threshold', threshold()),
                ('postprocessors', OrderedDict([
                    ('BuildingType', building_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
