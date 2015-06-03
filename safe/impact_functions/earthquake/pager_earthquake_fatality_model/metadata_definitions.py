# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for PAGER Earthquake
Impact Function on Population.

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
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .metadata_definitions import ITBFatalityMetadata
from safe.utilities.i18n import tr
from safe.definitions import (
    layer_mode_continuous,
    layer_geometry_raster,
    hazard_earthquake,
    exposure_population,
    count_exposure_unit,
    hazard_category_single_event,
    unit_mmi
)


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
            'name': tr('Earthquake PAGER fatality function'),
            'impact': tr('Die or be displaced according Pager model'),
            'title': tr('Die or be displaced according Pager model'),
            'function_type': 'old-style',
            'author': 'Helen Crowley',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impact of an earthquake on population based '
                'on the Population Vulnerability Pager Model.'),
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
