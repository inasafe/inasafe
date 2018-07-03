# coding=utf-8

"""Clip and mask a hazard layer."""

import logging

import processing

from qgis.core import (
    QgsFeatureRequest
)

from safe.common.exceptions import ProcessingInstallationError
from safe.definitions.fields import hazard_class_field
from safe.definitions.hazard_classifications import not_exposed_class
from safe.definitions.processing_steps import union_steps
from safe.gis.sanity_check import check_layer
from safe.utilities.profiling import profile
from safe.gis.processing_tools import (
    create_processing_context,
    create_processing_feedback,
    initialize_processing)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def union(union_a, union_b):
    """Union of two vector layers.

    Issue https://github.com/inasafe/inasafe/issues/3186

    :param union_a: The vector layer for the union.
    :type union_a: QgsVectorLayer

    :param union_b: The vector layer for the union.
    :type union_b: QgsVectorLayer

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = union_steps['output_layer_name']
    output_layer_name = output_layer_name % (
        union_a.keywords['layer_purpose'],
        union_b.keywords['layer_purpose']
    )

    keywords_union_1 = union_a.keywords
    keywords_union_2 = union_b.keywords
    inasafe_fields_union_1 = keywords_union_1['inasafe_fields']
    inasafe_fields_union_2 = keywords_union_2['inasafe_fields']
    inasafe_fields = inasafe_fields_union_1
    inasafe_fields.update(inasafe_fields_union_2)

    parameters = {'INPUT': union_a,
                  'OVERLAY': union_b,
                  'OUTPUT': 'memory:'}

    # TODO implement callback through QgsProcessingFeedback object

    initialize_processing()

    feedback = create_processing_feedback()
    context = create_processing_context(feedback=feedback)
    result = processing.run('native:union', parameters, context=context)
    if result is None:
        raise ProcessingInstallationError

    union_layer = result['OUTPUT']
    union_layer.setName(output_layer_name)

    # use to avoid modifying original source
    union_layer.keywords = dict(union_a.keywords)
    union_layer.keywords['inasafe_fields'] = inasafe_fields
    union_layer.keywords['title'] = output_layer_name
    union_layer.keywords['layer_purpose'] = 'aggregate_hazard'
    union_layer.keywords['hazard_keywords'] = keywords_union_1.copy()
    union_layer.keywords['aggregation_keywords'] = keywords_union_2.copy()

    fill_hazard_class(union_layer)

    check_layer(union_layer)
    return union_layer


@profile
def fill_hazard_class(layer):
    """We need to fill hazard class when it's empty.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The updated vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    hazard_field = layer.keywords['inasafe_fields'][hazard_class_field['key']]

    expression = '"%s" is NULL OR  "%s" = \'\'' % (hazard_field, hazard_field)
    index = layer.fields().lookupField(hazard_field)
    request = QgsFeatureRequest().setFilterExpression(expression)
    layer.startEditing()

    for feature in layer.getFeatures(request):
        layer.changeAttributeValue(
            feature.id(),
            index,
            not_exposed_class['key'])
    layer.commitChanges()

    return layer
