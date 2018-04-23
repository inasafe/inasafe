# coding=utf-8

"""Reclassify a continuous vector layer."""

from qgis.core import QgsField

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitions.fields import (
    hazard_class_field,
    hazard_value_field,
    exposure_type_field,
    exposure_class_field
)
from safe.definitions.layer_purposes import (
    layer_purpose_hazard, layer_purpose_exposure)
from safe.definitions.processing_steps import assign_inasafe_values_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import remove_fields
from safe.utilities.metadata import (
    active_thresholds_value_maps, active_classification)
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def update_value_map(layer, exposure_key=None, callback=None):
    """Assign inasafe values according to definitions for a vector layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param exposure_key: The exposure key.
    :type exposure_key: str

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The classified vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = assign_inasafe_values_steps['output_layer_name']
    processing_step = assign_inasafe_values_steps['step_name']  # NOQA
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']

    keywords = layer.keywords
    inasafe_fields = keywords['inasafe_fields']

    classification = None
    if keywords['layer_purpose'] == layer_purpose_hazard['key']:
        if not inasafe_fields.get(hazard_value_field['key']):
            raise InvalidKeywordsForProcessingAlgorithm
        old_field = hazard_value_field
        new_field = hazard_class_field
        classification = active_classification(layer.keywords, exposure_key)

    elif keywords['layer_purpose'] == layer_purpose_exposure['key']:
        if not inasafe_fields.get(exposure_type_field['key']):
            raise InvalidKeywordsForProcessingAlgorithm
        old_field = exposure_type_field
        new_field = exposure_class_field
    else:
        raise InvalidKeywordsForProcessingAlgorithm

    # It's a hazard layer
    if exposure_key:
        if not active_thresholds_value_maps(keywords, exposure_key):
            raise InvalidKeywordsForProcessingAlgorithm
        value_map = active_thresholds_value_maps(keywords, exposure_key)
    # It's exposure layer
    else:
        if not keywords.get('value_map'):
            raise InvalidKeywordsForProcessingAlgorithm
        value_map = keywords.get('value_map')

    unclassified_column = inasafe_fields[old_field['key']]
    unclassified_index = layer.fieldNameIndex(unclassified_column)

    reversed_value_map = {}
    for inasafe_class, values in list(value_map.items()):
        for val in values:
            reversed_value_map[val] = inasafe_class

    classified_field = QgsField()
    classified_field.setType(new_field['type'])
    classified_field.setName(new_field['field_name'])
    classified_field.setLength(new_field['length'])
    classified_field.setPrecision(new_field['precision'])

    layer.startEditing()
    layer.addAttribute(classified_field)

    classified_field_index = layer.fieldNameIndex(classified_field.name())

    for feature in layer.getFeatures():
        attributes = feature.attributes()
        source_value = attributes[unclassified_index]
        classified_value = reversed_value_map.get(source_value)

        if not classified_value:
            classified_value = ''

        layer.changeAttributeValue(
            feature.id(), classified_field_index, classified_value)

    layer.commitChanges()

    remove_fields(layer, [unclassified_column])

    # We transfer keywords to the output.
    # We add new class field
    inasafe_fields[new_field['key']] = new_field['field_name']

    # and we remove hazard value field
    inasafe_fields.pop(old_field['key'])

    layer.keywords = keywords
    layer.keywords['inasafe_fields'] = inasafe_fields
    if exposure_key:
        value_map_key = 'value_maps'
    else:
        value_map_key = 'value_map'
    if value_map_key in list(layer.keywords.keys()):
        layer.keywords.pop(value_map_key)
    layer.keywords['title'] = output_layer_name
    if classification:
        layer.keywords['classification'] = classification

    check_layer(layer)
    return layer
