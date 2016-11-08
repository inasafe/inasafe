# coding=utf-8

"""
Recompute counts.
"""

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    size_field,
    count_fields,
)
from safe.definitionsv4.post_processors import size
from safe.definitionsv4.processing_steps import (
    recompute_counts_steps)
from safe.utilities.profiling import profile


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def recompute_counts(layer, callback=None):
    """Recompute counts according to the size field and the new size.

    This function will also take care of updating the size field. The size
    post processor won't run after this function again.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The layer with updated counts.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = recompute_counts_steps['output_layer_name']
    processing_step = recompute_counts_steps['step_name']

    fields = layer.keywords['inasafe_fields']

    if size_field['key'] not in fields:
        # noinspection PyTypeChecker
        msg = '%s not found in %s' % (
            size_field['key'], layer.keywords['title'])
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    indexes = []
    absolute_field_keys = [f['key'] for f in count_fields]
    for field, field_name in fields.iteritems():
        if field in absolute_field_keys and field != size_field['key']:
            indexes.append(layer.fieldNameIndex(field_name))

    if not len(indexes):
        msg = 'Absolute field not found in the layer %s' % (
            layer.keywords['title'])
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    size_field_name = fields[size_field['key']]
    size_field_index = layer.fieldNameIndex(size_field_name)

    layer.startEditing()

    for feature in layer.getFeatures():
        old_size = feature[size_field_name]
        new_size = size(crs=layer.crs(), geometry=feature.geometry())

        layer.changeAttributeValue(feature.id(), size_field_index, new_size)

        # Cross multiplication for each field
        for index in indexes:
            old_count = feature[index]
            new_value = new_size * old_count / old_size
            layer.changeAttributeValue(feature.id(), index, new_value)

    layer.commitChanges()

    layer.keywords['title'] = output_layer_name

    return layer
