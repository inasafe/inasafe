# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for PAGER Earthquake
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.defaults import default_minimum_needs, default_provenance
from safe.definitions import hazard_definition, hazard_earthquake, unit_mmi, \
    layer_raster_continuous, exposure_definition, exposure_population, \
    unit_people_per_pixel
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .metadata_definitions import ITBFatalityMetadata
from safe.utilities.i18n import tr
from safe.impact_functions.earthquake.pager_earthquake_fatality_model\
    .parameter_definitions import \
    theta, beta, displacement_rate, mmi_range, \
    step, tolerance, calculate_displaced_people

__author__ = 'lucernae'
__date__ = '24/03/15'


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
                ('Theta', theta()),
                ('Beta', beta()),  # Model coefficients
                # Rates of people displaced for each MMI level
                ('displacement_rate', displacement_rate()),
                ('mmi_range', mmi_range()),
                ('step', step()),
                # Threshold below which layer should be transparent
                ('tolerance', tolerance()),
                ('calculate_displaced_people',
                 calculate_displaced_people()),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                    ])),
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())])

        }
        return dict_meta
