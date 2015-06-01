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
    layer_mode_classified,
    layer_mode_continuous,
    layer_geometry_polygon,
    layer_geometry_raster,
    hazard_all,
    hazard_category_multiple_event,
    exposure_population,
    all_vector_hazard_classes,
    hazard_category_single_event,
    count_exposure_unit,
    hazard_zone_field
)
from safe.defaults import (
    default_minimum_needs,
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
                'for each area.'),
            'actions': tr(
                'Provide details about the number of people that are '
                'within each hazard zone.'),
            'limitations': [],
            'citations': [],
            'overview': tr(
                'To assess the the number of people that may be impacted by '
                'each hazard zone.'),
            'detailed_description': '',
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
                    'vector_hazard_classifications': all_vector_hazard_classes,
                    'raster_hazard_classifications': [],
                    'additional_keywords': [hazard_zone_field]
                },
                'exposure': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'exposure_types': [exposure_population],
                    'exposure_units': [count_exposure_unit],
                    'additional_keywords': []
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
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
