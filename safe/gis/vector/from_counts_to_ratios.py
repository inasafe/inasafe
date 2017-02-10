# coding=utf-8

"""From counts to ratio."""

from safe.definitions.utilities import definition
from safe.definitions.fields import size_field, count_ratio_mapping
from safe.definitions.processing_steps import (
    recompute_counts_steps)
from safe.utilities.profiling import profile
from safe.gis.vector.tools import create_field_from_definition


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def from_counts_to_ratios(layer, callback=None):
    """Transform counts to ratios.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The layer with new ratios.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = recompute_counts_steps['output_layer_name']
    processing_step = recompute_counts_steps['step_name']

    exposure = definition(layer.keywords['exposure'])
    inasafe_fields = layer.keywords['inasafe_fields']

    layer.keywords['title'] = output_layer_name
    layer.startEditing()

    mapping = {}
    for count_field in exposure['extra_fields']:
        exists = count_field['key'] in inasafe_fields
        if count_field['key'] in count_ratio_mapping.keys() and exists:
            ratio_field = definition(count_ratio_mapping[count_field['key']])

            field = create_field_from_definition(ratio_field)
            layer.addAttribute(field)
            name = ratio_field['field_name']
            layer.keywords['inasafe_fields'][ratio_field['key']] = name
            mapping[count_field['field_name']] = layer.fieldNameIndex(name)

    if len(mapping) == 0:
        # There is not a count field. Let's skip this layer.
        layer.commitChanges()
        return layer

    size_field_name = inasafe_fields[size_field['key']]

    for feature in layer.getFeatures():
        size = feature[size_field_name]

        for count_field, index in mapping.iteritems():
            count = feature[count_field]
            try:
                new_value = count / size
            except TypeError:
                new_value = ''
            layer.changeAttributeValue(feature.id(), index, new_value)

    layer.commitChanges()
    return layer
