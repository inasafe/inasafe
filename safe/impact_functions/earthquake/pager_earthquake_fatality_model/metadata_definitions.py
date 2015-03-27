# coding=utf-8

__author__ = 'lucernae'
__date__ = '24/03/15'

import numpy
from safe.common.utilities import OrderedDict
from safe.defaults import get_defaults, default_minimum_needs, \
    default_provenance
from safe.definitions import hazard_definition, hazard_earthquake, unit_mmi, \
    layer_raster_continuous, exposure_definition, exposure_population, \
    unit_people_per_pixel
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector
    )
from safe.impact_functions.earthquake.itb_earthquake_fatality_model.metadata_definitions import \
    ITBFatalityMetadata
from safe.utilities.i18n import tr


class PAGFatalityMetadata(ITBFatalityMetadata):
    """Metadata for PAG Fatality Function.

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
        defaults = get_defaults()
        dict_meta = {
            'id': 'PAGFatalityFunction',
            'name': tr('PAG Fatality Function'),
            'impact': tr('Die or be displaced according Pager model'),
            'title': tr('Die or be displaced according Pager model'),
            'function_type': 'old-style',
            'author': 'Helen Crowley',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impact of earthquake on population based '
                'on Population Vulnerability Model Pager'),
            'detailed_description': '',
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [
                tr('Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a). '
                   'Estimating casualties for large worldwide earthquakes '
                   'using an empirical approach. U.S. Geological Survey '
                   'Open-File Report 2009-1136.')
            ],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_earthquake],
                    'units': [unit_mmi],
                    'layer_constraints': [layer_raster_continuous]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_population],
                    'units': [unit_people_per_pixel],
                    'layer_constraints': [layer_raster_continuous]
                }
            },
            'parameters': OrderedDict([
                ('Theta', 11.067),
                ('Beta', 0.106),  # Model coefficients
                # Rates of people displaced for each MMI level
                ('displacement_rate', {
                    1: 0, 1.5: 0, 2: 0, 2.5: 0, 3: 0,
                    3.5: 0, 4: 0, 4.5: 0, 5: 0, 5.5: 0,
                    6: 1.0, 6.5: 1.0, 7: 1.0, 7.5: 1.0,
                    8: 1.0, 8.5: 1.0, 9: 1.0, 9.5: 1.0,
                    10: 1.0}),
                ('mmi_range', list(numpy.arange(2, 10, 0.5))),
                ('step', 0.25),
                # Threshold below which layer should be transparent
                ('tolerance', 0.01),
                ('calculate_displaced_people', True),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                    ])),
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())])

        }
        return dict_meta