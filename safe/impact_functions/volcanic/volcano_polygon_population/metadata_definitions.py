# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Polygon on Population
Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.defaults import (
    default_minimum_needs,
    default_provenance,
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.new_definitions import (
    layer_mode_classified,
    layer_mode_continuous,
    layer_geometry_polygon,
    layer_geometry_point,
    layer_geometry_raster,
    hazard_volcano,
    volcano_vector_hazard_classes,
    hazard_category_hazard_zone,
    exposure_population,
    count_exposure_unit
)


class VolcanoPolygonPopulationFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for VolcanoPolygonPopulationFunctionMetadata.

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
            'id': 'VolcanoPolygonPopulationFunction',
            'name': tr('Volcano Polygon Population Impact Function'),
            'impact': tr('Need evacuation'),
            'title': tr('Need evacuation'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'hazard_input': tr(
                'A hazard vector layer can be polygon or point. If '
                'polygon, it must have "KRB" attribute and the valuefor '
                'it are "Kawasan Rawan Bencana I", "Kawasan Rawan Bencana '
                'II", or "Kawasan Rawan Bencana III."If you want to see '
                'the name of the volcano in the result, you need to add '
                '"NAME" attribute for point data or "GUNUNG" attribute '
                'for polygon data.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represent '
                'population count.'),
            'output': tr(
                'Vector layer contains people affected and the minimum '
                'needs based on the number of people affected.'),
            'actions': tr(
                'Provide details about how many population would likely '
                'be affected by each hazard zones.'),
            'limitations': [],
            'citations': [],
            'overview': tr(
                'To assess the impacts of volcano eruption on '
                'population.'),
            'detailed_description': '',
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [
                        layer_geometry_polygon,
                        layer_geometry_point
                    ],
                    'hazard_categories': [hazard_category_hazard_zone],
                    'hazard_types': [hazard_volcano],
                    'units_classes': [volcano_vector_hazard_classes]
                },
                'exposure': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'exposure_types': [exposure_population],
                    'units_classes': [count_exposure_unit]
                }
            },
            'parameters': OrderedDict([
                ('distance [km]', [3, 5, 10]),
                ('minimum needs', default_minimum_needs()),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())
            ])
        }
        return dict_meta
