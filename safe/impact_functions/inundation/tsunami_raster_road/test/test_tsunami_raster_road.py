# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Tsunami Raster Building Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'etiennetrimaille'
__project_name__ = 'inasafe-dev'
__filename__ = 'test_tsunami_raster_road.py'
__date__ = '11/03/16'
__copyright__ = 'etienne@kartoza.com'


import unittest
from collections import OrderedDict
from qgis.core import (
    QgsFeatureRequest,
    QgsField,
    QgsRasterLayer,
    QgsRectangle,
    QgsVectorLayer
)
from PyQt4.QtCore import QVariant

from safe.test.utilities import get_qgis_app, test_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
# noinspection PyProtectedMember
from safe.impact_functions.inundation.tsunami_raster_road\
    .impact_function import (
        TsunamiRasterRoadsFunction,
        _raster_to_vector_cells,
        _intersect_lines_with_vector_cells)
from safe.gis.qgis_vector_tools import create_layer


class TsunamiRasterRoadsFunctionTest(unittest.TestCase):
    """Test for Tsunami Raster Road Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(TsunamiRasterRoadsFunction)

    def test_run(self):
        """Test the tsunami on roads IF"""
        impact_function = TsunamiRasterRoadsFunction.instance()

        hazard_path = test_data_path('hazard', 'tsunami_wgs84.tif')
        exposure_path = test_data_path('exposure', 'roads.shp')
        hazard_layer = QgsRasterLayer(hazard_path, 'Tsunami')
        exposure_layer = QgsVectorLayer(exposure_path, 'Roads', 'ogr')

        impact_function.hazard = hazard_layer
        impact_function.exposure = exposure_layer

        # Let's set the extent to the hazard extent
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]
        impact_function.requested_extent = rect_extent
        impact_function.run()
        impact_layer = impact_function.impact

        # Extract calculated result
        impact_data = impact_layer.get_data()

        self.assertEqual(len(impact_data), 3968)

        # 1 = inundated, 2 = wet, 3 = dry
        expected_result = {
            0: 3606,
            1: 88,
            2: 107,
            3: 114,
            4: 53
        }

        result = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0
        }
        for feature in impact_data:
            inundated_status = feature[impact_function.target_field]
            result[inundated_status] += 1

        message = 'Expecting %s, but it returns %s' % (expected_result, result)
        self.assertEqual(expected_result, result, message)

    def test_filter(self):
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'tsunami',
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
            TsunamiRasterRoadsFunction)
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
            'tsunami_wgs84.tif')
        exposure_name = test_data_path(
            'exposure',
            'roads_osm_4326.shp')

        raster = QgsRasterLayer(raster_name, 'Flood')
        exposure = QgsVectorLayer(exposure_name, 'Exposure', 'ogr')

        ranges = OrderedDict()
        ranges[0] = [0, 1]
        ranges[1] = [1, 2]
        ranges[2] = [2, 100]
        index, flood_cells_map = _raster_to_vector_cells(
            raster, ranges, exposure.crs())

        self.assertEqual(len(flood_cells_map), 4198)
        rect_with_all_cells = raster.extent()
        rect_with_4_cells = QgsRectangle(106.824, -6.177, 106.825, -6.179)
        rect_with_0_cells = QgsRectangle(106.818, -6.168, 106.828, -6.175)
        self.assertEqual(len(index.intersects(rect_with_all_cells)), 4198)
        self.assertEqual(len(index.intersects(rect_with_4_cells)), 43)
        self.assertEqual(len(index.intersects(rect_with_0_cells)), 504)

        layer = create_layer(exposure)
        new_field = QgsField('flooded', QVariant.Int)
        layer.dataProvider().addAttributes([new_field])

        request = QgsFeatureRequest()
        _intersect_lines_with_vector_cells(
            exposure, request, index, flood_cells_map, layer, 'flooded')

        feature_count = layer.featureCount()
        self.assertEqual(feature_count, 388)

        flooded = 0
        iterator = layer.getFeatures()
        for feature in iterator:
            attributes = feature.attributes()
            if attributes[3] == 1:
                flooded += 1
        self.assertEqual(flooded, 40)
