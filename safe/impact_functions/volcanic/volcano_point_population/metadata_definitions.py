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
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.definitions import (
    layer_mode_none,
    layer_geometry_point,
    hazard_volcano,
    volcano_vector_hazard_classes,
    hazard_category_multiple_event,
    exposure_population,
    layer_geometry_raster,
    count_exposure_unit,
    layer_mode_continuous,
    volcano_name_field
)


class VolcanoPointPopulationFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for VolcanoPointPopulationFunctionMetadata.

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
            'id': 'VolcanoPointPopulationFunction',
            'name': tr('Point volcano on population'),
            'impact': tr('Be impacted'),
            'title': tr('Be impacted'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'hazard_input': tr(
                'A point vector layer.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represent '
                'population count.'),
            'output': tr(
                'Vector layer contains people affected and the minimum '
                'needs based on the number of people affected.'),
            'actions': tr(
                'Provide details about how many people would likely '
                'be affected by each hazard zone.'),
            'limitations': [],
            'citations': [],
            'overview': tr(
                'To assess the impacts of volcano eruption on '
                'population.'),
            'detailed_description': '',
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_none,
                    'layer_geometries': [layer_geometry_point],
                    'hazard_categories': [hazard_category_multiple_event],
                    'hazard_types': [hazard_volcano],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        volcano_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': [volcano_name_field]
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
                # The radii
                ('distance [km]', [3, 5, 10]),
                # The attribute for name of the volcano in hazard layer
                ('volcano name attribute', 'NAME'),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
