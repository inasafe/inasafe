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
    QGis,
)

from safe.common.exceptions import (
    InvalidKeywordsForProcessingAlgorithm, NoFeaturesInExtentError)
from safe.gisv4.vector.tools import (
    create_memory_layer,
    remove_fields,
    copy_fields,
    copy_layer,
    create_field_from_definition
)
from safe.definitions.processing_steps import prepare_vector_steps
from safe.definitions.fields import (
    exposure_id_field,
    hazard_id_field,
    aggregation_id_field,
    exposure_type_field,
    exposure_class_field,
    count_fields,
)
from safe.definitions.exposure import indivisible_exposure
from safe.definitions.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_aggregation
)
from safe.definitions.utilities import (
    get_fields,
    definition,
    get_compulsory_fields,
)
from safe.impact_function.postprocessors import run_single_post_processor
from safe.definitions.post_processors import post_processor_size
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
    output_layer_name = prepare_vector_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']
    processing_step = prepare_vector_steps['step_name']

    if not layer.keywords.get('inasafe_fields'):
        msg = 'inasafe_fields is missing in keywords from %s' % layer.name()
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    feature_count = layer.featureCount()

    cleaned = create_memory_layer(
        output_layer_name, layer.geometryType(), layer.crs(), layer.fields())

    # We transfer keywords to the output.
    cleaned.keywords = layer.keywords

    copy_layer(layer, cleaned)
    _remove_features(cleaned)

    # After removing rows, let's check if there is still a feature.
    request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
    iterator = cleaned.getFeatures(request)
    try:
        next(iterator)
    except StopIteration:
        raise NoFeaturesInExtentError

    _add_id_column(cleaned)
    _rename_remove_inasafe_fields(cleaned)

    if _size_is_needed(cleaned):
        run_single_post_processor(cleaned, post_processor_size)

    if cleaned.keywords['layer_purpose'] == 'exposure':
        fields = cleaned.keywords['inasafe_fields']
        if exposure_type_field['key'] not in fields:
            _add_default_exposure_class(cleaned)

        # Check value mapping
        _check_value_mapping(cleaned)

    cleaned.keywords['title'] = output_layer_name

    return cleaned


@profile
def _check_value_mapping(layer):
    """Loop over the exposure type field and check if the value map is correct.

    :param layer: The layer
    :type layer: QgsVectorLayer
    """
    index = layer.fieldNameIndex(exposure_type_field['field_name'])
    unique_exposure = layer.uniqueValues(index)
    value_map = layer.keywords.get('value_map')

    if not value_map:
        # The exposure do not have a value_map, we can skip the layer.
        return layer

    classification = layer.keywords['classification']
    exposure_classification = definition(classification)
    other = exposure_classification['classes'][-1]['key']

    exposure_mapped = []
    for group in value_map.itervalues():
        exposure_mapped.extend(group)

    diff = list(set(unique_exposure) - set(exposure_mapped))

    if other in value_map.keys():
        value_map[other].extend(diff)
    else:
        value_map[other] = diff

    layer.keywords['value_map'] = value_map
    return layer


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
    new_keywords = {}
    for key, val in layer.keywords.get('inasafe_fields').iteritems():
        if expected_fields[key] != val:
            to_rename[val] = expected_fields[key]
            new_keywords[key] = expected_fields[key]

    copy_fields(layer, to_rename)
    to_remove = to_rename.keys()

    LOGGER.debug(tr(
        'Fields which have been renamed from %s : %s'
        % (layer.keywords['layer_purpose'], to_rename)))

    # Houra, InaSAFE keywords match our concepts !
    layer.keywords['inasafe_fields'].update(new_keywords)

    # Remove useless fields
    for field in layer.fields().toList():
        if field.name() not in expected_fields.values():
            to_remove.append(field.name())
    remove_fields(layer, to_remove)
    LOGGER.debug(tr(
        'Fields which have been removed from %s : %s'
        % (layer.keywords['layer_purpose'], to_remove)))


def _size_is_needed(layer):
    """Checker if we need the size field.

     :param layer: The layer to test.
     :type layer: QgsVectorLayer

     :return: If we need the size field.
     :rtype: bool
    """

    exposure = layer.keywords.get('exposure')
    if not exposure:
        # The layer is not an exposure.
        return False

    indivisible_exposure_keys = [f['key'] for f in indivisible_exposure]
    if exposure in indivisible_exposure_keys:
        # The exposure is not divisible, We don't need to compute the size.
        return False

    if layer.geometryType() == QGis.Point:
        # The exposure is a point layer. We don't need to compute the size.
        return False

    # The layer is divisible and not a point layer.
    # We need to check if some fields are absolute.

    fields = layer.keywords['inasafe_fields']

    absolute_field_keys = [f['key'] for f in count_fields]

    for field in fields:
        if field in absolute_field_keys:
            return True
    else:
        return False


@profile
def _remove_features(layer):
    """Remove features which do not have information for InaSAFE or an invalid
    geometry.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer
    """
    # Get the layer purpose of the layer.
    layer_purpose = layer.keywords['layer_purpose']
    layer_subcategory = layer.keywords.get(layer_purpose)

    compulsory_field = get_compulsory_fields(layer_purpose, layer_subcategory)

    inasafe_fields = layer.keywords['inasafe_fields']
    field_name = inasafe_fields.get(compulsory_field['key'])
    if not field_name:
        msg = 'Keyword %s is missing from %s' % (
            compulsory_field['key'], layer_purpose)
        raise InvalidKeywordsForProcessingAlgorithm(msg)
    index = layer.fieldNameIndex(field_name)

    request = QgsFeatureRequest()
    request.setSubsetOfAttributes([field_name], layer.pendingFields())
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures(request):
        if isinstance(feature.attributes()[index], QPyNullVariant):
            if layer_purpose == 'hazard':
                # Remove the feature if the hazard is null.
                layer.deleteFeature(feature.id())
                i += 1
            elif layer_purpose == 'aggregation':
                # Put the ID if the value is null.
                layer.changeAttributeValue(
                    feature.id(), index, str(feature.id()))
            elif layer_purpose == 'exposure':
                # Put an empty value, the value mapping will take care of it
                # in the 'other' group.
                layer.changeAttributeValue(
                    feature.id(), index, '')

        # Check if there is en empty geometry.
        geometry = feature.geometry()
        if not geometry:
            layer.deleteFeature(feature.id())
            i += 1
            continue

        # Check if the geometry is empty.
        if geometry.isGeosEmpty():
            layer.deleteFeature(feature.id())
            i += 1
            continue

        # Check if the geometry is valid.
        if not geometry.isGeosValid():
            # polygonize can produce some invalid geometries
            # For instance a polygon like this, sharing a same point :
            #      _______
            #      |  ___|__
            #      |  |__|  |
            #      |________|
            # layer.deleteFeature(feature.id())
            # i += 1
            pass

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
        if isinstance(safe_id['type'], list):
            # Use the first element in the list of type
            id_field.setType(safe_id['type'][0])
        else:
            id_field.setType(safe_id['type'][0])
        id_field.setPrecision(safe_id['precision'])
        id_field.setLength(safe_id['length'])

        layer.addAttribute(id_field)

        new_index = layer.fieldNameIndex(id_field.name())

        for feature in layer.getFeatures():
            layer.changeAttributeValue(
                feature.id(), new_index, feature.id())

        layer.commitChanges()

        layer.keywords['inasafe_fields'][safe_id['key']] = (
            safe_id['field_name'])


@profile
def _add_default_exposure_class(layer):
    """The layer doesn't have an exposure class, we need to add it.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer
    """
    layer.startEditing()

    field = create_field_from_definition(exposure_class_field)
    layer.keywords['inasafe_fields'][exposure_class_field['key']] = (
        exposure_class_field['field_name'])
    layer.addAttribute(field)

    index = layer.fieldNameIndex(exposure_class_field['field_name'])

    exposure = layer.keywords['exposure']

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for feature in layer.getFeatures(request):
        layer.changeAttributeValue(feature.id(), index, exposure)

    layer.commitChanges()
    return
