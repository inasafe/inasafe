# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from PyQt4.QtGui import QIcon
from qgis.core import QGis, QgsFeature, QgsFeatureRequest, QgsGeometry

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.tools import dataobjects
from processing.tools.vector import spatialindex, features

from safe.utilities.resources import resources_path


class SplitPolygonsToLinesWithPoints(GeoAlgorithm):
    """Split a polygon layer into lines with the closest point.
    For instance this polygon and these two points:
        *       *
    |---------------\
    |               \
    |_______________\

    will give these three lines:
    |--][-------][--\
    |               \
    |_______________\
    """

    POINTS_LAYER = 'POINTS_LAYER'
    POLYGONS_LAYER = 'POLYGONS_LAYER'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        """Setting algorithm parameters."""
        self.name = 'Split polygons to lines'
        self.group = 'Geometry tools'

        self.addParameter(ParameterVector(
            self.POLYGONS_LAYER,
            self.tr('Polygons layer'),
            [ParameterVector.VECTOR_TYPE_POLYGON]))

        self.addParameter(ParameterVector(
            self.POINTS_LAYER,
            'Points layer',
            [ParameterVector.VECTOR_TYPE_POINT],
            False))

        self.addOutput(OutputVector(self.OUTPUT, self.tr('Split')))

    def getIcon(self):
        """Set the icon."""
        icon = resources_path('img', 'icons', 'icon.svg')
        return QIcon(icon)

    # pylint: disable=arguments-differ
    def processAlgorithm(self, progress):
        """Core algorithm.

        :param progress: The progress bar.
        :type progress: QProgressBar

        :raise GeoAlgorithmExecutionException
        """
        layer_poly = dataobjects.getObjectFromUri(
            self.getParameterValue(self.POLYGONS_LAYER))

        points_layer = dataobjects.getObjectFromUri(
            self.getParameterValue(self.POINTS_LAYER))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            layer_poly.pendingFields().toList(),
            QGis.WKBLineString,
            layer_poly.crs())

        polygons_spatial_index = spatialindex(layer_poly)

        # cuttings : dict QgsPoint : id
        cutting = {}
        selection = features(points_layer)
        current = 0
        total = 50.0 / float(len(selection))

        for f in selection:
            point = f.geometry().asPoint()
            results = polygons_spatial_index.nearestNeighbor(point, 5)
            minimum = None
            f_id = None
            for result in results:
                request = QgsFeatureRequest().setFilterFid(result)
                poly = layer_poly.getFeatures(request).next()
                dist = poly.geometry().distance(f.geometry())
                if dist < minimum or minimum is None:
                    minimum = dist
                    f_id = poly.id()
            cutting[point] = f_id

            current += 1
            progress.setPercentage(int(current * total))

        selection = features(layer_poly)
        current = 0
        total = 50.0 / float(len(selection))

        for f in selection:
            feature = QgsFeature()
            attributes = f.attributes()
            geometry = f.geometry()
            polyline = geometry.asPolygon()[0]

            if geometry.isMultipart() or geometry.wkbType() != QGis.WKBPolygon:
                raise GeoAlgorithmExecutionException('multigeometry')

            for ring in geometry.asPolygon()[1:]:
                ring_feature = QgsFeature()
                ring_feature.setAttributes(attributes)
                ring_feature.setGeometry(QgsGeometry.fromPolyline(ring))
                writer.addFeature(ring_feature)

            if f.id() not in cutting.values():
                feature.setGeometry(QgsGeometry.fromPolyline(polyline))
                feature.setAttributes(attributes)
                writer.addFeature(feature)
            else:

                # Getting a list of QgsPoint which will cut this polygon.
                list_point = [
                    pt for pt, pt_id in cutting.iteritems() if pt_id == f.id()]

                new_geometries = []
                for i, point in enumerate(list_point):
                    if i == 0:
                        # First loop, we need to transform the polygon to a
                        # polyline at the good vertex.
                        result = geometry.closestSegmentWithContext(point)
                        new_point = result[1]
                        index = result[2]
                        polyline.insert(index, new_point)
                        polyline.insert(index, new_point)
                        polyline.pop(0)
                        polyline = polyline[index:] + polyline[:index]
                        new_geometries.append(
                            QgsGeometry.fromPolyline(polyline))
                    else:
                        minimum = None
                        closest_geom = None
                        for geom in new_geometries:
                            dist = geom.distance(QgsGeometry.fromPoint(point))
                            if dist <= minimum or minimum is None:
                                minimum = dist
                                closest_geom = geom

                        result = closest_geom.closestSegmentWithContext(point)
                        new_point = result[1]
                        index = result[2]

                        polyline = closest_geom.asPolyline()
                        polyline.insert(index, new_point)
                        l = len(polyline)
                        temp_geometries = []
                        temp_geometries.append(
                            QgsGeometry.fromPolyline(polyline[:index + 1]))
                        temp_geometries.append(
                            QgsGeometry.fromPolyline(polyline[-(l - index):]))

                        # Deleting the old geometry which has been split
                        i = new_geometries.index(closest_geom)
                        new_geometries.pop(i)

                        for geom in temp_geometries:
                            if geom.length() > 0:
                                new_geometries.append(geom)

                for geom in new_geometries:
                    feature.setGeometry(geom)
                    feature.setAttributes(attributes)
                    writer.addFeature(feature)

            current += 1
            progress.setPercentage(int(current * total) + 50)

        del writer
