# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on Building
Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.definitions import (
    layer_mode_classified,
    layer_geometry_polygon,
    layer_geometry_point,
    hazard_volcano,
    volcano_vector_hazard_classes,
    hazard_category_multiple_event,
    exposure_structure,
    layer_mode_none,
    volcano_name_field,
    hazard_zone_field
)


class VolcanoPolygonBuildingFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for VolcanoPolygonBuildingFunctionMetadata.

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
            'id': 'VolcanoPolygonBuildingFunction',
            'name': tr('Polygon volcano on buildings'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of volcano eruption on building.'),
            'detailed_description': '',
            'hazard_input': tr(
                'The hazard layer must be a polygon layer. This layer '
                'must have an attribute representing the volcano hazard '
                'zone that can be specified in the impact function option.'
                'The valid values for the volcano hazard zone are "Kawasan '
                'Rawan Bencana I", "Kawasan Rawan Bencana II", '
                'or "Kawasan  Rawan Bencana III." If you want to see the '
                'name of the volcano in the result, you need to specify '
                'the volcano name attribute in the Impact Function '
                'options.'),
            'exposure_input': tr(
                'Vector polygon layer extracted from OSM where each '
                'polygon represents the footprint of a building.'),
            'output': tr(
                'Vector layer contains Map of building exposed to '
                'volcanic hazard zones for each Kawasan Rawan Bencana.'),
            'actions': tr(
                'Provide details about the number of buildings that are '
                'within each hazard zone.'),
            'limitations': [],
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [hazard_category_multiple_event],
                    'hazard_types': [hazard_volcano],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        volcano_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': [
                        volcano_name_field, hazard_zone_field]
                },
                'exposure': {
                    'layer_mode': layer_mode_none,
                    'layer_geometries': [
                        layer_geometry_polygon,
                        layer_geometry_point
                    ],
                    'exposure_types': [exposure_structure],
                    'exposure_units': [],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([
                # The attribute of hazard zone in hazard layer
                ('hazard zone attribute', 'KRB'),
                # The attribute for name of the volcano in hazard layer
                ('volcano name attribute', 'NAME')
            ])
        }
        return dict_meta
