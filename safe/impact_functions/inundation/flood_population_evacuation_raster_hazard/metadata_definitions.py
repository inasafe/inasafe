# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Raster Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'

from safe.common.utilities import OrderedDict
from safe.defaults import default_minimum_needs, default_provenance, \
    get_defaults
from safe.definitions import (
    hazard_definition,
    hazard_flood,
    exposure_definition,
    exposure_population,
    unit_people_per_pixel,
    layer_raster_continuous, unit_feet_depth, unit_metres_depth)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class FloodEvacuationRasterHazardMetadata(ImpactFunctionMetadata):
    """Metadata for FloodEvacuationFunction.

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
            'id': 'FloodEvacuationRasterHazardFunction',
            'name': tr('Flood Evacuation Raster Hazard Function'),
            'impact': tr('Need evacuation'),
            'title': tr('Need evacuation'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of flood inundation in raster '
                'format on population.'),
            'detailed_description': tr(
                'The population subject to inundation exceeding a '
                'threshold (default 1m) is calculated and returned as a '
                'raster layer. In addition the total number and the '
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
                'A hazard raster layer where each cell represents flood '
                'depth (in meters).'),
            'exposure_input': tr(
                'An exposure raster layer where each cell represent '
                'population count.'),
            'output': tr(
                'Raster layer contains people affected and the minimum '
                'needs based on the people affected.'),
            'actions': tr(
                'Provide details about how many people would likely need '
                'to be evacuated, where they are located and what '
                'resources would be required to support them.'),
            'limitations': [
                tr('The default threshold of 1 meter was selected based '
                   'on consensus, not hard evidence.')
            ],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_flood],
                    'units': [
                        unit_feet_depth,
                        unit_metres_depth
                    ],
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
                ('thresholds [m]', [1.0]),
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
