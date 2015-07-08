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
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector, ParameterTableField
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri
from processing.tools.vector import features

from safe.utilities.resources import resources_path


class CleaningLayer(GeoAlgorithm):
    """Cleaning a layer by removing features which ID are not in a column."""

    SOURCE_LAYER = 'LAYER_SOURCE'
    DIRTY_LAYER = 'DIRTY_LAYER'
    FIELD_SOURCE_LAYER = 'FIELD_SOURCE_LAYER'
    FIELD_DIRTY_LAYER = 'FIELD_DIRTY_LAYER'
    CLEANED = 'CLEANED'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
        """Setting algorithm parameters."""
        self.name = 'Removing unmatched features '
        self.group = 'Data management'

        self.addParameter(ParameterVector(
            self.SOURCE_LAYER,
            'Source layer',
            [ParameterVector.VECTOR_TYPE_ANY],
            False))
        self.addParameter(ParameterTableField(
            self.FIELD_SOURCE_LAYER,
            self.tr('Field ID'),
            self.SOURCE_LAYER))

        self.addParameter(ParameterVector(
            self.DIRTY_LAYER,
            'Layer to clean',
            [ParameterVector.VECTOR_TYPE_ANY],
            False))
        self.addParameter(ParameterTableField(
            self.FIELD_DIRTY_LAYER,
            self.tr('Field ID'),
            self.DIRTY_LAYER))

        self.addOutput(OutputVector(self.OUTPUT, 'Cleaned'))

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
        source_layer = self.getParameterValue(self.SOURCE_LAYER)
        source_layer = getObjectFromUri(source_layer)
        field_source_layer = self.getParameterValue(self.FIELD_SOURCE_LAYER)

        dirty_layer = self.getParameterValue(self.DIRTY_LAYER)
        dirty_layer = getObjectFromUri(dirty_layer)
        field_dirty_layer = self.getParameterValue(self.FIELD_DIRTY_LAYER)

        provider = dirty_layer.dataProvider()
        geometry = provider.geometryType()
        crs = dirty_layer.crs()
        fields = provider.fields()

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            fields, geometry, crs)

        field_source_layer_id = source_layer.fieldNameIndex(field_source_layer)
        field_dirty_layer_id = dirty_layer.fieldNameIndex(field_dirty_layer)

        list_id = []
        selection = features(source_layer)
        current = 0
        total = 100.0 / float(len(selection))

        for f in selection:
            feature_id = f.attributes()[field_source_layer_id]
            if feature_id not in list_id:
                list_id.append(feature_id)

        for f in features(dirty_layer):
            feature_id = f.attributes()[field_dirty_layer_id]
            if feature_id in list_id:
                writer.addFeature(f)

            current += 1
            progress.setPercentage(int(current * total))

        del writer
