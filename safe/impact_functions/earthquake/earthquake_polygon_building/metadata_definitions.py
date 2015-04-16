# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Earthquake Polygon on
Building Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.definitions import (
    hazard_definition,
    hazard_earthquake,
    unit_volcano_categorical,
    layer_vector_point,
    layer_vector_polygon,
    exposure_definition,
    exposure_structure,
    unit_building_type_type,
    unit_building_generic)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class EarthquakePolygonBuildingFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for EarthquakePolygonBuildingFunctionMetadata.

    .. versionadded:: 3.1

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
            'id': 'EarthquakePolygonBuildingFunction',
            'name': tr('Earthquake Polygon Building Impact Function'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of earthquake polygon on building.'),
            'detailed_description': '',
            'hazard_input': tr(
                'The hazard layer must be a polygon layer. This layer '
                'must have an attribute representing the earthquake hazard '
                'zone that can be specified in the impact function option.'),
            'exposure_input': tr(
                'Vector polygon layer extracted from OSM where each '
                'polygon represents the footprint of a building.'),
            'output': tr(
                'Vector layer contains Map of building exposed to '
                'each earthquake hazard zones.'),
            'actions': tr(
                'Provide details about how many building would likely be '
                'affected by each hazard zones.'),
            'limitations': [],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_earthquake],
                    'units': [unit_volcano_categorical],
                    'layer_constraints': [layer_vector_polygon]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_structure],
                    'units': [
                        unit_building_type_type,
                        unit_building_generic],
                    'layer_constraints': [
                        layer_vector_polygon,
                        layer_vector_point]
                }
            },
            'parameters': OrderedDict([
                # The attribute of hazard zone in hazard layer
                ('hazard zone attribute', 'hazard')
            ])
        }
        return dict_meta
