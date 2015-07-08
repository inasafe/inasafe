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
from PyQt4.QtCore import QVariant
from qgis.core import (
    QGis,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsSnappingUtils,
    QgsTolerance,
    QgsSnapper)
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException
from processing.core.parameters import (
    ParameterVector,
    ParameterBoolean,
    ParameterSelection,
    ParameterNumber)
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri
from processing.tools import vector

from safe.utilities.resources import resources_path


class SnapPoints(GeoAlgorithm):
    """Snap a point layer according to a bunch of settings."""

    POINTS = 'POINTS'
    LAYER = 'LAYER'
    SNAP_TYPE = 'SNAP_TYPE'
    TOLERANCE = 'TOLERANCE'
    INTERSECTIONS = 'INTERSECTIONS'
    UNIT = 'UNIT'
    SNAPPED = 'SNAPPED'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        """Setting algorithm parameters."""
        self.name = 'Snap points to a layer (needs review)'
        self.group = 'Other geometry tools'

        self.addParameter(ParameterVector(
            self.POINTS,
            'Points to snap',
            [ParameterVector.VECTOR_TYPE_POINT],
            False))

        self.addParameter(ParameterVector(
            self.LAYER,
            'Snap on',
            [ParameterVector.VECTOR_TYPE_ANY],
            False))

        self.addParameter(ParameterSelection(
            self.SNAP_TYPE,
            'Type',
            ['Snap to vertex',
             'Snap to segment',
             'Snap to vertex and segment']))

        self.addParameter(ParameterNumber(
            self.TOLERANCE,
            'Tolerance',
            minValue=0,
            default=0))

        self.addParameter(ParameterSelection(
            self.UNIT,
            'Unit',
            ['Layer units', 'Pixels', 'Project units']))

        self.addParameter(ParameterBoolean(
            self.INTERSECTIONS,
            'Snap to intersections',
            False))

        self.addParameter(ParameterBoolean(
            self.SNAPPED,
            'Add an attribute if it has been snapped',
            False))

        self.addOutput(OutputVector(self.OUTPUT, 'Snapped'))

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
        points_layer = self.getParameterValue(self.POINTS)
        points_layer = getObjectFromUri(points_layer)
        destination_layer = self.getParameterValue(self.LAYER)
        destination_layer = getObjectFromUri(destination_layer)
        tolerance = self.getParameterValue(self.TOLERANCE)
        snap_type = self.getParameterValue(self.SNAP_TYPE)
        intersections = self.getParameterValue(self.INTERSECTIONS)
        unit_label = self.getParameterValue(self.UNIT)

        print unit_label
        if unit_label == 'Layer units':
            unit = QgsTolerance.LayerUnits
        elif unit_label == 'Pixels':
            unit = QgsTolerance.Pixels
        elif unit_label == 'Project units':
            unit = QgsTolerance.ProjectUnits
        else:
            raise GeoAlgorithmExecutionException('Unit not found')

        if snap_type == 'Snap to vertex':
            snapping_type = QgsSnapper.SnapToVertex
        elif snap_type == 'Snap to segment':
            snapping_type = QgsSnapper.SnapToSegment
        elif snap_type == 'Snap to vertex and segment':
            snapping_type = QgsSnapper.SnapToVertexAndSegment
        else:
            raise GeoAlgorithmExecutionException('Snapping type not found')

        add_attribute = self.getParameterValue(self.SNAPPED)

        fields = points_layer.dataProvider().fields()
        if add_attribute:
            fields.append(QgsField('snapped', QVariant.String))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            fields,
            QGis.WKBPoint,
            points_layer.crs())

        layer_config = QgsSnappingUtils.LayerConfig(
            destination_layer, snapping_type, tolerance, unit)

        snapper = QgsSnappingUtils()
        snapper.setLayers([layer_config])
        snapper.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
        snapper.setSnapOnIntersections(intersections)

        selection = vector.features(points_layer)
        current = 0
        total = 100.0 / float(len(selection))

        for feature in selection:
            f = QgsFeature()
            attributes = feature.attributes()
            result = snapper.snapToMap(feature.geometry().asPoint())
            if result.type() == 2:
                # noinspection PyArgumentList
                f.setGeometry(QgsGeometry.fromPoint(result.point()))
                if add_attribute:
                    attributes.append('True')
            else:
                f.setGeometry(feature.geometry())
                if add_attribute:
                    attributes.append('False')
            f.setAttributes(attributes)
            writer.addFeature(f)

            current += 1
            progress.setPercentage(int(current * total))

        del writer
