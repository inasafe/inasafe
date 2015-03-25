# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Flood Vector Building Impact Function.**

Contact : ole.moller.nielsen@gmail.com

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

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_functions.inundation.flood_vector_building_impact_qgis\
    .impact_function import FloodPolygonBuildingQgisFunction
from safe.test.utilities import (
    TESTDATA,
    get_qgis_app,
    clone_shp_layer,
    test_data_path)
from safe.utilities.qgis_layer_wrapper import QgisWrapper

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodPolygonBuildingQgis(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodPolygonBuildingQgisFunction)

    def test_run(self):
        function = FloodPolygonBuildingQgisFunction.instance()

        building = 'buildings_osm_4326'
        flood_data = 'multipart_polygons_osm_4326'

        hazard_filename = test_data_path('hazard', flood_data)
        exposure_filename = test_data_path('exposure', building)
        hazard_layer = clone_shp_layer(
            name=hazard_filename,
            include_keywords=True,
            source_directory=TESTDATA)
        exposure_layer = clone_shp_layer(
            name=exposure_filename,
            include_keywords=True,
            source_directory=TESTDATA)

        # Let's set the extent to the hazard extent
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]

        function.hazard = QgisWrapper(hazard_layer)
        function.exposure = QgisWrapper(exposure_layer)
        function.requested_extent = rect_extent
        function.parameters['building_type_field'] = 'TYPE'
        function.parameters['affected_field'] = 'FLOODPRONE'
        function.parameters['affected_value'] = 'YES'
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # total flooded = 68, total buildings = 250
        count = sum(impact.get_data(attribute='INUNDATED'))
        self.assertEquals(count, 68)
        count = len(impact.get_data())
        self.assertEquals(count, 250)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'wetdry',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        exposure_keywords = {
            'subcategory': 'structure',
            'units': 'building_type',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('FloodPolygonBuildingQgis',
                         retrieved_IF,
                         'Expecting FloodPolygonBuildingQgis.'
                         'But got %s instead' %
                         retrieved_IF)
