# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for generic Impact
function on Population for Continuous Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__date__ = '24/03/15'

from safe.common.utilities import OrderedDict
from safe.defaults import default_minimum_needs
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.utilities.i18n import tr
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.definitions import (
    layer_mode_continuous,
    layer_geometry_raster,
    hazard_all,
    hazard_category_multiple_event,
    count_exposure_unit,
    exposure_population,
    hazard_category_single_event,
    continuous_hazard_unit_all,
    density_exposure_unit
)


class ContinuousHazardPopulationMetadata(ImpactFunctionMetadata):
    """Metadata for Continuous Hazard Population Impact Function.

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
            'id': 'ContinuousHazardPopulationFunction',
            'name': tr('Continuous raster hazard on population'),
            'impact': tr('Be impacted'),
            'title': tr('Be impacted'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of continuous hazards in raster '
                'format on population raster layer.'),
            'detailed_description': tr(
                'This function will categorised the continuous hazard '
                'level into 3 category based on the threshold that has '
                'been input by the user. After that, this function will '
                'calculate how many people will be impacted per category '
                'for all categories in the hazard layer.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents the '
                'level of the hazard. The hazard has continuous value of '
                'hazard level.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represent '
                'population count.'),
            'output': tr(
                'Map of population exposed to high category and a table '
                'with number of people in each category'),
            'actions': tr(
                'Provide details about how many people would likely '
                'be impacted in each category.'),
            'limitations': [tr('Only three categories can be used.')],
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_multiple_event,
                        hazard_category_single_event
                    ],
                    'hazard_types': hazard_all,
                    'continuous_hazard_units': continuous_hazard_unit_all,
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'exposure_types': [exposure_population],
                    'exposure_units': [
                        count_exposure_unit, density_exposure_unit],
                    'additional_keywords': []
                }
            },
            # Configurable parameters
            'parameters': OrderedDict([
                ('Categorical thresholds', [0.34, 0.67, 1]),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
