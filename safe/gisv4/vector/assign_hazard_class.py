# coding=utf-8

"""
Reclassify a continuous vector layer.
"""

from qgis.core import QGis, QgsField

from safe.definitionsv4.fields import hazard_class_field, hazard_value_field
from safe.definitionsv4.processing import reclassify_vector
from safe.gisv4.vector.tools import remove_fields

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def assign_hazard_class(layer, callback=None):
    """Assign hazard class to a vector layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The classified vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = reclassify_vector['output_layer_name']
    processing_step = reclassify_vector['step_name']

    # This layer should have this keyword, or it's a mistake from the dev.
    hazard_keywords = layer.keywords
    inasafe_fields = hazard_keywords['inasafe_fields']
    unclassified_column = inasafe_fields[hazard_value_field['key']]

    value_map = layer.keywords['value_map']

    reversed_value_map = {}
    for hazard_class, values in value_map.iteritems():
        for val in values:
            reversed_value_map[val] = hazard_class

    unclassified_index = layer.fieldNameIndex(unclassified_column)

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
        source_value = attributes[unclassified_index]
        classified_value = reversed_value_map.get(source_value)

        if not classified_value:
            layer.deleteFeature(feature.id())
        else:
            layer.changeAttributeValue(
                feature.id(), classified_field_index, classified_value)

    layer.commitChanges()

    remove_fields(layer, [unclassified_column])

    # We transfer keywords to the output.
    inasafe_fields[hazard_class_field['key']] = (
        hazard_class_field['field_name'])

    inasafe_fields.pop(hazard_value_field['key'])

    return layer
