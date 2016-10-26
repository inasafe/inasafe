# coding=utf-8

"""
Clip and mask a hazard layer.

Issue https://github.com/inasafe/inasafe/issues/3186
"""

import logging
from qgis.core import (
    QGis,
    QgsGeometry,
    QgsFeatureRequest,
    QgsWKBTypes,
    QgsFeature,
    QgsSpatialIndex
)

from safe.utilities.i18n import tr
# from safe.definitionsv4.processing import clip_vector
from safe.gisv4.vector.tools import create_memory_layer
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def smart_clip(layer_to_clip, mask_layer, callback=None):
    """Smart clip a vector layer with another.

    :param layer_to_clip: The vector layer to clip.
    :type layer_to_clip: QgsVectorLayer

    :param mask_layer: The vector layer to use for clipping.
    :type mask_layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    # To fix
    # output_layer_name = intersection_vector['output_layer_name']
    # processing_step = intersection_vector['step_name']
    output_layer_name = 'smart_clip'
    processing_step = 'Smart Clipping'

    writer = create_memory_layer(
        output_layer_name,
        layer_to_clip.geometryType(),
        layer_to_clip.crs(),
        layer_to_clip.fields()
    )
    writer.startEditing()

    # first build up a list of clip geometries
    request = QgsFeatureRequest().setSubsetOfAttributes([])
    iterator = mask_layer.getFeatures(request)
    feature = next(iterator)
    geometries = QgsGeometry(feature.geometry())

    # use prepared geometries for faster intersection tests
    # noinspection PyArgumentList
    engine = QgsGeometry.createGeometryEngine(geometries.geometry())
    engine.prepareGeometry()

    for feature in layer_to_clip.getFeatures():

        if engine.intersects(feature.geometry().geometry()):
            out_feat = QgsFeature()
            out_feat.setGeometry(feature.geometry())
            out_feat.setAttributes(feature.attributes())
            writer.addFeature(out_feat)

    writer.commitChanges()

    writer.keywords = layer_to_clip.keywords.copy()
    return writer
