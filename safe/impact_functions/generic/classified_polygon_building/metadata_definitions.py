# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Polygon on Building
Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.definitions import (
    layer_mode_classified,
    layer_geometry_polygon,
    layer_geometry_point,
    hazard_all,
    hazard_category_multiple_event,
    exposure_structure,
    all_vector_hazard_classes,
    hazard_category_single_event,
    layer_mode_none,
    hazard_zone_field
)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class ClassifiedPolygonHazardBuildingFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for ClassifiedPolygonBuildingFunctionMetadata.

    .. versionadded:: 3.1

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
            'id': 'ClassifiedPolygonHazardBuildingFunction',
            'name': tr('Classified polygon hazard on buildings'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'Akbar Gumbira (akbargumbira@gmail.com)',
            'date_implemented': '17/04/2015',
            'overview': tr(
                'To assess the impact of each hazard zone on buildings.'),
            'detailed_description': '',
            'hazard_input': tr(
                'The hazard layer must be a polygon layer. This layer '
                'must have an attribute representing the hazard '
                'zone that can be specified in the impact function options.'),
            'exposure_input': tr(
                'Vector polygon layer extracted from OSM where each '
                'polygon represents the footprint of a building.'),
            'output': tr(
                'A vector layer of buildings with each tagged according to '
                'the hazard zone in which it falls.'),
            'actions': tr(
                'Provide details about how many buildings fall within '
                'each hazard zone.'),
            'limitations': [],
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [
                        hazard_category_multiple_event,
                        hazard_category_single_event
                    ],
                    'hazard_types': hazard_all,
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications':
                        all_vector_hazard_classes,
                    'raster_hazard_classifications': [],
                    'additional_keywords': [hazard_zone_field]
                },
                'exposure': {
                    'layer_mode': layer_mode_none,
                    'layer_geometries': [
                        layer_geometry_point,
                        layer_geometry_polygon
                    ],
                    'exposure_types': [exposure_structure],
                    'exposure_units': [],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([
                # The attribute of hazard zone in hazard layer
                ('hazard zone attribute', 'KRB')
            ])
        }
        return dict_meta
