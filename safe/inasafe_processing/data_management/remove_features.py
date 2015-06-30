# -*- coding: utf-8 -*-

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector, ParameterTableField
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri
from processing.tools.vector import spatialindex, features


class CleaningLayer(GeoAlgorithm):

    SOURCE_LAYER = 'LAYER_SOURCE'
    DIRTY_LAYER = 'DIRTY_LAYER'
    FIELD_SOURCE_LAYER = 'FIELD_SOURCE_LAYER'
    FIELD_DIRTY_LAYER = 'FIELD_DIRTY_LAYER'
    CLEANED = 'CLEANED'
    OUTPUT = 'OUTPUT'

    def defineCharacteristics(self):
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

    def processAlgorithm(self, progress):
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
        for f in features(source_layer):
            feature_id = f.attributes()[field_source_layer_id]
            if feature_id not in list_id:
                list_id.append(feature_id)

        for f in features(dirty_layer):
            feature_id = f.attributes()[field_dirty_layer_id]
            if feature_id in list_id:
                writer.addFeature(f)

        del writer
