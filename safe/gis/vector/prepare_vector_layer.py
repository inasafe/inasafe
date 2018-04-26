# coding=utf-8

"""Prepare layers for InaSAFE."""


import logging

from qgis.core import (
    QgsField,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsExpressionContext,
    QgsExpression
)

from safe.common.exceptions import (
    InvalidKeywordsForProcessingAlgorithm)
from safe.definitions.exposure import indivisible_exposure
from safe.definitions.exposure_classifications import data_driven_classes
from safe.definitions.fields import (
    exposure_id_field,
    hazard_id_field,
    aggregation_id_field,
    exposure_type_field,
    exposure_class_field,
    count_fields,
    displaced_field
)
from safe.definitions.layer_purposes import (
    layer_purpose_exposure,
    layer_purpose_hazard,
    layer_purpose_aggregation
)
from safe.definitions.processing_steps import prepare_vector_steps
from safe.definitions.utilities import (
    get_fields,
    definition,
    get_compulsory_fields,
)
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import (
    create_memory_layer,
    remove_fields,
    copy_fields,
    copy_layer,
    create_field_from_definition
)
from safe.impact_function.postprocessors import run_single_post_processor
from safe.processors import post_processor_size
from safe.utilities.i18n import tr
from safe.utilities.metadata import (
    active_thresholds_value_maps, active_classification, copy_layer_keywords)
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def prepare_vector_layer(layer, callback=None):
    """This function will prepare the layer to be used in InaSAFE :
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
    processing_step = prepare_vector_steps['step_name']  # NOQA

    if not layer.keywords.get('inasafe_fields'):
        msg = 'inasafe_fields is missing in keywords from %s' % layer.name()
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    cleaned = create_memory_layer(
        output_layer_name, layer.geometryType(), layer.crs(), layer.fields())

    # We transfer keywords to the output.
    cleaned.keywords = copy_layer_keywords(layer.keywords)

    copy_layer(layer, cleaned)
    _remove_features(cleaned)

    # After removing rows, let's check if there is still a feature.
    request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
    iterator = cleaned.getFeatures(request)
    try:
        next(iterator)
    except StopIteration:
        LOGGER.warning(
            tr('No feature has been found in the {purpose}'
                .format(purpose=layer.keywords['layer_purpose'])))
        # Realtime may have no data in the extent when doing a multiexposure
        # analysis. We still want the IF. I disabled the exception. ET 19/02/18
        # raise NoFeaturesInExtentError

    _add_id_column(cleaned)
    clean_inasafe_fields(cleaned)

    if _size_is_needed(cleaned):
        LOGGER.info(
            'We noticed some counts in your exposure layer. Before to update '
            'geometries, we compute the original size for each feature.')
        run_single_post_processor(cleaned, post_processor_size)

    if cleaned.keywords['layer_purpose'] == 'exposure':
        fields = cleaned.keywords['inasafe_fields']
        if exposure_type_field['key'] not in fields:
            _add_default_exposure_class(cleaned)

        # Check value mapping
        _check_value_mapping(cleaned)

    cleaned.keywords['title'] = output_layer_name

    check_layer(cleaned)
    return cleaned


@profile
def _check_value_mapping(layer, exposure_key=None):
    """Loop over the exposure type field and check if the value map is correct.

    :param layer: The layer
    :type layer: QgsVectorLayer

    :param exposure_key: The exposure key.
    :type exposure_key: str
    """
    index = layer.fields().lookupField(exposure_type_field['field_name'])
    unique_exposure = layer.uniqueValues(index)
    if layer.keywords['layer_purpose'] == layer_purpose_hazard['key']:
        if not exposure_key:
            message = tr('Hazard value mapping missing exposure key.')
            raise InvalidKeywordsForProcessingAlgorithm(message)
        value_map = active_thresholds_value_maps(layer.keywords, exposure_key)
    else:
        value_map = layer.keywords.get('value_map')

    if not value_map:
        # The exposure do not have a value_map, we can skip the layer.
        return layer

    if layer.keywords['layer_purpose'] == layer_purpose_hazard['key']:
        if not exposure_key:
            message = tr('Hazard classification is missing exposure key.')
            raise InvalidKeywordsForProcessingAlgorithm(message)
        classification = active_classification(layer.keywords, exposure_key)
    else:
        classification = layer.keywords['classification']

    exposure_classification = definition(classification)

    other = None
    if exposure_classification['key'] != data_driven_classes['key']:
        other = exposure_classification['classes'][-1]['key']

    exposure_mapped = []
    for group in list(value_map.values()):
        exposure_mapped.extend(group)

    diff = list(set(unique_exposure) - set(exposure_mapped))

    if other in list(value_map.keys()):
        value_map[other].extend(diff)
    else:
        value_map[other] = diff

    layer.keywords['value_map'] = value_map
    layer.keywords['classification'] = classification
    return layer


@profile
def clean_inasafe_fields(layer):
    """Clean inasafe_fields based on keywords.

    1. Must use standard field names.
    2. Sum up list of fields' value and put in the standard field name.
    3. Remove un-used fields.

    :param layer: The layer
    :type layer: QgsVectorLayer
    """
    fields = []
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

    # Add displaced_field definition to expected_fields
    # for minimum needs calculator.
    # If there is no displaced_field keyword, then pass
    try:
        if layer.keywords['inasafe_fields'][displaced_field['key']]:
            fields.append(displaced_field)
    except KeyError:
        pass

    expected_fields = {field['key']: field['field_name'] for field in fields}

    # Convert the field name and sum up if needed
    new_keywords = {}
    for key, val in list(layer.keywords.get('inasafe_fields').items()):
        if key in expected_fields:
            if isinstance(val, str):
                val = [val]
            sum_fields(layer, key, val)
            new_keywords[key] = expected_fields[key]

    # Houra, InaSAFE keywords match our concepts !
    layer.keywords['inasafe_fields'].update(new_keywords)

    to_remove = []
    # Remove unnecessary fields (the one that is not in the inasafe_fields)
    for field in layer.fields().toList():
        if field.name() not in list(layer.keywords['inasafe_fields'].values()):
            to_remove.append(field.name())
    remove_fields(layer, to_remove)
    LOGGER.debug(
        'Fields which have been removed from %s : %s'
        % (layer.keywords['layer_purpose'], ' '.join(to_remove)))


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

    if layer.geometryType() == QgsWkbTypes.PointGeometry:
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
    # Compulsory fields can be list of field name or single field name.
    # We need to iterate through all of them
    field_names = inasafe_fields.get(compulsory_field['key'])
    if not isinstance(field_names, list):
        field_names = [field_names]
    for field_name in field_names:
        if not field_name:
            message = 'Keyword %s is missing from %s' % (
                compulsory_field['key'], layer_purpose)
            raise InvalidKeywordsForProcessingAlgorithm(message)
        index = layer.fields().lookupField(field_name)

        request = QgsFeatureRequest()
        request.setSubsetOfAttributes([field_name], layer.fields())
        layer.startEditing()
        i = 0
        for feature in layer.getFeatures(request):
            if feature.attributes()[index] is None:
                if layer_purpose == 'hazard':
                    # Remove the feature if the hazard is null.
                    layer.deleteFeature(feature.id())
                    i += 1
                elif layer_purpose == 'aggregation':
                    # Put the ID if the value is null.
                    layer.changeAttributeValue(
                        feature.id(), index, str(feature.id()))
                elif layer_purpose == 'exposure':
                    # Put an empty value, the value mapping will take care of
                    # it in the 'other' group.
                    layer.changeAttributeValue(
                        feature.id(), index, '')

            # Check if there is en empty geometry.
            geometry = feature.geometry()
            if not geometry:
                layer.deleteFeature(feature.id())
                i += 1
                continue

            # Check if the geometry is empty.
            if geometry.isEmpty():
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
    for layer_type, field in list(mapping.items()):
        if layer_purpose == layer_type:
            safe_id = field
            if layer.keywords['inasafe_fields'].get(field['key']):
                has_id_column = True
            break

    if not has_id_column:
        LOGGER.info(
            'We add an ID column in {purpose}'.format(purpose=layer_purpose))

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

        new_index = layer.fields().lookupField(id_field.name())

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

    index = layer.fields().lookupField(exposure_class_field['field_name'])

    exposure = layer.keywords['exposure']

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for feature in layer.getFeatures(request):
        layer.changeAttributeValue(feature.id(), index, exposure)

    layer.commitChanges()
    return


@profile
def sum_fields(layer, output_field_key, input_fields):
    """Sum the value of input_fields and put it as output_field.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param output_field_key: The output field definition key.
    :type output_field_key: basestring

    :param input_fields: List of input fields' name.
    :type input_fields: list
    """
    field_definition = definition(output_field_key)
    output_field_name = field_definition['field_name']
    # If the fields only has one element
    if len(input_fields) == 1:
        # Name is different, copy it
        if input_fields[0] != output_field_name:
            to_rename = {input_fields[0]: output_field_name}
            # We copy only, it will be deleted later.
            # We can't rename the field, we need to copy it as the same
            # field might be used many times in the FMT tool.
            copy_fields(layer, to_rename)
        else:
            # Name is same, do nothing
            return
    else:
        # Creating expression
        # Put field name in a double quote. See #4248
        input_fields = ['"%s"' % f for f in input_fields]
        string_expression = ' + '.join(input_fields)
        sum_expression = QgsExpression(string_expression)
        context = QgsExpressionContext()
        context.setFields(layer.fields())
        sum_expression.prepare(context)

        # Get the output field index
        output_idx = layer.fields().lookupField(output_field_name)
        # Output index is not found
        if output_idx == -1:
            output_field = create_field_from_definition(field_definition)
            layer.startEditing()
            layer.addAttribute(output_field)
            layer.commitChanges()
            output_idx = layer.fields().lookupField(output_field_name)

        layer.startEditing()
        # Iterate to all features
        for feature in layer.getFeatures():
            context.setFeature(feature)
            result = sum_expression.evaluate(context)
            feature[output_idx] = result
            layer.updateFeature(feature)

        layer.commitChanges()
