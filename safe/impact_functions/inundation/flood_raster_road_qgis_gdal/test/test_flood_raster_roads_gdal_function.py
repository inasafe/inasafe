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
from safe.impact_functions.inundation.flood_raster_road_qgis_gdal.impact_function import \
    FloodRasterRoadsGdalFunction

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'test_flood_raster_road_qgis'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.test.utilities import TESTDATA, get_qgis_app, clone_shp_layer, \
    test_data_path, clone_raster_layer
from safe.utilities.qgis_layer_wrapper import QgisWrapper

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

class TestFloodRasterRoadsGdalFunction(unittest.TestCase):
    """Test for Flood Raster Roads Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodRasterRoadsGdalFunction)

    def test_run(self):
        function = FloodRasterRoadsGdalFunction.instance()

        hazard_name = test_data_path('hazard', 'jakarta_flood_design')
        qgis_hazard = clone_raster_layer(
            name=hazard_name,
            extension='.tif',
            include_keywords=True,
            source_directory=TESTDATA)

        exposure_name = test_data_path('exposure', 'roads_osm_4326')
        qgis_exposure = clone_shp_layer(
            name=exposure_name,
            include_keywords=True,
            source_directory=TESTDATA)

        # Let's set the extent to the hazard extent
        extent = qgis_hazard.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]
        function.hazard = QgisWrapper(qgis_hazard)
        function.exposure = QgisWrapper(qgis_exposure)
        function.extent = rect_extent
        function.parameters['road_type_field'] = 'TYPE'
        function.parameters['min threshold [m]'] = 0.005
        function.parameters['max threshold [m]'] = float('inf')
        function.run()
        impact = function.impact

        keywords = impact.get_keywords()
        self.assertEquals('flooded', keywords['target_field'])
        count = sum(impact.get_data(attribute=keywords['target_field']))
        self.assertEquals(count, 25)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'metres_depth',
            'layer_type': 'raster',
            'data_type': 'continuous'
        }

        exposure_keywords = {
            'subcategory': 'road',
            'unit': 'road_type',
            'layer_type': 'vector',
            'data_type': 'line'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('FloodRasterRoadsGdalFunction',
                         retrieved_IF,
                         'Expecting FloodRasterRoadsGdalFunction.'
                         'But got %s instead' %
                         retrieved_IF)
