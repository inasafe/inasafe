# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Classified Polygon on
Land Cover Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.exposure import exposure_land_cover
from safe.definitionsv4.hazard import hazard_category_single_event, \
    hazard_category_multiple_event, generic_vector_hazard_classes, hazard_all
from safe.definitionsv4.layer_geometry import layer_geometry_polygon
from safe.common.utilities import OrderedDict
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class ClassifiedPolygonHazardLandCoverFunctionMetadata(ImpactFunctionMetadata):

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
            'id': 'ClassifiedPolygonHazardLandCoverFunction',
            'name': tr('Classified polygon hazard on land cover'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'qgis2.0',
            'author': 'Martin Dobias (wonder.sk@gmail.com)',
            'date_implemented': '15/06/2015',
            'overview': tr(
                'To assess the impact of each hazard zone on land cover.'),
            'detailed_description': '',
            'hazard_input': tr(
                'The hazard layer must be a polygon layer. This layer '
                'must have an attribute representing the hazard '
                'zone that can be specified in the impact function options.'),
            'exposure_input': tr(
                'Vector polygon layer where each '
                'polygon represents a type of land cover.'),
            'output': tr(
                'A vector layer of land cover polygons with each tagged '
                'according to the hazard zone in which it falls.'),
            'actions': tr(
                'Provide details about how big area fall within '
                'each hazard zone.'),
            'limitations': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_title': '',
            'legend_units': '',
            'legend_notes': '',
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': hazard_all,
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        generic_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'exposure_types': [exposure_land_cover],
                    'exposure_units': [],
                    'exposure_class_fields': [],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([])
        }
        return dict_meta
