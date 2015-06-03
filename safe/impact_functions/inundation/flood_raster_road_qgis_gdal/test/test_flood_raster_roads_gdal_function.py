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
__project_name__ = 'inasafe'
__filename__ = 'test_flood_raster_road_qgis'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

import unittest
from qgis.core import QgsRasterLayer, QgsVectorLayer

from safe.impact_functions.inundation\
    .flood_raster_road_qgis_gdal.impact_function import \
    FloodRasterRoadsGdalFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.test.utilities import get_qgis_app, test_data_path
from safe.utilities.qgis_layer_wrapper import QgisWrapper

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodRasterRoadsGdalFunction(unittest.TestCase):
    """Test for Flood Raster Roads Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodRasterRoadsGdalFunction)

    def test_run(self):
        function = FloodRasterRoadsGdalFunction.instance()

        hazard_path = test_data_path('hazard', 'continuous_flood_20_20.asc')
        exposure_path = test_data_path('exposure', 'roads.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsRasterLayer(hazard_path, 'Flood')
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
        function.run()
        impact = function.impact

        keywords = impact.get_keywords()
        self.assertEquals(function.target_field, keywords['target_field'])
        expected_inundated_feature = 182
        count = sum(impact.get_data(attribute=function.target_field))
        self.assertEquals(count, expected_inundated_feature)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'flood',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'metres'
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
            FloodRasterRoadsGdalFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
