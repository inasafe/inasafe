# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact function Test Cases.**

Contact : kolesov.dm@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__date__ = '11/12/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from qgis.core import QgsVectorLayer

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_polygon_roads\
    .impact_function import FloodVectorRoadsExperimentalFunction
from safe.test.utilities import (
    get_qgis_app,
    test_data_path)
from safe.utilities.qgis_layer_wrapper import QgisWrapper

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodVectorPolygonRoadsFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodVectorRoadsExperimentalFunction)

    def test_run(self):
        function = FloodVectorRoadsExperimentalFunction.instance()

        hazard_path = test_data_path('hazard', 'flood_multipart_polygons.shp')
        exposure_path = test_data_path('exposure', 'roads.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Roads', 'ogr')

        # Let's set the extent to the hazard extent
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]
        function.hazard = QgisWrapper(hazard_layer)
        function.exposure = QgisWrapper(exposure_layer)
        function.requested_extent = rect_extent
        function.parameters['affected_field'] = 'FLOODPRONE'
        function.parameters['affected_value'] = 'YES'
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # the count = 69
        expected_feature_total = 69
        count = sum(impact.get_data(attribute=function.target_field))
        message = 'Expecting %s, but it returns %s' % (
            expected_feature_total, count)
        self.assertEquals(count, expected_feature_total, message)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'hazard': 'flood',
            'hazard_category': 'single_event',
            'vector_hazard_classification': 'flood_vector_hazard_classes'
        }

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'none',
            'layer_geometry': 'line',
            'exposure': 'road'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            FloodVectorRoadsExperimentalFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
