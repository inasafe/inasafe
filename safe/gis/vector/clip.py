# coding=utf-8

"""Clip and mask a hazard layer."""

import processing

from safe.common.exceptions import ProcessingInstallationError
from safe.definitions.processing_steps import clip_steps
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


@profile
def clip(layer_to_clip, mask_layer):
    """Clip a vector layer with another.

    Issue https://github.com/inasafe/inasafe/issues/3186

    :param layer_to_clip: The vector layer to clip.
    :type layer_to_clip: QgsVectorLayer

    :param mask_layer: The vector layer to use for clipping.
    :type mask_layer: QgsVectorLayer

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = clip_steps['output_layer_name']
    output_layer_name = output_layer_name % (
        layer_to_clip.keywords['layer_purpose'])

    parameters = {'INPUT': layer_to_clip,
                  'OVERLAY': mask_layer,
                  'OUTPUT': 'memory:'}

    # TODO implement callback through QgsProcessingFeedback object

    initialize_processing()

    feedback = create_processing_feedback()
    context = create_processing_context(feedback=feedback)
    result = processing.run('native:clip', parameters, context=context)
    if result is None:
        raise ProcessingInstallationError

    clipped = result['OUTPUT']

    clipped.keywords = layer_to_clip.keywords.copy()
    clipped.keywords['title'] = output_layer_name
    check_layer(clipped)
    return clipped
