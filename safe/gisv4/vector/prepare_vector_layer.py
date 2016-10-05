# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from qgis.core import (
    QgsVectorLayer,
    QgsField,
)

from safe.common.exceptions import KeywordNotFoundError
from safe.gisv4.vector.tools import create_memory_layer, remove_fields, copy_fields, copy_layer
from safe.definitionsv4.processing import prepare_vector
from safe.definitionsv4.fields import (
    exposure_id_field,
    hazard_id_field,
    aggregation_id_field,
    exposure_fields,
    hazard_fields,
    aggregation_fields
)
from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_aggregation
)


def prepare_vector_layer(layer, callback=None):
    """
    This function will prepare the layer to be used in InaSAFE :
     * Make a local copy of the layer.
     * Make sure that we have an InaSAFE ID column.
     * Rename fields according to our definitions.
     * Remove fields which are not used.

    :param layer: The layer to prepare.
    :type layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: Cleaned memory layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = prepare_vector['output_layer_name']
    processing_step = prepare_vector['step_name']

    feature_count = layer.featureCount()

    cleaned = create_memory_layer(
        output_layer_name, layer.geometryType(), layer.crs(), layer.fields())

    # We transfer keywords to the output.
    try:
        cleaned.keywords = layer.keywords
    except KeywordNotFoundError:
        pass

    copy_layer(layer, cleaned)
    _add_id_column(cleaned)
    _rename_remove_inasafe_fields(cleaned)

    return cleaned


def _rename_remove_inasafe_fields(layer):
    """Loop over fields and rename fields which are used in InaSAFE.

    :param layer: The layer
    :type layer: QgsVectorLayer
    """

    # Exposure
    if layer.keywords['layer_purpose'] == layer_purpose_exposure['key']:
        fields = exposure_fields

    # Hazard
    elif layer.keywords['layer_purpose'] == layer_purpose_hazard['key']:
        fields = hazard_fields

    # Aggregation
    elif layer.keywords['layer_purpose'] == layer_purpose_aggregation['key']:
        fields = aggregation_fields

    expected_fields = {field['key']: field['field_name'] for field in fields}

    # Rename fields
    to_rename = {}
    for key, val in layer.keywords.get('inasafe_fields').iteritems():
        to_rename[val] = expected_fields[key]

    copy_fields(layer, to_rename)
    remove_fields(layer, to_rename.keys())

    # Houra, InaSAFE keywords match our concepts !
    layer.keywords['inasafe_fields'] = {key: key for key in to_rename.values()}

    # Remove useless fields
    to_remove = []
    for field in layer.fields().toList():
        if field.name() not in expected_fields.values():
            to_remove.append(field.name())
    remove_fields(layer, to_remove)


def _add_id_column(layer):
    """Add an ID column if it's not present in the attribute table.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer
    """
    has_id_column = False

    # Exposure
    if layer.keywords['layer_purpose'] == layer_purpose_exposure['key']:
        if layer.keywords.get(exposure_id_field['field_name']):
            has_id_column = True
        else:
            safe_id = exposure_id_field

    # Hazard
    elif layer.keywords['layer_purpose'] == layer_purpose_hazard['key']:
        if layer.keywords.get(hazard_id_field['field_name']):
            has_id_column = True
        else:
            safe_id = exposure_id_field

    # Aggregation
    elif layer.keywords['layer_purpose'] == layer_purpose_aggregation['key']:
        if layer.keywords.get(aggregation_id_field['field_name']):
            has_id_column = True
        else:
            safe_id = exposure_id_field

    if not has_id_column:

        layer.startEditing()

        id_field = QgsField()
        id_field.setName(safe_id['field_name'])
        id_field.setType(safe_id['type'])
        id_field.setPrecision(safe_id['precision'])
        id_field.setLength(safe_id['length'])

        layer.addAttribute(id_field)

        new_index = layer.fieldNameIndex(id_field.name())

        for feature in layer.getFeatures():
            layer.changeAttributeValue(
                feature.id(), new_index, feature.id())

        layer.commitChanges()
