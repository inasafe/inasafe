# coding=utf-8

"""Reclassify a continuous vector layer."""

from PyQt4.QtCore import QPyNullVariant
from qgis.core import QgsField

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitions.utilities import definition
from safe.definitions.fields import hazard_class_field, hazard_value_field
from safe.definitions.processing_steps import reclassify_vector_steps
from safe.gis.sanity_check import check_layer
from safe.utilities.metadata import (
    active_thresholds_value_maps, active_classification)
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def reclassify(layer, exposure_key=None, callback=None):
    """Reclassify a continuous vector layer.

    This function will modify the input.

    For instance if you want to reclassify like this table :
            Original Value     |   Class
            - ∞ < val <= 0     |     1
            0   < val <= 0.5   |     2
            0.5 < val <= 5     |     3
            5   < val <  + ∞   |     6

    You need a dictionary :
        ranges = OrderedDict()
        ranges[1] = [None, 0]
        ranges[2] = [0.0, 0.5]
        ranges[3] = [0.5, 5]
        ranges[6] = [5, None]

    :param layer: The raster layer.
    :type layer: QgsRasterLayer

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
    output_layer_name = reclassify_vector_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['title']
    processing_step = reclassify_vector_steps['step_name']

    # This layer should have this keyword, or it's a mistake from the dev.
    inasafe_fields = layer.keywords['inasafe_fields']
    continuous_column = inasafe_fields[hazard_value_field['key']]

    if exposure_key:
        classification_key = active_classification(
            layer.keywords, exposure_key)
        thresholds = active_thresholds_value_maps(layer.keywords, exposure_key)
        layer.keywords['thresholds'] = thresholds
        layer.keywords['classification'] = classification_key
    else:
        classification_key = layer.keywords.get('classification')
        thresholds = layer.keywords.get('thresholds')

    if not thresholds:
        raise InvalidKeywordsForProcessingAlgorithm(
            'thresholds are missing from the layer %s'
            % layer.keywords['layer_purpose'])

    continuous_index = layer.fieldNameIndex(continuous_column)

    classified_field = QgsField()
    classified_field.setType(hazard_class_field['type'])
    classified_field.setName(hazard_class_field['field_name'])
    classified_field.setLength(hazard_class_field['length'])
    classified_field.setPrecision(hazard_class_field['precision'])

    layer.startEditing()
    layer.addAttribute(classified_field)

    classified_field_index = layer.fieldNameIndex(classified_field.name())

    for feature in layer.getFeatures():
        attributes = feature.attributes()
        source_value = attributes[continuous_index]
        classified_value = _classified_value(source_value, thresholds)
        if not classified_value:
            layer.deleteFeature(feature.id())
        else:
            layer.changeAttributeValue(
                feature.id(), classified_field_index, classified_value)

    layer.commitChanges()
    layer.updateFields()

    # We transfer keywords to the output.
    inasafe_fields[hazard_class_field['key']] = (
        hazard_class_field['field_name'])

    value_map = {}

    hazard_classes = definition(classification_key)['classes']
    for hazard_class in reversed(hazard_classes):
        value_map[hazard_class['key']] = [hazard_class['value']]

    layer.keywords['value_map'] = value_map
    layer.keywords['title'] = output_layer_name

    check_layer(layer)
    return layer


def _classified_value(value, ranges):
    """This function will return the classified value.

    The algorithm will return None if the continuous value has not any class.

    :param value: The continuous value to classify.
    :type value: float

    :param ranges: Classes
    :type ranges: OrderedDict

    :return: The classified value or None.
    :rtype: float or None
    """
    if value is None or value == '' or isinstance(value, QPyNullVariant):
        return None

    for threshold_id, threshold in ranges.iteritems():
        value_min = threshold[0]
        value_max = threshold[1]

        # If, eg [0, 0], the value must be equal to 0.
        if value_min == value_max and value_max == value:
            return threshold_id

        # If, eg [None, 0], the value must be less or equal than 0.
        if value_min is None and value <= value_max:
            return threshold_id

        # If, eg [0, None], the value must be greater than 0.
        if value_max is None and value > value_min:
            return threshold_id

        # If, eg [0, 1], the value must be
        # between 0 excluded and 1 included.
        if value_min < value <= value_max:
            return threshold_id
