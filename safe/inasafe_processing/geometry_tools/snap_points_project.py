# -*- coding: utf-8 -*-

from qgis.core import QGis, QgsFeature, QgsGeometry, QgsField
from qgis.utils import iface
from PyQt4.QtCore import QVariant
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector, ParameterBoolean
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri
from processing.tools import vector


class SnapPointsProject(GeoAlgorithm):

    POINTS = 'POINTS'
    SNAPPED = 'SNAPPED'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        self.name = "Snap points (project settings)"
        self.group = "Other geometry tools"

        self.addParameter(ParameterVector(
            self.POINTS, 'Points', [ParameterVector.VECTOR_TYPE_POINT], False))
        self.addParameter(ParameterBoolean(
            self.SNAPPED,
            'Add an attribute if the entity has been snapped',
            False))

        self.addOutput(OutputVector(self.OUTPUT, 'Snapped'))

    def processAlgorithm(self, progress):
        points_layer = self.getParameterValue(self.POINTS)
        points_layer = getObjectFromUri(points_layer)

        add_attribute = self.getParameterValue(self.SNAPPED)

        fields = points_layer.dataProvider().fields()

        if add_attribute:
            fields.append(QgsField('snapped', QVariant.String))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            fields,
            QGis.WKBPoint,
            points_layer.crs())

        snapper = iface.mapCanvas().snappingUtils()

        for feature in vector.features(points_layer):
            f = QgsFeature()
            attributes = feature.attributes()
            result = snapper.snapToMap(feature.geometry().asPoint())
            if result.type() == 2:
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
