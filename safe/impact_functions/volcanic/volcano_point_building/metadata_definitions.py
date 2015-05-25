# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on Building
Metadata Definitions.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.definitions import (
    hazard_definition,
    hazard_volcano,
    unit_volcano_categorical,
    layer_vector_point,
    layer_vector_polygon,
    exposure_definition,
    exposure_structure,
    unit_building_type_type,
    unit_building_generic)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.volcanic.volcano_point_building\
    .parameter_definitions import (
        distance, volcano_name_attribute)
from safe.utilities.i18n import tr


class VolcanoPointBuildingFunctionMetadata(ImpactFunctionMetadata):
    """Metadata for VolcanoPointBuildingFunctionMetadata.

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
            'id': 'VolcanoPointBuildingFunction',
            'name': tr('Point volcano on buildings'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'AIFDR',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of volcano points on buildings.'),
            'detailed_description': '',
            'hazard_input': tr(
                'The hazard layer must be a point layer. '
                'This point will be buffered with the radii specified in '
                'the parameters as the hazard zone. If you want to see '
                'the name of the volcano in the result, you need to '
                'specify the volcano name attribute in the Impact Function '
                'option.'),
            'exposure_input': tr(
                'Vector polygon layer extracted from OSM where each '
                'polygon represents the footprint of a building.'),
            'output': tr(
                'Vector layer contains Map of building exposed to '
                'volcanic hazard zones for each  radius.'),
            'actions': tr(
                'Provide details about how many building would likely be '
                'affected by each hazard zones.'),
            'limitations': [],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_volcano],
                    'units': [unit_volcano_categorical],
                    'layer_constraints': [
                        layer_vector_point
                    ]
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
                # The list of radii in km for volcano point hazard
                ('distances', distance()),
                # The attribute for name of the volcano in hazard layer
                ('volcano name attribute', volcano_name_attribute())
            ])
        }
        return dict_meta
