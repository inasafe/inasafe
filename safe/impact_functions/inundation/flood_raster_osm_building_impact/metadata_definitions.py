# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Raster Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "lucernae"

from safe.common.utilities import OrderedDict
from safe.definitions import (
    hazard_definition,
    hazard_flood,
    hazard_tsunami,
    layer_vector_polygon,
    exposure_definition,
    exposure_structure,
    unit_building_type_type,
    unit_building_generic,
    layer_vector_point, unit_metres_depth, unit_feet_depth,
    layer_raster_continuous)
from safe.defaults import building_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.inundation.flood_raster_osm_building_impact\
    .parameter_definitions import threshold, hazard_level_name
from safe.utilities.i18n import tr


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
                '(OSM).'),
            'detailed_description': tr(
                'The inundation status is calculated for each building '
                '(using the centroid if it is a polygon) based on the '
                'hazard levels provided. if the hazard is given as a '
                'raster a threshold of 1 meter is used. This is '
                'configurable through the InaSAFE interface. If the '
                'hazard is given as a vector polygon layer buildings are '
                'considered to be impacted depending on the value of '
                'hazard attributes (in order) affected" or "FLOODPRONE": '
                'If a building is in a region that has attribute '
                '"affected" set to True (or 1) it is impacted. If '
                'attribute "affected" does not exist but "FLOODPRONE" '
                'does, then the building is considered impacted if '
                '"FLOODPRONE" is "yes". If neither affected" nor '
                '"FLOODPRONE" is available, a building will be impacted '
                'if it belongs to any polygon. The latter behaviour is '
                'implemented through the attribute "inapolygon" which is '
                'automatically assigned.'),
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
                   'either based on a fixed threshold in case of raster '
                   'hazard or the the attributes mentioned under input '
                   'in case of vector hazard.')
            ],
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
                        unit_feet_depth],
                    'layer_constraints': [
                        layer_raster_continuous,
                        ]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_structure],
                    'units': [
                        unit_building_type_type,
                        unit_building_generic],
                    'layer_constraints': [
                        layer_vector_polygon,
                        layer_vector_point
                    ]
                }
            },
            'parameters': OrderedDict([
                ('threshold', threshold()),
                ('hazard_level_name', hazard_level_name()),
                ('postprocessors', OrderedDict([
                    ('BuildingType', building_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
