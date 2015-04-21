# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Classified Polygon on
Population Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.definitions import (
    hazard_all,
    unit_classified,
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


class ClassifiedPolygonHazardPopulationFunctionMetadata(
    ImpactFunctionMetadata):
    """Metadata for ClassifiedPolygonHazardPopulationFunctionMetadata.

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
            'id': 'ClassifiedPolygonHazardPopulationFunction',
            'name': tr('Classified polygon hazard on population'),
            'impact': tr('Be impacted'),
            'title': tr('Be impacted'),
            'function_type': 'old-style',
            'author': 'Akbar Gumbira (akbargumbira@gmail.com)',
            'date_implemented': 'N/A',
            'hazard_input': tr(
                'A hazard vector layer must be a polygon layer that has a '
                'hazard zone attribute.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represents '
                'the population count for that cell.'),
            'output': tr(
                'A vector layer containing polygons matching the hazard areas'
                'and an attribute representing the number of people affected '
                'for each area. The minimum needs for the affected people are '
                'also calculated.'),
            'actions': tr(
                'Provide details about how many people would likely '
                'be affected by each hazard zone.'),
            'limitations': [],
            'citations': [],
            'overview': tr(
                'To assess the impact of each hazard zone on population.'),
            'detailed_description': '',
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': hazard_all,
                    'units': [unit_classified],
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
