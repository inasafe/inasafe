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
from qgis.core import QGis, QgsFeature, QgsGeometry, QgsField
from qgis.utils import iface
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector, ParameterBoolean
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri
from processing.tools import vector

from safe.utilities.resources import resources_path


class SnapPointsProject(GeoAlgorithm):
    """Snap a point layer according to the project settings."""

    POINTS = 'POINTS'
    SNAPPED = 'SNAPPED'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        """Setting algorithm parameters."""
        self.name = 'Snap points (project settings)'
        self.group = 'Other geometry tools'

        self.addParameter(ParameterVector(
            self.POINTS, 'Points', [ParameterVector.VECTOR_TYPE_POINT], False))
        self.addParameter(ParameterBoolean(
            self.SNAPPED,
            'Add an attribute if the entity has been snapped',
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

        add_attribute = self.getParameterValue(self.SNAPPED)

        fields = points_layer.dataProvider().fields()

        if add_attribute:
            fields.append(QgsField('snapped', QVariant.String))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            fields,
            QGis.WKBPoint,
            points_layer.crs())

        snapper = iface.mapCanvas().snappingUtils()

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
