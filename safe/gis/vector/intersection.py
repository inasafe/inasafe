# coding=utf-8

"""Intersect two layers."""

import logging

import processing

from safe.common.exceptions import ProcessingInstallationError
from safe.definitions.layer_purposes import layer_purpose_exposure_summary
from safe.definitions.processing_steps import intersection_steps
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
def intersection(source, mask):
    """Intersect two layers.

    Issue https://github.com/inasafe/inasafe/issues/3186

    :param source: The vector layer to clip.
    :type source: QgsVectorLayer

    :param mask: The vector layer to use for clipping.
    :type mask: QgsVectorLayer

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = intersection_steps['output_layer_name']
    output_layer_name = output_layer_name % (
        source.keywords['layer_purpose'])

    parameters = {'INPUT': source,
                  'OVERLAY': mask,
                  'OUTPUT': 'memory:'}

    # TODO implement callback through QgsProcessingFeedback object

    initialize_processing()

    feedback = create_processing_feedback()
    context = create_processing_context(feedback=feedback)
    result = processing.run('native:intersection', parameters, context=context)
    if result is None:
        raise ProcessingInstallationError

    intersect = result['OUTPUT']
    intersect.setName(output_layer_name)
    intersect.keywords = dict(source.keywords)
    intersect.keywords['title'] = output_layer_name
    intersect.keywords['layer_purpose'] = layer_purpose_exposure_summary['key']
    intersect.keywords['inasafe_fields'] = dict(source.keywords['inasafe_fields'])
    intersect.keywords['inasafe_fields'].update(mask.keywords['inasafe_fields'])
    intersect.keywords['hazard_keywords'] = dict(mask.keywords['hazard_keywords'])
    intersect.keywords['exposure_keywords'] = dict(source.keywords)
    intersect.keywords['aggregation_keywords'] = dict(
        mask.keywords['aggregation_keywords'])

    check_layer(intersect)
    return intersect
