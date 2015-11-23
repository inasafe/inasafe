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
from qgis.core import QGis
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException
from processing.core.parameters import (
    ParameterVector,
    ParameterTableField,
    ParameterNumber,
    ParameterSelection)
from processing.core.outputs import OutputVector
from processing.tools.dataobjects import getObjectFromUri

from safe.routing.core.inasafe_graph import InasafeGraph
from safe.utilities.resources import resources_path


class AllocateExits(GeoAlgorithm):
    """Allocate an IDP to each exits."""

    ROADS = 'ROADS'
    TOLERANCE = 'TOLERANCE'
    STRATEGY = 'STRATEGY'
    COEFFICIENT_FIELD = 'FIELD'
    EXITS = 'EXITS'
    IDP = 'IDP'
    IDP_ID = 'IDP_ID'
    OUTPUT_EXITS = 'EXITS_LAYER'
    OUTPUT_ROUTE = 'ROUTE_LAYER'

    def __init__(self):
        """Constructor."""
        self.strategies = ['distance', 'flood']
        GeoAlgorithm.__init__(self)

    def defineCharacteristics(self):
        """Setting algorithm parameters."""
        self.name = 'Allocate exits'
        self.group = 'Routing'

        self.addParameter(ParameterVector(
            self.ROADS, 'Roads', [ParameterVector.VECTOR_TYPE_LINE], False))
        self.addParameter(ParameterNumber(
            self.TOLERANCE, 'Topology tolerance', 0, default=0.00000))
        self.addParameter(ParameterSelection(
            self.STRATEGY, 'Strategy', self.strategies))
        self.addParameter(ParameterTableField(
            self.COEFFICIENT_FIELD,
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
        self.addParameter(ParameterTableField(
            self.IDP_ID, self.tr('IDP ID'), self.IDP))

        self.addOutput(OutputVector(self.OUTPUT_EXITS, 'Exit with IDP'))
        self.addOutput(OutputVector(self.OUTPUT_ROUTE, 'Routes'))

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
        roads_layer = self.getParameterValue(self.ROADS)
        roads_layer = getObjectFromUri(roads_layer)
        index_cost_strategy = self.getParameterValue(self.STRATEGY)
        for strategy in self.strategies:
            if strategy == self.strategies[index_cost_strategy]:
                cost_strategy = strategy
                break
        else:
            cost_strategy = None

        topology_tolerance = self.getParameterValue(self.TOLERANCE)
        coefficient_field = self.getParameterValue(self.COEFFICIENT_FIELD)
        coefficient_field = roads_layer.fieldNameIndex(coefficient_field)
        idp_id_field = self.getParameterValue(self.IDP_ID)
        idp_id_field = roads_layer.fieldNameIndex(idp_id_field)
        exits_layer = self.getParameterValue(self.EXITS)
        exits_layer = getObjectFromUri(exits_layer)
        idp_layer = self.getParameterValue(self.IDP)
        idp_layer = getObjectFromUri(idp_layer)

        if coefficient_field < 0 and cost_strategy != 'distance':
            raise GeoAlgorithmExecutionException('Invalid cost and field')

        tied_points = []
        for f in idp_layer.getFeatures():
            tied_points.append(f.geometry().asPoint())
        for f in exits_layer.getFeatures():
            tied_points.append(f.geometry().asPoint())

        if coefficient_field < 0:
            graph = InasafeGraph(roads_layer, tied_points)
        else:
            graph = InasafeGraph(
                roads_layer,
                tied_points,
                topology_tolerance=topology_tolerance,
                coefficient_field_id=coefficient_field)
        memory_exit_layer, memory_route_layer = graph.allocate_exits(
            idp_layer, idp_id_field, exits_layer, cost_strategy)

        exit_layer = self.getOutputFromName(self.OUTPUT_EXITS).getVectorWriter(
            memory_exit_layer.dataProvider().fields(),
            QGis.WKBPoint,
            roads_layer.crs()
        )

        for feature in memory_exit_layer.getFeatures():
            exit_layer.addFeature(feature)

        del exit_layer

        progress.setPercentage(50)

        route_layer = self.getOutputFromName(
            self.OUTPUT_ROUTE).getVectorWriter(
                memory_route_layer.dataProvider().fields(),
                QGis.WKBMultiLineString,
                roads_layer.crs()
            )

        for feature in memory_route_layer.getFeatures():
            route_layer.addFeature(feature)

        del route_layer

        progress.setPercentage(100)
