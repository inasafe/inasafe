# coding=utf-8

"""Reproject a vector layer to a specific CRS."""

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
)

from safe.definitions.processing_steps import reproject_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import create_memory_layer
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def reproject(layer, output_crs, callback=None):
    """Reproject a vector layer to a specific CRS.

    Issue https://github.com/inasafe/inasafe/issues/3183

    :param layer: The layer to reproject.
    :type layer: QgsVectorLayer

    :param output_crs: The destination CRS.
    :type output_crs: QgsCoordinateReferenceSystem

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = reproject_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']
    processing_step = reproject_steps['step_name']

    input_crs = layer.crs()
    input_fields = layer.fields()
    feature_count = layer.featureCount()

    reprojected = create_memory_layer(
        output_layer_name, layer.geometryType(), output_crs, input_fields)
    reprojected.startEditing()

    crs_transform = QgsCoordinateTransform(input_crs, output_crs)

    out_feature = QgsFeature()

    for i, feature in enumerate(layer.getFeatures()):
        geom = feature.geometry()
        geom.transform(crs_transform)
        out_feature.setGeometry(geom)
        out_feature.setAttributes(feature.attributes())
        reprojected.addFeature(out_feature)

        if callback:
            callback(current=i, maximum=feature_count, step=processing_step)

    reprojected.commitChanges()

    # We transfer keywords to the output.
    # We don't need to update keywords as the CRS is dynamic.
    reprojected.keywords = layer.keywords
    reprojected.keywords['title'] = output_layer_name
    check_layer(reprojected)
    return reprojected
