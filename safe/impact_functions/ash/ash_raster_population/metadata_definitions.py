# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Ash Raster on Population
Metadata

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from definitionsv4.definitions_v3 import (
    layer_mode_continuous,
    layer_geometry_raster,
    hazard_category_single_event,
    hazard_category_multiple_event,
    exposure_population,
    hazard_volcanic_ash,
    unit_centimetres,
    count_exposure_unit
)
from safe.common.utilities import OrderedDict
from safe.defaults import (
    default_gender_postprocessor,
    minimum_needs_selector,
    age_postprocessor)
from safe.defaults import (
    default_minimum_needs)
from safe.impact_functions.ash.parameter_definitions import \
    threshold_group_parameter
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'metadata_definitions.py'
__date__ = '7/13/16'
__copyright__ = 'imajimatika@gmail.com'


class AshRasterPopulationFunctionMetadata(ImpactFunctionMetadata):

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
            'id': 'AshRasterPopulationFunction',
            'name': tr('Ash raster on population'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'Ismail Sunni',
            'date_implemented': '13/07/2016',
            'overview': tr(
                'To assess the impact of each hazard zone on population.'),
            'detailed_description': '',
            'hazard_input': tr(
                'The hazard layer must be an ash raster layer.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represents the '
                'population count for that cell.'),
            'output': tr(
                'Map of population exposed to the highest hazard zone and a '
                'table with the number of population in each hazard zone'),
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
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': [hazard_volcanic_ash],
                    'continuous_hazard_units': [unit_centimetres],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'exposure_types': [exposure_population],
                    'exposure_units': [count_exposure_unit],
                    'exposure_class_fields': [],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict(
                [
                    ('group_threshold', threshold_group_parameter()),
                    ('postprocessors', OrderedDict([
                        ('Gender', default_gender_postprocessor()),
                        ('Age', age_postprocessor()),
                        ('MinimumNeeds', minimum_needs_selector()),
                    ])),
                    ('minimum needs', default_minimum_needs())
                ])
        }
        return dict_meta
