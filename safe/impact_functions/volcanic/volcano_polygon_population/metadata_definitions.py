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
from safe.definitions import (
    hazard_volcano,
    unit_volcano_categorical,
    layer_vector_polygon,
    layer_raster_continuous,
    exposure_population,
    unit_people_per_pixel,
    hazard_definition,
    exposure_definition)
from safe.defaults import (
    default_minimum_needs,
    default_provenance,
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


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
            'name': tr('Polygon volcano on population'),
            'impact': tr('Need evacuation'),
            'title': tr('Need evacuation'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'hazard_input': tr(
                'The hazard vector layer must be a polygon that has a '
                'specific hazard zone attribute.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represents a '
                'population count for that cell.'),
            'output': tr(
                'A vector layer containing people affected per hazard zone '
                'and the minimum needs based on the number of people '
                'affected.'),
            'actions': tr(
                'Provide details about the number of people that are within '
                'each hazard zone.'),
            'limitations': [],
            'citations': [],
            'overview': tr(
                'To assess the impact of a volcano eruption on people.'),
            'detailed_description': '',
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_volcano],
                    'units': [unit_volcano_categorical],
                    'layer_constraints': [
                        layer_vector_polygon
                    ]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_population],
                    'units': [unit_people_per_pixel],
                    'layer_constraints': [layer_raster_continuous]
                }
            },
            'parameters': OrderedDict([
                # The attribute of hazard zone in hazard layer
                ('hazard zone attribute', 'KRB'),
                # The attribute for name of the volcano in hazard layer
                ('volcano name attribute', 'NAME'),
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
