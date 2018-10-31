# coding=utf-8

"""Some helpers about the summary calculation."""

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitions.fields import count_fields
from safe.definitions.utilities import definition
from safe.gis.vector.tools import create_field_from_definition
from safe.utilities.pivot_table import FlatTable

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def check_inputs(compulsory_fields, fields):
    """Helper function to check if the layer has every compulsory fields.

    :param compulsory_fields: List of compulsory fields.
    :type compulsory_fields: list

    :param fields: inasafe_field dictionary from the layer.
    :type fields: dict

    :raises: InvalidKeywordsForProcessingAlgorithm if the layer is not valid.
    """
    for field in compulsory_fields:
        # noinspection PyTypeChecker
        if not fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)


def create_absolute_values_structure(layer, fields):
    """Helper function to create the structure for absolute values.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param fields: List of name field on which we want to aggregate.
    :type fields: list

    :return: The data structure.
    :rtype: dict
    """
    # Let's create a structure like :
    # key is the index of the field : (flat table, definition name)
    source_fields = layer.keywords['inasafe_fields']
    absolute_fields = [field['key'] for field in count_fields]
    summaries = {}
    for field in source_fields:
        if field in absolute_fields:
            field_name = source_fields[field]
            index = layer.fields().lookupField(field_name)
            flat_table = FlatTable(*fields)
            summaries[index] = (flat_table, field)
    return summaries


def add_fields(
        layer, absolute_values, static_fields, dynamic_structure):
    """Function to add fields needed in the output layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param absolute_values: The absolute value structure.
    :type absolute_values: dict

    :param static_fields: The list of static fields to add.
    :type static_fields: list

    :param dynamic_structure: The list of dynamic fields to add to the layer.
    The list must be structured like this:
    dynamic_structure = [
        [exposure_count_field, unique_exposure]
    ]
    where "exposure_count_field" is the dynamic to field to add and
    "unique_exposure" is the list of unique values to associate with this
    dynamic field. Because dynamic_structure is a ordered list, you can add
    many dynamic fields.
    :type dynamic_structure: list
    """
    for new_dynamic_field in dynamic_structure:
        field_definition = new_dynamic_field[0]
        unique_values = new_dynamic_field[1]
        for column in unique_values:
            if (column == ''
                    or (hasattr(column, 'isNull')
                        and column.isNull())):
                column = 'NULL'
            field = create_field_from_definition(field_definition, column)
            layer.addAttribute(field)
            key = field_definition['key'] % column
            value = field_definition['field_name'] % column
            layer.keywords['inasafe_fields'][key] = value

    for static_field in static_fields:
        field = create_field_from_definition(static_field)
        layer.addAttribute(field)
        # noinspection PyTypeChecker
        layer.keywords['inasafe_fields'][static_field['key']] = (
            static_field['field_name'])

    # For each absolute values
    for absolute_field in list(absolute_values.keys()):
        field_definition = definition(absolute_values[absolute_field][1])
        field = create_field_from_definition(field_definition)
        layer.addAttribute(field)
        key = field_definition['key']
        value = field_definition['field_name']
        layer.keywords['inasafe_fields'][key] = value
