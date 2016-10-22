# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for generic Impact
function on Population for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'metadata_definitions'
__date__ = '24/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

from safe.definitionsv4.layer_modes import layer_mode_continuous, \
    layer_mode_classified
from safe.definitionsv4.exposure import exposure_population
from safe.definitionsv4.units import count_exposure_unit, density_exposure_unit
from safe.definitionsv4.hazard import hazard_all
from safe.definitionsv4 import generic_raster_hazard_classes
from safe.definitionsv4.hazard_category import hazard_category_single_event, \
    hazard_category_multiple_event
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.common.utilities import OrderedDict, get_thousand_separator
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.defaults import default_minimum_needs
from safe.impact_functions.generic.parameter_definitions import \
    categorical_hazards
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class ClassifiedRasterHazardPopulationMetadata(ImpactFunctionMetadata):
    """Metadata for Classified Hazard Population Impact Function.

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
            'id': 'ClassifiedRasterHazardPopulationFunction',
            'name': tr('Classified raster hazard on population'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'Dianne Bencito',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of classified hazards in raster '
                'format on a population raster layer.'),
            'detailed_description': tr(
                'This function will treat the values in the hazard raster '
                'layer as classes representing low, medium and high '
                'impact. You need to ensure that the keywords for the hazard '
                'layer have been set appropriately to define these classes.'
                'The number of people that will be affected will be '
                'calculated for each class. The report will show the total '
                'number of people that will be affected for each '
                'hazard class.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents the '
                'class of the hazard. There should be three classes: e.g. '
                '1, 2, and 3.'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represents the '
                'population count for that cell.'),
            'output': tr(
                'Map of population exposed to the highest class and a table '
                'with the number of people in each class'),
            'actions': tr(
                'Provide details about how many people would likely be '
                'affected for each hazard class.'),
            'limitations': [tr('The number of classes is three.')],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_title': tr('Number of People'),
            'legend_units': tr('(people per cell)'),
            'legend_notes': tr(
                'Thousand separator is represented by %s' %
                get_thousand_separator()),
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': hazard_all,
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [
                        generic_raster_hazard_classes
                    ],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'exposure_types': [exposure_population],
                    'exposure_units': [
                        count_exposure_unit, density_exposure_unit],
                    'exposure_class_fields': [],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict([
                ('Categorical hazards', categorical_hazards()),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
