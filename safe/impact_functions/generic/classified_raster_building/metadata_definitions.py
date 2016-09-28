# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for generic Impact
function on Building for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.definitionsv4.definitions_v3 import (
    layer_geometry_polygon,
    layer_geometry_raster,
    hazard_all,
    hazard_category_multiple_event,
    generic_raster_hazard_classes
)
from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.fields import structure_class_field
from safe.definitionsv4.exposure import exposure_structure
from safe.definitionsv4.hazard import hazard_category_single_event, \
    hazard_category_multiple_event, generic_raster_hazard_classes, hazard_all
from safe.definitionsv4.layer_geometry import layer_geometry_point, \
    layer_geometry_polygon, layer_geometry_raster
from safe.common.utilities import OrderedDict
from safe.defaults import building_type_postprocessor
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.utilities.i18n import tr

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
                'Provide details about the number of buildings that are '
                'within each hazard class.'),
            'limitations': [tr('The number of classes is three.')],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
            'legend_notes': '',
            'legend_units': tr('(Low, Medium, High)'),
            'legend_title': tr('Structure inundated status'),
            'layer_requirements': {
                'hazard': {
                    'layer_mode': layer_mode_classified,
                    'layer_geometries': [layer_geometry_raster],
                    'hazard_categories': [
                        hazard_category_single_event,
                        hazard_category_multiple_event
                    ],
                    'hazard_types': hazard_all,
                    'continuous_hazard_units': [],
                    'vector_hazard_classifications': [],
                    'raster_hazard_classifications': [
                        generic_raster_hazard_classes
                    ],
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
            # parameters
            'parameters': OrderedDict([
                ('postprocessors', OrderedDict([
                    ('BuildingType', building_type_postprocessor())
                ]))
            ])
        }
        return dict_meta
