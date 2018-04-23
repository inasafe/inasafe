# coding=utf-8

"""Recompute counts."""

import logging

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitions.fields import (
    size_field,
    count_fields,
)
from safe.definitions.processing_steps import (
    recompute_counts_steps)
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import SizeCalculator
from safe.processors.post_processor_functions import size
from safe.utilities.profiling import profile

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def recompute_counts(layer):
    """Recompute counts according to the size field and the new size.

    This function will also take care of updating the size field. The size
    post processor won't run after this function again.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The layer with updated counts.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = recompute_counts_steps['output_layer_name']

    fields = layer.keywords['inasafe_fields']

    if size_field['key'] not in fields:
        # noinspection PyTypeChecker
        msg = '%s not found in %s' % (
            size_field['key'], layer.keywords['title'])
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    indexes = []
    absolute_field_keys = [f['key'] for f in count_fields]
    for field, field_name in list(fields.items()):
        if field in absolute_field_keys and field != size_field['key']:
            indexes.append(layer.fieldNameIndex(field_name))
            LOGGER.info(
                'We detected the count {field_name}, we will recompute the '
                'count according to the new size.'.format(
                    field_name=field_name))

    if not len(indexes):
        msg = 'Absolute field not found in the layer %s' % (
            layer.keywords['title'])
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    size_field_name = fields[size_field['key']]
    size_field_index = layer.fieldNameIndex(size_field_name)

    layer.startEditing()

    exposure_key = layer.keywords['exposure_keywords']['exposure']
    size_calculator = SizeCalculator(
        layer.crs(), layer.geometryType(), exposure_key)

    for feature in layer.getFeatures():
        old_size = feature[size_field_name]
        new_size = size(
            size_calculator=size_calculator, geometry=feature.geometry())

        layer.changeAttributeValue(feature.id(), size_field_index, new_size)

        # Cross multiplication for each field
        for index in indexes:
            old_count = feature[index]
            try:
                new_value = new_size * old_count / old_size
            except TypeError:
                new_value = ''
            except ZeroDivisionError:
                new_value = 0
            layer.changeAttributeValue(feature.id(), index, new_value)

    layer.commitChanges()

    layer.keywords['title'] = output_layer_name

    check_layer(layer)
    return layer
