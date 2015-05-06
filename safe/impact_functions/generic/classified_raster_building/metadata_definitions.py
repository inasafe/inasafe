# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for generic Impact
function on Building for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.definitions import hazard_definition, hazard_all, unit_classified, \
    layer_raster_classified, exposure_definition, exposure_structure, \
    unit_building_type_type, unit_building_generic, layer_vector_polygon, \
    layer_vector_point
from safe.impact_functions.generic.classified_hazard_building\
    .parameter_definitions import (
        low_hazard_class, medium_hazard_class, high_hazard_class)
from safe.utilities.i18n import tr

from safe.defaults import building_type_postprocessor
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'metadata_definitions'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'


class ClassifiedRasterHazardBuildingMetadata(ImpactFunctionMetadata):
    """Metadata for Classified Hazard Building Impact Function.

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
            'id': 'ClassifiedRasterHazardBuildingFunction',
            'name': tr('Classified raster hazard on buildings'),
            'impact': tr('Be impacted'),
            'title': tr('Be impacted in each hazard class'),
            'function_type': 'old-style',
            'author': 'Dianne Bencito',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of a classified hazard in raster '
                'format on a buildings vector layer.'),
            'detailed_description': tr(
                'This function will treat the values in the hazard raster '
                'layer as classes representing low, medium and high '
                'impact. You need to ensure that the keywords for the hazard '
                'layer have been set appropriately to define these classes.'
                'The number of buildings that will be impacted will be '
                'calculated for each class. The report will show the total '
                'number of buildings that will be affected for each '
                'hazard class.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents the '
                'class of the hazard. There should be 3 classes: e.g. '
                '1, 2, and 3.'),
            'exposure_input': tr(
                'A vector polygon layer which can be extracted from OSM '
                'where each polygon represents the footprint of a '
                'building.'),
            'output': tr(
                'The impact layer will contain all structures that were '
                'exposed to the highest class (3) and a summary table '
                'containing the number of structures in each class.'),
            'actions': tr(
                'Provide details about how many buildings would likely be '
                'impacted for each hazard class.'),
            'limitations': [tr('The number of classes is three.')],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': hazard_all,
                    'units': [unit_classified],
                    'layer_constraints': [layer_raster_classified]
                },
                'exposure': {
                    'definition': exposure_definition,
                    'subcategories': [exposure_structure],
                    'units': [
                        unit_building_type_type,
                        unit_building_generic],
                    'layer_constraints': [
                        layer_vector_polygon,
                        layer_vector_point
                    ]
                }
            },
            # parameters
            'parameters': OrderedDict([
                ('low_hazard_class', low_hazard_class()),
                ('medium_hazard_class', medium_hazard_class()),
                ('high_hazard_class', high_hazard_class()),
                ('postprocessors', OrderedDict([('BuildingType',
                                                building_type_postprocessor())
                                                ]))
            ])
        }
        return dict_meta
