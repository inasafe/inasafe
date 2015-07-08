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

import unittest
import logging
from types import GeneratorType, XRangeType

from safe.test.utilities import test_data_path, get_qgis_app

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

LOGGER = logging.getLogger('InaSAFE')

from qgis.core import QgsVectorLayer, QGis, QgsPoint, QgsGeometry
from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException

from safe.routing.core.graph import Graph
from safe.routing.core.multiply_properter import MultiplyProperty


class GraphTest(unittest.TestCase):

    def setUp(self):
        roads_file = test_data_path('exposure', 'network.shp')
        self.roads = QgsVectorLayer(roads_file, 'roads', 'ogr')
        self.graph = Graph(
            self.roads,
            direction_field_id=4,
            direct_direction_value='yes',
            reverse_direction_value='reverse',
            both_direction_value='both',
            default_direction=3)

    def tearDown(self):
        pass

    def test_graph(self):
        """Test generalities on the graph."""
        msg = 'The graph has not been built correctly.'
        self.assertEqual(self.graph.vertex_count(), 928, msg)
        self.assertEqual(self.graph.arc_count(), 1465, msg)
        self.assertIsInstance(self.graph.get_vertices(), GeneratorType, msg)
        self.assertIsInstance(self.graph.get_arcs(), GeneratorType, msg)
        self.assertIsInstance(self.graph.get_id_vertices(), XRangeType, msg)
        self.assertIsInstance(self.graph.get_id_arcs(), XRangeType, msg)

        arc = self.graph.get_arc(5)
        cost = arc.properties()[0]
        self.assertEqual(cost, 17.811515877232498, msg)
        self.assertRaises(
            GeoAlgorithmExecutionException, self.graph.get_arc, 2065)
        linestring = self.graph.get_arc_linestring(5)
        expected = [
            'POINT(106.80260478444803596 -6.24332985662669415)',
            'POINT(106.80272929094641654 -6.24322778815910162)']
        for i, wkt in enumerate(expected):
            self.assertEqual(linestring[i].wellKnownText(), wkt)

        # vertex = self.graph.get_vertex(900)
        # self.assertEqual(vertex.point())
        # self.assertIsInstance(vertex, QgsGraphVertex)

    def test_add_cost(self):
        """Test if we can add a cost strategy to the graph."""
        msg = 'The new cost for the graph is not correct.'
        self.assertEqual(len(self.graph.properties), 1, msg)
        self.graph.add_cost('flood', MultiplyProperty(4), False)
        self.assertEqual(len(self.graph.properties), 2, msg)
        self.graph.add_cost('flood', MultiplyProperty(4), False)
        self.assertEqual(len(self.graph.properties), 2, msg)

    def test_get_nearest_vertex_id(self):
        """Test if we can the the nearest vertex id."""

        vertex_id = 500
        self.assertEqual(
            self.graph.get_nearest_vertex_id(vertex_id), vertex_id)

        vertex = self.graph.get_vertex(vertex_id)
        self.assertEqual(
            self.graph.get_nearest_vertex_id(vertex), vertex_id)

        point = QgsPoint(106.8185416771, -6.1862835407)
        self.assertEqual(
            self.graph.get_nearest_vertex_id(point), vertex_id)

    def test_dijkstra(self):
        """Test if we can run the dijkstra algorithm."""

        self.assertRaises(
            GeoAlgorithmExecutionException, self.graph.dijkstra, 500, 'foo')

        start_vertex_id = 500
        end_vertex_id = 400
        dijkstra = self.graph.dijkstra(start_vertex_id, 'distance')
        self.assertEqual(dijkstra[0][end_vertex_id], 218)
        self.assertEqual(dijkstra[1][end_vertex_id], 984.457635409196)

    def test_cost(self):
        """Test cost method between two points."""
        start_vertex_id = 500
        end_vertex_id = 400
        cost = self.graph.cost(start_vertex_id, end_vertex_id, 'distance')
        expected = 984.457635409196
        self.assertEqual(cost, expected)

        start_vertex_id = 500
        end_vertex_id = 200
        cost = self.graph.cost(start_vertex_id, end_vertex_id, 'distance')
        expected = -1
        self.assertEqual(cost, expected)

    def test_route_geom(self):
        """Test we can compute a route and get the geometry."""
        geom = self.graph.route_geom(500, 400, 'distance')
        self.assertIsInstance(geom, QgsGeometry)
        self.assertEqual(geom.wkbType(), QGis.WKBMultiLineString)

    def test_route(self):
        """Test we can get a route and get everything."""
        route = self.graph.route(500, 400, 'distance')
        self.assertIsInstance(route, tuple)
        self.assertEqual(len(route), 3)
        self.assertIsInstance(route[0], QgsGeometry)
        self.assertIsInstance(route[1], float)
        self.assertIsInstance(route[2], float)

    def test_tarjan(self):
        """Test tarjan algorithm."""
        tarjan = self.graph.tarjan()
        self.assertEqual(len(tarjan), 262)
        self.assertEqual(len(tarjan[0]), 82)
        self.assertEqual(tarjan[0][0], 694)

    def test_deep_first_search(self):
        """Test Deep Fist Search algorithm."""
        dfs_500 = self.graph.deep_first_search(500)
        self.assertEqual(len(dfs_500), 347)

    def test_debug_arcs(self):
        """Test the debug arcs layer."""
        layer = self.graph.debug_arcs()
        provider = layer.dataProvider()
        self.assertEqual(layer.geometryType(), QGis.Line)
        expected = {
            'id_arc': 0, 'in_vertex': 2, '0_distance': 1, 'out_vertex': 3}
        self.assertDictEqual(provider.fieldNameMap(), expected)
        self.assertEqual(provider.featureCount(), 1465)

    def test_debug_vertices(self):
        """Test the debug vertices layer."""
        layer = self.graph.debug_vertices()
        provider = layer.dataProvider()
        self.assertEqual(layer.geometryType(), QGis.Point)
        expected = {
            'arcs_nb': 3, 'in_arcs_nb': 1, 'id_vertex': 0, 'out_arcs_nb': 2}
        self.assertDictEqual(provider.fieldNameMap(), expected)
        self.assertEqual(provider.featureCount(), 928)

if __name__ == '__main__':
    suite = unittest.makeSuite(GraphTest, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
