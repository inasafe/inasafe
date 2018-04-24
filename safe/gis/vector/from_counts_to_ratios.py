# coding=utf-8

"""From counts to ratio."""

import logging

from safe.definitions import count_ratio_mapping
from safe.definitions.fields import population_count_field
from safe.definitions.layer_purposes import layer_purpose_exposure
from safe.definitions.processing_steps import (
    recompute_counts_steps)
from safe.definitions.utilities import definition, get_non_compulsory_fields
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import create_field_from_definition
from safe.utilities.profiling import profile

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def from_counts_to_ratios(layer):
    """Transform counts to ratios.

    Formula: ratio = subset count / total count

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The layer with new ratios.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = recompute_counts_steps['output_layer_name']

    exposure = definition(layer.keywords['exposure'])
    inasafe_fields = layer.keywords['inasafe_fields']

    layer.keywords['title'] = output_layer_name

    if not population_count_field['key'] in inasafe_fields:
        # There is not a population count field. Let's skip this layer.
        LOGGER.info(
            'Population count field {population_count_field} is not detected '
            'in the exposure. We will not compute a ratio from this field '
            'because the formula needs Population count field. Formula: '
            'ratio = subset count / total count.'.format(
                population_count_field=population_count_field['key']))
        return layer

    layer.startEditing()

    mapping = {}
    non_compulsory_fields = get_non_compulsory_fields(
        layer_purpose_exposure['key'], exposure['key'])
    for count_field in non_compulsory_fields:
        exists = count_field['key'] in inasafe_fields
        if count_field['key'] in list(count_ratio_mapping.keys()) and exists:
            ratio_field = definition(count_ratio_mapping[count_field['key']])

            field = create_field_from_definition(ratio_field)
            layer.addAttribute(field)
            name = ratio_field['field_name']
            layer.keywords['inasafe_fields'][ratio_field['key']] = name
            mapping[count_field['field_name']] = layer.fields().lookupField(name)
            LOGGER.info(
                'Count field {count_field} detected in the exposure, we are '
                'going to create a equivalent field {ratio_field} in the '
                'exposure layer.'.format(
                    count_field=count_field['key'],
                    ratio_field=ratio_field['key']))
        else:
            LOGGER.info(
                'Count field {count_field} not detected in the exposure. We '
                'will not compute a ratio from this field.'.format(
                    count_field=count_field['key']))

    if len(mapping) == 0:
        # There is not a subset count field. Let's skip this layer.
        layer.commitChanges()
        return layer

    for feature in layer.getFeatures():
        total_count = feature[inasafe_fields[population_count_field['key']]]

        for count_field, index in list(mapping.items()):
            count = feature[count_field]
            try:
                # For #4669, fix always get 0
                new_value = count / float(total_count)
            except TypeError:
                new_value = ''
            except ZeroDivisionError:
                new_value = 0
            layer.changeAttributeValue(feature.id(), index, new_value)

    layer.commitChanges()
    check_layer(layer)
    return layer
