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

from qgis.networkanalysis import (
    QgsLineVectorLayerDirector,
    QgsGraphVertex,
    QgsDistanceArcProperter,
    QgsGraphAnalyzer,
    QgsGraphBuilder
)

from qgis.core import (
    QgsVectorLayer,
    QgsGeometry,
    QgsFeature,
    QgsPoint,
    QgsField
)

from PyQt4.QtCore import QVariant

from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException


class Graph(object):
    """Manage a graph."""

    def __init__(
            self,
            layer,
            points=None,
            direction_field_id=-1,
            direct_direction_value='',
            reverse_direction_value='',
            both_direction_value='',
            default_direction=3,
            ctf_enabled=True,
            topology_tolerance=0.0,
            ellipsoid_id='WGS84'):
        """Constructor for the graph.

        :param layer: The road layer.
        :type layer: QgsVectorLayer

        :param points: The list of points to add as tied points.
        :type points: list

        :param direction_field_id: Field containing road direction value.
        :type direction_field_id: int

        :param direct_direction_value: Value for one-way road.
        :type direct_direction_value: str

        :param reverse_direction_value: Value for reverse one-way road.
        :type reverse_direction_value: str

        :param both_direction_value: Value for road.
        :type both_direction_value: str

        :param default_direction: Default direction value (1: direct direction,
            2: reverse direction, 3: both direction)
        :type default_direction: int

        :param ctf_enabled: Enable coordinate transform from source graph.
        :type ctf_enabled: bool

        :param topology_tolerance: Tolerance between two source points.
        :type topology_tolerance: float

        :param ellipsoid_id: Ellipsoid for edge measurement. Default WGS84.
        :type ellipsoid_id: str
        """
        self.dijkstra_results = {}
        self.properties = []
        self.layer = layer
        if points is None:
            points = []
        self.points = points
        self.topology_tolerance = topology_tolerance
        self.crs = self.layer.crs()
        self.ctf_enabled = ctf_enabled
        self.ellipsoid_id = ellipsoid_id
        self.director = QgsLineVectorLayerDirector(
            layer,
            direction_field_id,
            direct_direction_value,
            reverse_direction_value,
            both_direction_value,
            default_direction)
        self.add_cost('distance', QgsDistanceArcProperter())
        self.builder = None
        self.tiedPoint = None
        self.graph = None
        self.distance_area = None
        self.build()

    # pylint: disable=pointless-string-statement
    """
    BUILDER
    """
    def build(self):
        """Build the graph."""
        self.builder = QgsGraphBuilder(
            self.crs,
            self.ctf_enabled,
            self.topology_tolerance,
            self.ellipsoid_id)
        self.tiedPoint = self.director.makeGraph(self.builder, self.points)
        self.distance_area = self.builder.distanceArea()
        self.graph = self.builder.graph()

    def add_cost(self, name, cost_strategy, build=False):
        """Add a cost strategy to the graph and give it a name.

        :param name: Unique name of the strategy.
        :type name: str

        :param cost_strategy: The cost strategy to use.
        :type cost_strategy: QgsArcProperter

        :param build: If the graph needs to be rebuilded after.
        :type build bool

        :return: Return True if the strategy has been added.
        :rtype bool
        """
        if name not in self.properties:
            self.director.addProperter(cost_strategy)
            self.properties.append(name)

            if build:
                self.build()

            return True
        else:
            return False

    # pylint: disable=pointless-string-statement
    """
    ITERATOR
    """
    def get_vertices(self):
        """Get a generator to loop over all vertices.

        :return: A list of vertices.
        :rtype: list
        """
        nb_vertices = self.graph.vertexCount()
        return (self.graph.vertex(i) for i in xrange(0, nb_vertices))

    def get_id_vertices(self):
        """Get a generator to loop over all vertices id.

        :return: A list of ids.
        :rtype: list
        """
        nb_vertices = self.graph.vertexCount()
        return xrange(0, nb_vertices)

    def get_arcs(self):
        """Get a generator to loop over all arcs.

        :return: A list of arcs.
        :rtype: list
        """
        nb_edges = self.graph.arcCount()
        return (self.graph.arc(i) for i in xrange(0, nb_edges))

    def get_id_arcs(self):
        """Get a generator to loop over all arcs id.

        :return: A list of ids.
        :rtype: list
        """
        nb_edges = self.graph.arcCount()
        return xrange(0, nb_edges)

    # pylint: disable=pointless-string-statement
    """
    ARC
    """
    def arc_count(self):
        """Get the number of arc.

        :return: The number of arc.
        :rtype: int
        """
        return self.graph.arcCount()

    def get_arc(self, id_arc):
        """Get an arc according to an id.

        :return: The arc.
        :rtype: QgsGraphArc
        """
        if id_arc < 0 or id_arc >= self.arc_count():
            msg = 'Arc %s doesn\'t exist' % id_arc
            raise GeoAlgorithmExecutionException(msg)

        return self.graph.arc(id_arc)

    def get_in_vertex_id(self, id_arc):
        """Get the incoming vertex of an arc.

        :param id_arc: The arc.
        :type id_arc: int

        :return: The vertex.
        :rtype: QgsGraphVertex
        """
        return self.get_arc(id_arc).inVertex()

    def get_out_vertex_id(self, id_arc):
        """Get the outcoming vertex of an arc.

        :param id_arc: The arc.
        :type id_arc: int

        :return: The vertex.
        :rtype: QgsGraphVertex
        """
        return self.get_arc(id_arc).outVertex()

    def get_arc_linestring(self, id_arc):
        """Get the incoming vertex of an arc.

        :param id_arc: The arc.
        :type id_arc: int

        :return: The vertex.
        :rtype: QgsGraphVertex
        """
        arc = self.get_arc(id_arc)
        point_start = self.get_vertex_point(arc.inVertex())
        point_end = self.get_vertex_point(arc.outVertex())
        linestring = [point_start, point_end]
        return linestring

    # pylint: disable=pointless-string-statement
    """
    VERTEX
    """
    def vertex_count(self):
        """Get the number of vertices.

        :return: The number of vertices.
        :rtype: int
        """
        return self.graph.vertexCount()

    def get_vertex(self, id_vertex):
        """Get a vertex according to an id.

        :return: The vertex.
        :rtype: QgsGraphVertex
        """
        if id_vertex < 0 or id_vertex >= self.vertex_count():
            msg = 'Vertex %s doesn\'t exist' % id_vertex
            raise GeoAlgorithmExecutionException(msg)

        return self.graph.vertex(id_vertex)

    def get_vertex_point(self, id_vertex):
        """Get the point of a vertex according to an id.

        :return: The point.
        :rtype: QgsPoint
        """
        return self.get_vertex(id_vertex).point()

    def get_vertices_neighbours_out(self, id_vertex):
        """Return a list of vertices which are directly connected to a vertex.

        :param id_vertex: The vertex id.
        :type id_vertex: int

        :return The list of vertices.
        :rtype list.
        """
        vertex = self.get_vertex(id_vertex)
        vertices = []
        for id_arc in vertex.outArc():
            vertices.append(self.get_in_vertex_id(id_arc))
        return vertices

    # pylint: disable=pointless-string-statement
    """
    SEARCHING VERTEX
    """
    def get_nearest_vertex_id(self, point):
        """Get the nearest vertex id.

        :param point The point.
        :type point QgsPoint or int or QgsGraphVertex.

        :return: The closest vertex id.
        :rtype: int
        """
        if isinstance(point, int):
            # Try to get vertex, an exception will be raised if the point
            # doesn't exit.
            self.get_vertex(point)
            vertex_id = point

        elif isinstance(point, QgsGraphVertex):
            vertex_id = self.graph.findVertex(point.point())

        elif isinstance(point, QgsPoint):
            vertex_id = self.graph.findVertex(point)
            if vertex_id < 0:
                vertex = self.get_nearest_vertex(point)
                vertex_id = self.graph.findVertex(vertex.point())
        else:
            raise GeoAlgorithmExecutionException('unknown type')

        return vertex_id

    def get_nearest_vertex(self, point):
        """Get the nearest vertex from a point.

        :param point The point.
        :type point QgsPoint

        :return The vertex.
        :rtype QgsGraphVertex
        """
        minimum = -1
        closest_vertex = None

        for vertex in self.get_vertices():
            dist = point.sqrDist(vertex.point())
            if dist < minimum or not closest_vertex:
                minimum = dist
                closest_vertex = vertex

        return closest_vertex

    # pylint: disable=pointless-string-statement
    """
    ROUTING
    """
    def dijkstra(self, start, cost_strategy='distance'):
        """Compute dijkstra from a start point.

        :param start The start.
        :type start QgsPoint or int or QgsGraphVertex.

        :return Dijkstra : tree, cost
        :rtype: tab
        """

        if cost_strategy not in self.properties:
            msg = 'Cost %s does not exist' % cost_strategy
            raise GeoAlgorithmExecutionException(msg)

        vertex_id = self.get_nearest_vertex_id(start)

        if vertex_id not in self.dijkstra_results.keys():
            self.dijkstra_results[vertex_id] = {}

        if cost_strategy not in self.dijkstra_results[vertex_id].keys():
            criterion = self.properties.index(cost_strategy)
            dijkstra = QgsGraphAnalyzer.dijkstra(
                self.graph, vertex_id, criterion)

            # Clean the dataset be removing infinite value.
            # tree = [-1 if x == float('inf') else x for x in dijkstra[0]]
            # cost = [-1 if x == float('inf') else x for x in dijkstra[1]]
            # dijkstra = (tree, cost)

            self.dijkstra_results[vertex_id][cost_strategy] = dijkstra

        return self.dijkstra_results[vertex_id][cost_strategy]

    def cost(self, start, end, cost_strategy='distance'):
        """Compute cost between two points.

        :type start QgsPoint or int or QgsGraphVertex
        :type end QgsPoint or int or QgsGraphVertex

        :return The cost.
        :rtype int
        """
        vertex_start_id = self.get_nearest_vertex_id(start)
        vertex_stop_id = self.get_nearest_vertex_id(end)
        _, cost = self.dijkstra(vertex_start_id, cost_strategy)
        cost = cost[vertex_stop_id]
        if cost == float('inf'):
            cost = -1
        return cost

    def route_geom(self, start, end, cost_strategy='distance'):
        """Get the route as a multilinestrings geometry between two positions.

        :param start: The start.
        :type start: QgsPoint or int or QgsGraphVertex.

        :param end: The end.
        :type end: QgsPoint or int or QgsGraphVertex.

        :param cost_strategy: The cost strategy to use.
        :type cost_strategy: str

        :return The route as a multilinestrings geometry.
        :rtype QgsGeometry
        """
        cost = self.cost(start, end, cost_strategy)
        if cost < 0:
            raise GeoAlgorithmExecutionException('Path not found')

        tree, cost = self.dijkstra(start, cost_strategy)
        vertex_start_id = self.get_nearest_vertex_id(start)
        vertex_stop_id = self.get_nearest_vertex_id(end)
        current_vertex = vertex_stop_id

        multigeometry = []
        while current_vertex != vertex_start_id:
            arc_id = tree[current_vertex]
            multigeometry.append(self.get_arc_linestring(arc_id))
            current_vertex = self.get_out_vertex_id(arc_id)

        return QgsGeometry().fromMultiPolyline(multigeometry)

    def route(self, start, end, cost_strategy='distance'):
        """Compute the route between two positions according to a strategy.

        :param start: The start.
        :type start: QgsPoint or int or QgsGraphVertex.

        :param end: The end.
        :type end: QgsPoint or int or QgsGraphVertex.

        :param cost_strategy: The cost strategy to use.
        :type cost_strategy: str

        :return A list composed of the geometry, real length and cost.
        :rtype list
        """

        geom = self.route_geom(start, end, cost_strategy)
        distance = self.distance_area.measure(geom)
        cost = self.cost(start, end, cost_strategy)
        return geom, distance, cost

    def isochrone(self, start, cost, cost_strategy='distance'):
        """Compute isochrone"""
        pass

    # pylint: disable=pointless-string-statement
    """
    ANALYSE
    """
    def tarjan(self):
        """Compute strongly connected components according to Tarjan.

        :return List of strongly connected components.
        :rtype list
        """
        class StrongConnectedComponent(object):

            def __init__(self):
                self.graph = None
                self.counter = None
                self.count = None
                self.low_link = None
                self.stack = None
                self.connected_components = None

            def strong_connect(self, head):
                low_link, count, stack = self.low_link, self.count, self.stack
                low_link[head] = count[head] = self.counter = self.counter + 1
                stack.append(head)

                for tail in self.graph.get_vertices_neighbours_out(head):
                    if tail not in count:
                        self.strong_connect(tail)
                        low_link[head] = min(low_link[head], low_link[tail])
                    elif count[tail] < count[head]:
                        if tail in self.stack:
                            low_link[head] = min(low_link[head], count[tail])

                if low_link[head] == count[head]:
                    component = []
                    while stack and count[stack[-1]] >= count[head]:
                        component.append(stack.pop())
                    self.connected_components.append(component)

            def __call__(self, graph):
                self.graph = graph
                self.counter = 0
                self.count = {}
                self.low_link = {}
                self.stack = []
                self.connected_components = []

                for id_vertex in self.graph.get_id_vertices():
                    if id_vertex not in self.count:
                        self.strong_connect(id_vertex)

                return self.connected_components

        strongly_connected_components = StrongConnectedComponent()
        return strongly_connected_components(self)

    def deep_first_search(self, vertex_id, visited=None):
        """Compute Deep Fist Search (DFS) algorithm on the graph.

        :param vertex_id: The vertex id.
        :type vertex_id: int

        :return A list of vertex id.
        :rtype list
        """
        if visited is None:
            visited = []

        visited.append(vertex_id)
        for next_vertex in self.get_vertices_neighbours_out(vertex_id):
            if next_vertex not in visited:
                self.deep_first_search(next_vertex, visited)
        return visited

    # pylint: disable=pointless-string-statement
    """
    DEBUG
    """
    def debug_vertices(self):
        """Helper to debug vertices in a graph.

        :return: The debug layer.
        :rtype: QgsVectorLayer
        """
        srs = self.crs.toWkt()
        layer = QgsVectorLayer(
            'Point?crs=' + srs, 'Debug point', 'memory')
        layer_dp = layer.dataProvider()

        layer_dp.addAttributes([
            QgsField('id_vertex', QVariant.Int),
            QgsField('in_arcs_nb', QVariant.Int),
            QgsField('out_arcs_nb', QVariant.Int),
            QgsField('arcs_nb', QVariant.Int)
        ])
        layer.updateFields()

        for id_vertex in self.get_id_vertices():
            vertex = self.get_vertex(id_vertex)

            feature = QgsFeature()
            # noinspection PyCallByClass
            geom = QgsGeometry.fromPoint(self.get_vertex_point(id_vertex))
            in_arcs_id = vertex.inArc()
            out_arcs_id = vertex.outArc()
            attributes = [
                id_vertex,
                len(in_arcs_id),
                len(out_arcs_id),
                len(in_arcs_id) + len(out_arcs_id)]
            feature.setAttributes(attributes)
            feature.setGeometry(geom)
            layer_dp.addFeatures([feature])
        layer.updateExtents()
        return layer

    def debug_arcs(self):
        """Helper to debug arcs in a graph.

        :return: The debug layer.
        :rtype: QgsVectorLayer
        """
        srs = self.crs.toWkt()
        layer = QgsVectorLayer(
            'LineString?crs=' + srs, 'Debug edges', 'memory')
        dp = layer.dataProvider()
        fields = list()
        fields.append(QgsField('id_arc', QVariant.Int))
        for i, strategy in enumerate(self.properties):
            fields.append(QgsField('%s_%s' % (i, strategy), QVariant.Double))
        fields.append(QgsField('in_vertex', QVariant.Int))
        fields.append(QgsField('out_vertex', QVariant.Int))

        dp.addAttributes(fields)
        layer.updateFields()

        for arc_id in self.get_id_arcs():
            # noinspection PyCallByClass
            geom = QgsGeometry.fromPolyline(self.get_arc_linestring(arc_id))
            arc = self.get_arc(arc_id)
            out_vertex_id = self.get_out_vertex_id(arc_id)
            in_vertex_id = self.get_in_vertex_id(arc_id)

            attributes = list()
            attributes.append(arc_id)
            attributes = attributes + arc.properties()
            attributes.append(in_vertex_id)
            attributes.append(out_vertex_id)

            feature = QgsFeature()
            feature.setAttributes(attributes)
            feature.setGeometry(geom)

            dp.addFeatures([feature])

        layer.updateExtents()
        return layer
