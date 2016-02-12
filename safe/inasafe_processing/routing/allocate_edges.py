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
from qgis.core import (
    QGis,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsField,
    QgsPoint)
from PyQt4.QtCore import QVariant
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector, ParameterTableField
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri
from processing.tools.vector import spatialindex, features

from safe.routing.core.middle import split_middle
from safe.utilities.resources import resources_path


class AllocateEdges(GeoAlgorithm):
    """Allocate an IDP to each edges."""

    LINES = 'LINES'
    POINTS = 'POINTS'
    FIELD = 'FIELD'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        """Constructor."""
        self.lines_layer = None
        self.points_layer = None
        self.idx_points = None
        GeoAlgorithm.__init__(self)

    def defineCharacteristics(self):
        """Setting algorithm parameters."""
        self.name = 'Allocate edges'
        self.group = 'Routing'

        self.addParameter(ParameterVector(
            self.LINES, 'Lines', [ParameterVector.VECTOR_TYPE_LINE], False))
        self.addParameter(ParameterVector(
            self.POINTS, 'Points', [ParameterVector.VECTOR_TYPE_POINT], False))
        self.addParameter(ParameterTableField(
            self.FIELD, self.tr('IDP ID'), self.POINTS))

        self.addOutput(OutputVector(self.OUTPUT, 'Edges'))

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
        lines_layer = self.getParameterValue(self.LINES)
        self.lines_layer = getObjectFromUri(lines_layer)
        points_layer = self.getParameterValue(self.POINTS)
        self.points_layer = getObjectFromUri(points_layer)
        field = self.getParameterValue(self.FIELD)
        index_field = self.points_layer.fieldNameIndex(field)

        fields = [QgsField(field, QVariant.Int)]

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            fields,
            QGis.WKBLineString,
            self.lines_layer.crs())

        self.idx_points = spatialindex(self.points_layer)

        selection = features(self.lines_layer)
        current = 0
        total = 100.0 / float(len(selection))

        for edge in selection:
            geometry = edge.geometry()

            # noinspection PyCallByClass
            point_start = QgsGeometry.fromPoint(
                QgsPoint(geometry.asPolyline()[0]))
            feature_start = self.nearest_exit(point_start)
            # noinspection PyCallByClass
            point_end = QgsGeometry.fromPoint(
                QgsPoint(geometry.asPolyline()[-1]))
            feature_end = self.nearest_exit(point_end)

            idp_start = feature_start.attributes()[index_field]
            idp_end = feature_end.attributes()[index_field]

            if idp_start == idp_end:
                edge.setAttributes([idp_start])
                writer.addFeature(edge)
            else:
                geom = geometry.asPolyline()
                split = split_middle(geom)
                for idp, part in zip([idp_start, idp_end], split):
                    f = QgsFeature()
                    f.setAttributes([idp])
                    new_geom = [QgsPoint(p[0], p[1]) for p in part]
                    # noinspection PyCallByClass
                    f.setGeometry(QgsGeometry.fromPolyline(new_geom))
                    writer.addFeature(f)

            current += 1
            progress.setPercentage(int(current * total))

        del writer

    def nearest_exit(self, point):
        results = self.idx_points.nearestNeighbor(point.asPoint(), 5)
        minimum = None
        feature = None

        for result in results:
            request = QgsFeatureRequest().setFilterFid(result)
            f = self.points_layer.getFeatures(request).next()
            dist = f.geometry().distance(point)
            if dist < minimum or minimum is None:
                minimum = dist
                feature = f
        return feature
