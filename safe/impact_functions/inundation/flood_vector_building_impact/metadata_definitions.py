# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for Flood Vector
Impact on OSM Buildings using QGIS libraries.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'

from safe.common.utilities import OrderedDict
from safe.definitions import (
    hazard_definition,
    hazard_flood,
    hazard_tsunami,
    unit_wetdry,
    layer_vector_polygon,
    exposure_definition,
    exposure_structure,
    unit_building_type_type)
from safe.defaults import building_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.inundation.flood_vector_building_impact\
    .parameter_definitions import (
        building_type_field,
        affected_field,
        affected_value)
from safe.utilities.i18n import tr


class FloodPolygonBuildingFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for Flood Vector on Building Impact Function using QGIS.

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
            'id': 'FloodPolygonBuildingFunction',
            'name': tr('Polygon flood on buildings'),
            'impact': tr('Be flooded'),
            'title': tr('Be flooded'),
            'function_type': 'qgis2.0',
            'author': 'Dmitry Kolesov',
            'date_implemented': 'N/A',
            'overview': tr('N/A'),
            'detailed_description': tr('N/A'),
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_flood, hazard_tsunami],
                    'units': [unit_wetdry],
                    'layer_constraints': [layer_vector_polygon]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_structure],
                    'units': [unit_building_type_type],
                    'layer_constraints': [layer_vector_polygon]
                }
            },
            'parameters': OrderedDict([
                # This field of the exposure layer contains
                # information about building types
                ('building_type_field', building_type_field()),
                # This field of the  hazard layer contains information
                # about inundated areas
                ('affected_field', affected_field()),
                # This value in 'affected_field' of the hazard layer
                # marks the areas as inundated
                ('affected_value', affected_value()),

                ('postprocessors', OrderedDict([
                    ('BuildingType', building_type_postprocessor())
                ]))
            ])
            }
        return dict_meta
