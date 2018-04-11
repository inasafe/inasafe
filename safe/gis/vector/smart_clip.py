# coding=utf-8

"""Clip and mask a hazard layer."""

import logging

from qgis.core import (
    QgsGeometry,
    QgsFeatureRequest,
    QgsFeature,
)

from safe.definitions.processing_steps import smart_clip_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import create_memory_layer
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def smart_clip(
        layer_to_clip, mask_layer, check_selected_flag=False, callback=None):
    """Smart clip a vector layer with another.

    Issue https://github.com/inasafe/inasafe/issues/3186

    :param layer_to_clip: The vector layer to clip.
    :type layer_to_clip: QgsVectorLayer

    :param mask_layer: The vector layer to use for clipping.
    :type mask_layer: QgsVectorLayer

    :param check_selected_flag: If the algorithm must check the selection flag.
    Default to False.
    :type check_selected_flag: bool

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = smart_clip_steps['output_layer_name']

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

    extent = mask_layer.extent()

    request = QgsFeatureRequest()
    request.setFilterRect(extent)
    # Check for some selected features
    try:
        if layer_to_clip.use_selected_features_only:
            request.setFilterFids(layer_to_clip.selectedFeaturesIds())
    except AttributeError:
        pass
    for feature in layer_to_clip.getFeatures(request):

        if engine.intersects(feature.geometry().geometry()):
            out_feat = QgsFeature()
            out_feat.setGeometry(feature.geometry())
            out_feat.setAttributes(feature.attributes())
            writer.addFeature(out_feat)

    writer.commitChanges()

    writer.keywords = layer_to_clip.keywords.copy()
    writer.keywords['title'] = output_layer_name
    check_layer(writer)
    return writer
