# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Flood Polygon
on Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'

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
    layer_mode_classified,
    layer_mode_continuous,
    layer_geometry_polygon,
    layer_geometry_raster,
    hazard_flood,
    hazard_category_single_event,
    flood_vector_hazard_classes,
    count_exposure_unit,
    exposure_population,
    affected_field,
    affected_value
)


class FloodEvacuationVectorHazardMetadata(ImpactFunctionMetadata):
    """Metadata for FloodEvacuationFunctionVectorHazard.

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
            'id': 'FloodEvacuationVectorHazardFunction',
            'name': tr('Polygon flood on people'),
            'impact': tr('Need evacuation'),
            'title': tr('Need evacuation'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of flood inundation in vector '
                'format on population.'),
            'detailed_description': tr(
                'The population subject to inundation is determined by '
                'whether they are in a flood affected area or not. You can '
                'also set an evacuation percentage to calculate what '
                'percentage of the affected population should be '
                'evacuated. This number will be used to estimate needs '
                'based on the user defined minimum needs file.'),
            'hazard_input': tr(
                'A hazard vector layer which has an affected attribute. If '
                'it does not have that attribute, all polygons will be '
                'considered as affected.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represents a '
                'population count.'),
            'output': tr(
                'A vector layer containing the number of people affected '
                'per flood area and the minimum needs based on '
                'evacuation percentage.'),
            'actions': tr(
                'Provide details about how many people would likely need '
                'to be evacuated, where they are located and what '
                'resources would be required to support them.'),
            'limitations': [],
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [hazard_category_single_event],
                    'hazard_types': [hazard_flood],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        flood_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': [affected_field, affected_value]
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
                # This field of the  hazard layer contains information
                # about inundated areas
                ('affected_field', 'FLOODPRONE'),
                # This value in 'affected_field' of the hazard layer
                # marks the areas as inundated
                ('affected_value', 'YES'),
                # Percent of affected needing evacuation
                ('evacuation_percentage', 1),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
