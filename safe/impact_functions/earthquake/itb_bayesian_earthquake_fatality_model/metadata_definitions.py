# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for ITB Earthquake
Impact Function on Population based on a Bayesian approach.

Contact : dynaryu@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'dynaryu@gmail.com'
__date__ = '09/09/15'

from safe.definitionsv4.definitions_v3 import (
    hazard_earthquake,
    count_exposure_unit
)
from safe.definitionsv4.layer_modes import layer_mode_continuous
from safe.definitionsv4.exposure import exposure_population
from safe.definitionsv4.units import unit_mmi, count_exposure_unit
from safe.definitionsv4.hazard import hazard_category_single_event, \
    hazard_earthquake
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.common.utilities import OrderedDict
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.defaults import default_minimum_needs
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .metadata_definitions import ITBFatalityMetadata
from safe.utilities.i18n import tr


class ITBBayesianFatalityMetadata(ITBFatalityMetadata):
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
            'id': 'ITBBayesianFatalityFunction',
            'name': tr(
                'Earthquake ITB fatality function based on a Bayesian '
                'approach'),
            'impact': tr('Die or be displaced according ITB bayesian model'),
            'title': tr('Die or be displaced according ITB bayesian model'),
            'function_type': 'old-style',
            'author': 'ITB and GA',  # FIXME
            'date_implemented': 'N/A',
            'overview': tr(
                'Estimates fatalities resulting from an earthquake using data '
                'from an Indonesian database of earthquake events to '
                'calculate fatality rates. This model is better at '
                'capturing uncertainty in the results.'),
            'detailed_description': tr(
                'Based on the Population Vulnerability ITB Bayesian Model.'),
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [
                {
                    'text': tr(
                        'Sengara, W., Suarjana, M., Yulman, M.A., Ghasemi, '
                        'H., and Ryu, H. (2015). An empirical fatality model '
                        'for Indonesia based on a Bayesian approach. '
                        'Submitted for Journal of the Geological Society'),
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
                    'hazard_categories': [hazard_category_single_event],
                    'hazard_types': [hazard_earthquake],
                    'continuous_hazard_units': [unit_mmi],
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
