# coding=utf-8

__author__ = 'lucernae'
__date__ = '24/03/15'

from safe.common.utilities import OrderedDict
from safe.defaults import (
    get_defaults, default_minimum_needs, default_provenance)
from safe.definitions import (
    hazard_definition,
    hazard_all,
    layer_raster_continuous,
    exposure_definition,
    exposure_population,
    unit_people_per_pixel)
from safe.utilities.i18n import tr
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata


class ContinuousHazardPopulationMetadata(ImpactFunctionMetadata):
    """Metadata for Continuous Hazard Population Impact Function.

    .. versionadded:: 2.1

    We only need to re-implement get_metadata(), all other behaviours
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
        defaults = get_defaults()
        dict_meta = {
            'id': 'ContinuousHazardPopulationFunction',
            'name': tr('Continuous Hazard Population Function'),
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
                'Provide details about how many people would likely need '
                'to be impacted for each category.'),
            'limitations': [tr('The number of categories is three.')],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': hazard_all,  # already a list
                    'units': [],
                    'layer_constraints': [layer_raster_continuous]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_population],
                    'units': [unit_people_per_pixel],
                    'layer_constraints': [layer_raster_continuous]
                }
            },
            # Configurable parameters
            'parameters': OrderedDict([
                ('Categorical thresholds', [0.34, 0.67, 1]),
                ('postprocessors', OrderedDict([
                    ('Gender', {'on': True}),
                    ('Age', {
                        'on': True,
                        'params': OrderedDict([
                            ('youth_ratio', defaults['YOUTH_RATIO']),
                            ('adult_ratio', defaults['ADULT_RATIO']),
                            ('elderly_ratio', defaults['ELDERLY_RATIO'])])}),
                    ('MinimumNeeds', {'on': True}),
                ])),
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())
            ])
        }
        return dict_meta