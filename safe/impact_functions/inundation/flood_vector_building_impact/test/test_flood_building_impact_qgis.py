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
from qgis.core import QgsVectorLayer
from safe.test.utilities import (
    get_qgis_app,
    standard_data_path,
    clone_shp_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_functions.inundation.flood_vector_building_impact\
    .impact_function import FloodPolygonBuildingFunction
from safe.storage.safe_layer import SafeLayer


class TestFloodPolygonBuildingFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodPolygonBuildingFunction)

    def test_run(self):
        function = FloodPolygonBuildingFunction.instance()

        hazard_path = standard_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        # exposure_path = standard_data_path('exposure', 'buildings.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        # exposure_layer = QgsVectorLayer(exposure_path, 'Buildings', 'ogr')

        exposure_layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        # Let's set the extent to the hazard extent
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]

        function.hazard = SafeLayer(hazard_layer)
        function.exposure = SafeLayer(exposure_layer)
        function.requested_extent = rect_extent
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # total flooded = 27, total buildings = 129
        count = sum(impact.get_data(attribute=function.target_field))
        self.assertEquals(count, 33)
        count = len(impact.get_data())
        self.assertEquals(count, 176)

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
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'exposure': 'structure'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            FloodPolygonBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
