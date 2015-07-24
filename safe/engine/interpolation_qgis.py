# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid


.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsRectangle,
    QgsSpatialIndex
)
from PyQt4.QtCore import QVariant

from safe.gis.qgis_vector_tools import create_layer


def interpolate_polygon_polygon(source, target, wgs84_extent):
    """ Transfer values from source polygon layer to the target polygon layer.

    This method will do a spatial join: the output layer will contain all
    features from target layer, with the addition of attributes of intersecting
    feature from the source layer. If there is not intersecting source feature,
    the output layer will still contain the target feature, with null
    attributes from the source layer.

    The intersection test considers only centroids of target features
    (not the whole polygon geometry).

    If more features from source layer intersect a target feature, only
    the first intersecting source feature will be used.

    :param source: Source polygon layer
    :type source: QgsVectorLayer

    :param target: Target polygon layer
    :type target: QgsVectorLayer

    :param wgs84_extent: Requested extent for analysis, in WGS84 coordinates
    :type wgs84_extent: QgsRectangle

    :return: output layer
    :rtype: QgsVectorLayer
    """

    source_field_count = source.dataProvider().fields().count()
    target_field_count = target.dataProvider().fields().count()

    # Create new layer for writing resulting features.
    # It will contain attributes of both target and source layers
    result = create_layer(target)
    new_fields = source.dataProvider().fields().toList()
    new_fields.append(QgsField('polygon_id', QVariant.Int))
    result.dataProvider().addAttributes(new_fields)
    result.updateFields()
    result_fields = result.dataProvider().fields()

    # setup transform objects between different CRS
    crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    wgs84_to_source = QgsCoordinateTransform(crs_wgs84, source.crs())
    wgs84_to_target = QgsCoordinateTransform(crs_wgs84, target.crs())
    source_to_target = QgsCoordinateTransform(source.crs(), target.crs())

    # compute extents in CRS of layers
    source_extent = wgs84_to_source.transformBoundingBox(wgs84_extent)
    target_extent = wgs84_to_target.transformBoundingBox(wgs84_extent)

    # cache source layer (in CRS of target layer)
    source_index = QgsSpatialIndex()
    source_geometries = {}  # key = feature ID, value = QgsGeometry
    source_attributes = {}
    for f in source.getFeatures(QgsFeatureRequest(source_extent)):
        f.geometry().transform(source_to_target)
        source_index.insertFeature(f)
        source_geometries[f.id()] = QgsGeometry(f.geometry())
        source_attributes[f.id()] = f.attributes()

    # Go through all features in target layer and for each decide
    # whether it is intersected by any source feature
    result_features = []
    for f in target.getFeatures(QgsFeatureRequest(target_extent)):
        # we use just centroids of target polygons
        centroid_geometry = f.geometry().centroid()
        centroid = centroid_geometry.asPoint()
        rect = QgsRectangle(
            centroid.x(), centroid.y(),
            centroid.x(), centroid.y())
        ids = source_index.intersects(rect)

        has_matching_source = False
        for source_id in ids:
            if source_geometries[source_id].intersects(centroid_geometry):
                # we have found intersection between source and target
                f_result = QgsFeature(result_fields)
                f_result.setGeometry(f.geometry())
                for i in xrange(target_field_count):
                    f_result[i] = f[i]
                for i in xrange(source_field_count):
                    f_result[i + target_field_count] = \
                        source_attributes[source_id][i]
                f_result['polygon_id'] = source_id
                result_features.append(f_result)
                has_matching_source = True
                break   # assuming just one source for each target feature

        # if there is no intersecting feature from source layer,
        # we will keep the source attributes null
        if not has_matching_source:
            f_result = QgsFeature(result_fields)
            f_result.setGeometry(f.geometry())
            for i in xrange(target_field_count):
                f_result[i] = f[i]
            result_features.append(f_result)

        if len(result_features) == 1000:
            result.dataProvider().addFeatures(result_features)
            result_features = []

    result.dataProvider().addFeatures(result_features)
    return result
