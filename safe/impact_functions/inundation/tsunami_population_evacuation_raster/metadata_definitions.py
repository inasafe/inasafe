# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Tsunami Raster
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'metadata_definitions'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

from safe.defaults import (
    default_minimum_needs)
from safe.defaults import (
    default_gender_postprocessor,
    minimum_needs_selector,
    age_postprocessor)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr
from safe.common.utilities import OrderedDict
from safe.definitions import (
    layer_mode_continuous,
    layer_geometry_raster,
    hazard_category_single_event,
    unit_metres,
    unit_feet,
    count_exposure_unit,
    exposure_population,
    hazard_tsunami
)


class TsunamiEvacuationMetadata(ImpactFunctionMetadata):
    """Metadata for TsunamiEvacuationFunction.

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
            'id': 'TsunamiEvacuationFunction',
            'name': tr('Tsunami evacuation'),
            'impact': tr('Need evacuation'),
            'title': tr('Need evacuation'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of tsunami inundation in raster '
                'format on population.'),
            'detailed_description': tr(
                'The population subject to inundation exceeding a '
                'threshold (default 0.7m) is calculated and returned as '
                'a raster layer. In addition the total number and the '
                'required needs in terms of the BNPB (Perka 7) are '
                'reported. The threshold can be changed and even contain '
                'multiple numbers in which case evacuation and needs are '
                'calculated using the largest number with population '
                'breakdowns provided for the smaller numbers. The '
                'population raster is resampled to the resolution of the '
                'hazard raster and is rescaled so that the resampled '
                'population counts reflect estimates of population count '
                'per resampled cell. The resulting impact layer has the '
                'same resolution and reflects population count per cell '
                'which are affected by inundation.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents tsunami '
                'depth (in meters).'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represent '
                'population count.'),
            'output': tr(
                'Raster layer contains population affected and the '
                'minimum needs based on the population affected.'),
            'actions': tr(
                'Provide details about how many people would likely need '
                'to be evacuated, where they are located and what '
                'resources would be required to support them.'),
            'limitations': [tr(
                'The default threshold of 0.7 meter was selected based on '
                'consensus, not hard evidence.')],
            'citations': [],
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [hazard_category_single_event],
                    'hazard_types': [hazard_tsunami],
                    'continuous_hazard_units': [unit_feet, unit_metres],
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
                ('thresholds [m]', [0.7]),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                ])),
                ('minimum needs', default_minimum_needs())
            ])
        }
        return dict_meta
