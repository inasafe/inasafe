# -*- coding: utf-8 -*-

from qgis.core import QGis, QgsFeature, QgsGeometry, QgsField, QgsSnappingUtils
from PyQt4.QtCore import QVariant
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


class SnapPoints(GeoAlgorithm):

    POINTS = 'POINTS'
    LAYER = 'LAYER'
    SNAP_TYPE = 'SNAP_TYPE'
    TOLERANCE = 'TOLERANCE'
    INTERSECTIONS = 'INTERSECTIONS'
    UNIT = 'UNIT'
    SNAPPED = 'SNAPPED'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        self.name = "Snap points to a layer (needs review)"
        self.group = "Geometry tools"

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

    def processAlgorithm(self, progress):
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

        for feature in vector.features(points_layer):
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
        del writer
