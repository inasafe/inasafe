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
from safe.common.exceptions import ZeroImpactException

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'test_flood_raster_road'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'


import unittest

from safe.test.utilities import get_qgis_app, test_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsFeatureRequest,
    QgsField,
    QgsRasterLayer,
    QgsRectangle,
    QgsVectorLayer
)

from safe.storage.safe_layer import SafeLayer

# noinspection PyProtectedMember
from safe.impact_functions.inundation.flood_raster_road.impact_function \
    import (
        FloodRasterRoadsFunction,
        _raster_to_vector_cells,
        _intersect_lines_with_vector_cells)
from safe.gis.qgis_vector_tools import create_layer
from safe.impact_functions.impact_function_manager import ImpactFunctionManager


class TestFloodRasterRoadsFunction(unittest.TestCase):
    """Test for Flood Raster Roads Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodRasterRoadsFunction)

    def test_run(self):
        function = FloodRasterRoadsFunction.instance()

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
        function.hazard = SafeLayer(hazard_layer)
        function.exposure = SafeLayer(exposure_layer)
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
            'layer_mode': 'classified',
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
            FloodRasterRoadsFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)

    def test_raster_to_vector_and_line_intersection(self):
        """Test the core part of the analysis.

        1. Test creation of spatial index of flood cells
        2. Test intersection of flood cells with roads layer
        """

        raster_name = test_data_path(
            'hazard',
            'jakarta_flood_design.tif')
        exposure_name = test_data_path(
            'exposure',
            'roads_osm_4326.shp')

        raster = QgsRasterLayer(raster_name, 'Flood')
        exposure = QgsVectorLayer(exposure_name, 'Exposure', 'ogr')

        index, flood_cells_map = _raster_to_vector_cells(
            raster, 0.1, 1e10, exposure.crs())

        self.assertEqual(len(flood_cells_map), 221)

        rect_with_all_cells = raster.extent()
        rect_with_4_cells = QgsRectangle(106.824, -6.177, 106.825, -6.179)
        rect_with_0_cells = QgsRectangle(106.818, -6.168, 106.828, -6.175)
        self.assertEqual(len(index.intersects(rect_with_all_cells)), 221)
        self.assertEqual(len(index.intersects(rect_with_4_cells)), 4)
        self.assertEqual(len(index.intersects(rect_with_0_cells)), 0)

        layer = create_layer(exposure)
        new_field = QgsField('flooded', QVariant.Int)
        layer.dataProvider().addAttributes([new_field])

        request = QgsFeatureRequest()
        _intersect_lines_with_vector_cells(
            exposure, request, index, flood_cells_map, layer, 'flooded')

        feature_count = layer.featureCount()
        self.assertEqual(feature_count, 184)

        flooded = 0
        iterator = layer.getFeatures()
        for feature in iterator:
            attributes = feature.attributes()
            if attributes[3] == 1:
                flooded += 1
        self.assertEqual(flooded, 25)

    def test_zero_intersection(self):
        hazard_path = test_data_path(
            'hazard',
            'continuous_flood_20_20.asc')
        exposure_path = test_data_path(
            'exposure',
            'roads.shp')

        # noinspection PyCallingNonCallable
        hazard_layer = QgsRasterLayer(hazard_path, 'Flood')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Roads', 'ogr')

        # Let's set the extent to the hazard extent
        function = FloodRasterRoadsFunction.instance()
        rect_extent = [106.831991, -6.170044, 106.834868, -6.167793]
        function.hazard = SafeLayer(hazard_layer)
        function.exposure = SafeLayer(exposure_layer)
        function.requested_extent = rect_extent
        with self.assertRaises(ZeroImpactException):
            function.run()
