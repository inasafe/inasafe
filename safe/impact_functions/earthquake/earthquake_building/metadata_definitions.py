# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Earthquake
Impact Function on Building.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.definitionsv4.definitions_v3 import (
    layer_mode_classified,
    layer_geometry_polygon,
    layer_geometry_raster,
    hazard_earthquake,
    hazard_category_multiple_event
)
from safe.definitionsv4.layer_modes import layer_mode_continuous, \
    layer_mode_classified
from safe.definitionsv4.fields import structure_class_field
from safe.definitionsv4.exposure import exposure_structure
from safe.definitionsv4.units import unit_mmi
from safe.definitionsv4.hazard import hazard_category_single_event, \
    hazard_category_multiple_event, hazard_earthquake
from safe.definitionsv4.layer_geometry import layer_geometry_point, \
    layer_geometry_polygon, layer_geometry_raster
from safe.common.utilities import OrderedDict
from safe.defaults import building_type_postprocessor
from safe.impact_functions.earthquake.earthquake_building\
    .parameter_definitions import (
        low_threshold, medium_threshold, high_threshold)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'metadata_definitions'
__date__ = '24/03/15'
__copyright__ = 'lana.pcfre@gmail.com'


class EarthquakeBuildingMetadata(ImpactFunctionMetadata):
    """Metadata for Earthquake Building Impact Function.

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
            'id': 'EarthquakeBuildingFunction',
            'name': tr('Earthquake on buildings'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'N/A',
            'date_implemented': 'N/A',
            'overview': tr(
                'This impact function will calculate the impact of an '
                'earthquake on buildings, reporting how many are expected '
                'to be damaged.'),
            'detailed_description': '',
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_notes': tr(
                'The level of the impact is according to the threshold the '
                'user input.'),
            'legend_units': tr('(mmi)'),
            'legend_title': tr('Impact level'),
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': [hazard_earthquake],
                    'continuous_hazard_units': [unit_mmi],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [
                        layer_geometry_point,
                        layer_geometry_polygon
                    ],
                    'exposure_types': [exposure_structure],
                    'exposure_units': [],
                    'exposure_class_fields': [structure_class_field],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict(
                [('low_threshold', low_threshold()),
                 ('medium_threshold', medium_threshold()),
                 ('high_threshold', high_threshold()),
                 ('postprocessors', OrderedDict([
                     ('BuildingType',
                      building_type_postprocessor())]))]
            )
        }
        return dict_meta
