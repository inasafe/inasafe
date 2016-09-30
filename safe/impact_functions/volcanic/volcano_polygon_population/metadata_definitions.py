# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Polygon on Population
Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.definitionsv4.layer_modes import layer_mode_continuous, \
    layer_mode_classified
from safe.definitionsv4.fields import volcano_name_field
from safe.definitionsv4.exposure import exposure_population
from safe.definitionsv4.units import count_exposure_unit
from safe.definitionsv4.hazard import hazard_category_multiple_event, \
    hazard_volcano
from safe.definitionsv4 import volcano_vector_hazard_classes
from safe.definitionsv4.hazard_category import hazard_category_single_event, \
    hazard_category_multiple_event
from safe.definitionsv4.layer_geometry import layer_geometry_polygon, \
    layer_geometry_raster
from safe.common.utilities import OrderedDict, get_thousand_separator
from safe.defaults import (
    default_minimum_needs,
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
                'The hazard layer must be a polygon layer. This layer '
                'must have an attribute representing the volcano hazard '
                'zone that can be specified in the impact function option. '
                'There are three classes low, medium, and high. The default '
                'values are "Kawasan Rawan Bencana I" for low, "Kawasan Rawan '
                'Bencana II" for medium, and "Kawasan  Rawan Bencana III for '
                'high." If you want to see the name of the volcano in the '
                'result, you need to specify the volcano name attribute in '
                'the Impact Function options.'),
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
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_title': tr('Population'),
            'legend_units': tr('(people per cell)'),
            'legend_notes': tr(
                'Thousand separator is represented by  %s' %
                get_thousand_separator()),
            'overview': tr(
                'To assess the impact of a volcano eruption on people.'),
            'detailed_description': '',
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_polygon],
                    'hazard_categories': [
                        hazard_category_multiple_event,
                        hazard_category_single_event
                    ],
                    'hazard_types': [hazard_volcano],
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [
                        volcano_vector_hazard_classes],
                    'raster_hazard_classifications': [],
                    'additional_keywords': [
                        volcano_name_field]
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
            'parameters': OrderedDict([
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
