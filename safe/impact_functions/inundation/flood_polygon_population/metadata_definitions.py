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
    default_provenance,
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.definitions import (
    hazard_definition,
    hazard_flood,
    unit_wetdry,
    layer_vector_polygon,
    exposure_definition,
    exposure_population,
    unit_people_per_pixel,
    layer_raster_continuous, unit_metres_depth, unit_feet_depth)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


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
                'whether they are in an area which affected or not. You can '
                'also set an evacuation percentage to calculate what '
                'percent of the total population affected should be '
                'evacuated.'),
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
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_flood],
                    'units': [unit_wetdry,
                              unit_metres_depth,
                              unit_feet_depth],
                    'layer_constraints': [layer_vector_polygon]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_population],
                    'units': [unit_people_per_pixel],
                    'layer_constraints': [layer_raster_continuous]
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
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())
            ])
        }
        return dict_meta
