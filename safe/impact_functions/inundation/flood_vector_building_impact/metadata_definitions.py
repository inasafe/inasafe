# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Flood Vector
Impact on OSM Buildings using QGIS libraries.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'

from safe.common.utilities import OrderedDict
from safe.defaults import building_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.definitions import (
    layer_mode_classified,
    layer_geometry_polygon,
    layer_geometry_point,
    hazard_flood,
    hazard_category_single_event,
    hazard_category_multiple_event,
    exposure_structure,
    flood_vector_hazard_classes,
    structure_class_field
)


class FloodPolygonBuildingFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for Flood Vector on Building Impact Function using QGIS.

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
            'id': 'FloodPolygonBuildingFunction',
            'name': tr('Polygon flood on buildings'),
            'impact': tr('Be flooded'),
            'title': tr('Be flooded'),
            'function_type': 'qgis2.0',
            'author': 'Dmitry Kolesov',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of (flood or tsunami) inundation '
                'on building footprints with hazard in vector format.'),
            'detailed_description': tr(
                'The inundation status is calculated for each building '
                '(using the centroid if it is a polygon) based on the value '
                'of hazard attribute. The attribute and the values that are '
                'considered as flooded can be configured in impact function '
                'options.'),
            'hazard_input': tr(
                'A hazard vector layer whose attribute that can be used to '
                'mark whether a polygon is flood or not.'),
            'exposure_input': tr(
                'Vector polygon or point layer extracted from OSM where '
                'each feature represents the footprint of a building.'),
            'output': tr(
                'Vector layer contains building is estimated to be '
                'flooded and the breakdown of the building by type.'),
            'actions': '',
            'limitations': [],
            'citations': [],
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
                    'layer_geometries': [
                        layer_geometry_polygon,
                        layer_geometry_point],
                    'exposure_types': [exposure_structure],
                    'exposure_units': [],
                    'exposure_class_fields': [structure_class_field],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([
                ('postprocessors', OrderedDict([
                    ('BuildingType', building_type_postprocessor())
                ]))
            ])
            }
        return dict_meta
