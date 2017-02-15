# coding=utf-8

"""Add default values."""

import logging
from PyQt4.QtCore import QPyNullVariant

from safe.common.exceptions import (
    InvalidKeywordsForProcessingAlgorithm)
from safe.definitions.processing_steps import assign_default_values_steps
from safe.definitions.utilities import definition
from safe.gis.vector.tools import create_field_from_definition
from safe.gis.sanity_check import check_layer
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def add_default_values(layer, callback=None):
    """Add or fill default values to the layer, see #3325.

    1. It doesn't have inasafe_field and it doesn't have inasafe_default_value
        --> Do nothing.
    2. It has inasafe_field and it does not have inasafe_default_value
        --> Do nothing.
    3. It does not have inasafe_field but it has inasafe_default_value
        --> Create new field, and fill with the default value for all features
    4. It has inasafe_field and it has inasafe_default_value
        --> Replace the null value with the default one.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The vector layer with the default values.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = assign_default_values_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']
    processing_step = assign_default_values_steps['step_name']

    fields = layer.keywords.get('inasafe_fields')
    if not isinstance(fields, dict):
        msg = 'inasafe_fields is missing in keywords from %s' % layer.name()
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    defaults = layer.keywords.get('inasafe_default_values')

    if not defaults:
        # Case 1 and 2.
        LOGGER.debug(
            tr('inasafe_default_value is not present, we can not fill default '
               'values.'))
        return layer

    for default in defaults.keys():

        field = fields.get(default)
        target_field = definition(default)
        layer.startEditing()

        if not field:
            # Case 3
            LOGGER.debug(
                tr('{field} key is not present but the layer has {value} as a '
                   'default for {field}. We create the new field.'.format(
                    **{'field': target_field['key'],
                       'value': defaults[default]})))

            new_field = create_field_from_definition(target_field)

            layer.addAttribute(new_field)

            new_index = layer.fieldNameIndex(new_field.name())

            for feature in layer.getFeatures():
                layer.changeAttributeValue(
                    feature.id(), new_index, defaults[default])

            layer.keywords['inasafe_fields'][target_field['key']] = (
                target_field['field_name'])

        else:
            # Case 4
            LOGGER.debug(
                tr(
                    '{field} key is present and the layer has {value} as a '
                    'default for {field}, we should fill null values.'.format(
                        **{'field': target_field['key'],
                           'value': defaults[default]})))

            index = layer.fieldNameIndex(field)

            for feature in layer.getFeatures():
                if isinstance(feature.attributes()[index], QPyNullVariant):
                    layer.changeAttributeValue(
                        feature.id(), index, defaults[default])
                    continue
                if feature.attributes()[index] == '':
                    layer.changeAttributeValue(
                        feature.id(), index, defaults[default])
                    continue

        layer.commitChanges()
        layer.keywords['title'] = output_layer_name

    check_layer(layer)
    return layer
