# coding=utf-8
from safe.common.utilities import OrderedDict
from safe.definitions import hazard_definition, hazard_earthquake, unit_mmi, \
    layer_raster_continuous, exposure_definition, exposure_structure, \
    unit_building_type_type, unit_building_generic, layer_vector_polygon, \
    layer_vector_point
from safe.defaults import aggregation_categorial_postprocessor
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
            'name': tr('Earthquake Building Function'),
            'impact': tr('Be affected'),
            'title': tr('Be affected'),
            'function_type': 'old-style',
            'author': 'N/A',
            'date_implemented': 'N/A',
            'overview': tr(
                'This impact function will calculate the impact of an '
                'earthquake on buildings, reporting how many are expected '
                'to be damaged etc.'),
            'detailed_description': '',
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': '',
            'limitations': [],
            'citations': [],
            'categories': {
                'hazard': {
                    'definition': hazard_definition,
                    'subcategories': [hazard_earthquake],
                    'units': [unit_mmi],
                    'layer_constraints': [layer_raster_continuous],
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
            'parameters': OrderedDict(
                [('low_threshold', 6),
                 ('medium_threshold', 7),
                 ('high_threshold', 8),
                 ('postprocessors', OrderedDict([
                     ('AggregationCategorical',
                      aggregation_categorial_postprocessor())]))])
        }
        return dict_meta