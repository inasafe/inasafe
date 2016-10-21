# coding=utf-8

"""
Prepare layers for InaSAFE.
"""
import logging
from PyQt4.QtCore import QPyNullVariant
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeatureRequest,
)

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.gisv4.vector.tools import (
    create_memory_layer, remove_fields, copy_fields, copy_layer)
from safe.definitionsv4.processing import prepare_vector
from safe.definitionsv4.fields import (
    exposure_id_field,
    hazard_id_field,
    aggregation_id_field,
    exposure_type_field,
    hazard_value_field,
    aggregation_name_field,
    exposure_fields,
    hazard_fields,
    aggregation_fields,
    exposure_type_field
)
from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_aggregation
)
from safe.definitionsv4.utilities import get_fields
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
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
    cleaned.keywords = layer.keywords

    copy_layer(layer, cleaned)
    _remove_rows(cleaned)
    _add_id_column(cleaned)
    _rename_remove_inasafe_fields(cleaned)

    return cleaned


@profile
def _rename_remove_inasafe_fields(layer):
    """Loop over fields and rename fields which are used in InaSAFE.

    :param layer: The layer
    :type layer: QgsVectorLayer
    """

    # Exposure
    if layer.keywords['layer_purpose'] == layer_purpose_exposure['key']:
        fields = get_fields(
            layer.keywords['layer_purpose'], layer.keywords['exposure'])

    # Hazard
    elif layer.keywords['layer_purpose'] == layer_purpose_hazard['key']:
        fields = get_fields(
            layer.keywords['layer_purpose'], layer.keywords['hazard'])

    # Aggregation
    elif layer.keywords['layer_purpose'] == layer_purpose_aggregation['key']:
        fields = get_fields(
            layer.keywords['layer_purpose'])



    expected_fields = {field['key']: field['field_name'] for field in fields}

    # Rename fields
    to_rename = {}
    for key, val in layer.keywords.get('inasafe_fields').iteritems():
        if expected_fields[key] != val:
            to_rename[val] = expected_fields[key]

    copy_fields(layer, to_rename)
    remove_fields(layer, to_rename.keys())

    LOGGER.debug(tr(
        'Fields which have been renamed from %s : %s'
        % (layer.keywords['layer_purpose'], to_rename)))

    # Houra, InaSAFE keywords match our concepts !
    layer.keywords['inasafe_fields'].update(expected_fields)

    # Remove useless fields
    to_remove = []
    for field in layer.fields().toList():
        if field.name() not in expected_fields.values():
            to_remove.append(field.name())
    remove_fields(layer, to_remove)
    LOGGER.debug(tr(
        'Fields which have been removed from %s : %s'
        % (layer.keywords['layer_purpose'], to_remove)))


@profile
def _remove_rows(layer):
    """Remove rows which do not have information for InaSAFE.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer
    """
    # Get the layer purpose of the layer.
    layer_purpose = layer.keywords['layer_purpose']

    mapping = {
        layer_purpose_exposure['key']: exposure_type_field,
        layer_purpose_hazard['key']: hazard_value_field,
        layer_purpose_aggregation['key']: aggregation_name_field
    }

    for layer_type, field in mapping.iteritems():
        if layer_purpose == layer_type:
            compulsory_field = field['key']
            break

    inasafe_fields = layer.keywords['inasafe_fields']
    field_name = inasafe_fields.get(compulsory_field)
    if not field_name:
        msg = 'Keyword %s is missing from %s' % (
            compulsory_field, layer_purpose)
        raise InvalidKeywordsForProcessingAlgorithm(msg)
    index = layer.fieldNameIndex(field_name)

    request = QgsFeatureRequest()
    request.setSubsetOfAttributes([field_name], layer.pendingFields())
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures(request):
        if isinstance(feature.attributes()[index], QPyNullVariant):
            layer.deleteFeature(feature.id())
            i += 1
        # TODO We need to add more tests
        # like checking if the value is in the value_mapping.
    layer.commitChanges()
    LOGGER.debug(tr(
        'Features which have been removed from %s : %s'
        % (layer.keywords['layer_purpose'], i)))


@profile
def _add_id_column(layer):
    """Add an ID column if it's not present in the attribute table.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer
    """
    layer_purpose = layer.keywords['layer_purpose']
    mapping = {
        layer_purpose_exposure['key']: exposure_id_field,
        layer_purpose_hazard['key']: hazard_id_field,
        layer_purpose_aggregation['key']: aggregation_id_field
    }

    has_id_column = False
    for layer_type, field in mapping.iteritems():
        if layer_purpose == layer_type:
            safe_id = field
            if layer.keywords.get(field['key']):
                has_id_column = True
            break

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

        layer.keywords[safe_id['key']] = safe_id['field_name']
