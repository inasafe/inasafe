# -*- coding: utf-8 -*-

from qgis.utils import iface
from qgis.core import (
    QgsVectorFileWriter,
    QGis)
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException
from processing.core.parameters import (
    ParameterVector,
    ParameterTableField,
    ParameterSelection)
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri

from safe.routing.core.inasafe_graph import InasafeGraph


class AllocateExits(GeoAlgorithm):

    ROADS = 'ROADS'
    STRATEGY = 'STRATEGY'
    FIELD = 'FIELD'
    EXITS = 'EXITS'
    IDP = 'IDP'
    OUTPUT_EXITS = 'EXITS_LAYER'
    OUTPUT_ROUTE = 'ROUTE_LAYER'

    def __init__(self):
        self.strategies = ['distance', 'flood']
        GeoAlgorithm.__init__(self)

    def defineCharacteristics(self):
        self.name = 'Allocate exits'
        self.group = 'Routing'
        self.addParameter(ParameterVector(
            self.ROADS, 'Roads', [ParameterVector.VECTOR_TYPE_LINE], False))
        self.addParameter(ParameterSelection(
            self.STRATEGY, 'Strategy', self.strategies))
        self.addParameter(ParameterTableField(
            self.FIELD,
            'Coefficient field',
            self.ROADS,
            ParameterTableField.DATA_TYPE_ANY,
            optional=True))
        self.addParameter(ParameterVector(
            self.EXITS,
            'Exit layer',
            [ParameterVector.VECTOR_TYPE_POINT],
            False))
        self.addParameter(ParameterVector(
            self.IDP,
            'IDP',
            [ParameterVector.VECTOR_TYPE_POINT],
            False))

        self.addOutput(OutputVector(self.OUTPUT_EXITS, 'Exit with IDP'))
        self.addOutput(OutputVector(self.OUTPUT_ROUTE, 'Routes'))

    def processAlgorithm(self, progress):
        roads_layer = self.getParameterValue(self.ROADS)
        roads_layer = getObjectFromUri(roads_layer)
        index_cost_strategy = self.getParameterValue(self.STRATEGY)
        for strategy in self.strategies:
            if strategy == self.strategies[index_cost_strategy]:
                cost_strategy = strategy
                break
        else:
            cost_strategy = None

        field = self.getParameterValue(self.FIELD)
        field = roads_layer.fieldNameIndex(field)
        exits_layer = self.getParameterValue(self.EXITS)
        exits_layer = getObjectFromUri(exits_layer)
        idp_layer = self.getParameterValue(self.IDP)
        idp_layer = getObjectFromUri(idp_layer)

        if field < 0 and cost_strategy != 'distance':
            raise GeoAlgorithmExecutionException('Invalid cost and field')

        output_exits = self.getOutputValue(self.OUTPUT_EXITS)
        output_routes = self.getOutputValue(self.OUTPUT_ROUTE)

        tied_points = []
        for f in idp_layer.getFeatures():
            tied_points.append(f.geometry().asPoint())
        for f in exits_layer.getFeatures():
            tied_points.append(f.geometry().asPoint())

        if field < 0:
            graph = InasafeGraph(roads_layer, tied_points)
        else:
            graph = InasafeGraph(
                roads_layer, tied_points, coefficient_field_id=field)
        memory_exit_layer, memory_route_layer = graph.allocate_exits(
            idp_layer, exits_layer, cost_strategy)

        exit_layer = QgsVectorFileWriter(
            output_exits,
            None,
            memory_exit_layer.dataProvider().fields(),
            QGis.WKBPoint,
            roads_layer.crs()
        )

        for feature in memory_exit_layer.getFeatures():
            exit_layer.addFeature(feature)

        del exit_layer

        route_layer = QgsVectorFileWriter(
            output_routes,
            None,
            memory_route_layer.dataProvider().fields(),
            QGis.WKBMultiLineString,
            roads_layer.crs()
        )

        for feature in memory_route_layer.getFeatures():
            route_layer.addFeature(feature)

        del route_layer
