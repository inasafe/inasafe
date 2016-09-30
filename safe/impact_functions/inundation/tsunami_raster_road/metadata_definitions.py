# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Tsunami Raster Impact on
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'etiennetrimaille'
__project_name__ = 'inasafe-dev'
__filename__ = 'metadata_definitions.py'
__date__ = '11/03/16'
__copyright__ = 'etienne@kartoza.com'

from safe.definitionsv4.layer_modes import layer_mode_continuous, \
    layer_mode_classified
from safe.definitionsv4.fields import road_class_field
from safe.definitionsv4.exposure import exposure_road
from safe.definitionsv4.units import unit_feet, unit_metres
from safe.definitionsv4.hazard import hazard_category_multiple_event, hazard_tsunami
from safe.definitionsv4.hazard_category import hazard_category_single_event, \
    hazard_category_multiple_event
from safe.definitionsv4.layer_geometry import layer_geometry_line, \
    layer_geometry_raster
from safe.common.utilities import OrderedDict
from safe.defaults import road_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.inundation.tsunami_raster_building \
    .parameter_definitions import (
        low_threshold,
        medium_threshold,
        high_threshold
    )
from safe.utilities.i18n import tr


class TsunamiRasterRoadMetadata(ImpactFunctionMetadata):
    """Metadata for Tsunami Raster Road Impact Function.

    .. versionadded:: 3.3

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
            'id': 'TsunamiRasterRoadFunction',
            'name': tr('Raster tsunami on roads'),
            'impact': tr('Be inundated'),
            'title': tr('Be inundated'),
            'function_type': 'qgis2.0',
            # should be a list, but we can do it later.
            'author': 'Ole Nielsen, Kristy van Putten, and Ismail Sunni',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of tsunami inundation on roads in '
                'vector format with hazard in raster format.'),
            'detailed_description': tr(
                'The inundation status is calculated for each roads based on '
                'the tsunami threshold. The threshold can be configured in '
                'impact function options.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents tsunami '
                'inundation depth (in meters).'),
            'exposure_input': tr(
                'Vector line where each feature represents the road.'),
            'output': tr(
                'Vector layer contains road is estimated to be '
                'inundated and the breakdown of the road by type.'),
            'actions': tr(
                'Provide details about where critical road '
                'might be inundated.'),
            'limitations': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_units': '',
            'legend_notes': '',
            'legend_title': tr('Road inundated status'),
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_continuous,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': [hazard_tsunami],
                    'continuous_hazard_units': [unit_feet, unit_metres],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [],
                    'additional_keywords': []
                },
                'exposure': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_line],
                    'exposure_types': [exposure_road],
                    'exposure_units': [],
                    'exposure_class_fields': [road_class_field],
                    'additional_keywords': []
                }
            },
            'parameters': OrderedDict(
                [
                    ('low_threshold', low_threshold()),
                    ('medium_threshold', medium_threshold()),
                    ('high_threshold', high_threshold()),
                    ('postprocessors', OrderedDict([
                        ('RoadType', road_type_postprocessor())
                    ])
                    )
                ])
        }
        return dict_meta
