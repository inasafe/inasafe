# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
)

from safe.common.exceptions import KeywordNotFoundError
from safe.gisv4.vector.tools import create_memory_layer
from safe.definitionsv4.processing import reproject_vector


def reproject(layer, output_crs, callback=None):
    """
    Reproject a vector layer to a specific CRS.

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
    output_layer_name = reproject_vector['output_layer_name']
    processing_step = reproject_vector['step_name']

    input_crs = layer.crs()
    input_fields = layer.fields()
    feature_count = layer.featureCount()

    reprojected = create_memory_layer(
        output_layer_name, layer.geometryType(), output_crs, input_fields)
    data_provider = reprojected.dataProvider()

    crs_transform = QgsCoordinateTransform(input_crs, output_crs)

    out_feature = QgsFeature()

    for i, feature in enumerate(layer.getFeatures()):
        geom = feature.geometry()
        geom.transform(crs_transform)
        out_feature.setGeometry(geom)
        out_feature.setAttributes(feature.attributes())
        data_provider.addFeatures([out_feature])

        if callback:
            callback(current=i, maximum=feature_count, step=processing_step)

    # We transfer keywords to the output.
    # We don't need to update keywords as the CRS is dynamic.
    try:
        reprojected.keywords = layer.keywords
    except KeywordNotFoundError:
        pass

    return reprojected
