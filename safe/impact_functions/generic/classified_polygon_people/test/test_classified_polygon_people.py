# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Classified Hazard Land Cover Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from qgis.core import QgsVectorLayer

from safe.impact_functions.generic.classified_polygon_people. \
    impact_function import ClassifiedPolygonHazardPolygonPeopleFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.test.utilities import get_qgis_app, test_data_path
from safe.storage.utilities import safe_to_qgis_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestClassifiedPolygonPeopleFunction(unittest.TestCase):
    """Test for Classified Polygon People Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ClassifiedPolygonHazardPolygonPeopleFunction)

    def test_run(self):
        function = ClassifiedPolygonHazardPolygonPeopleFunction.instance()

        hazard_path = test_data_path('hazard', 'floods.shp')
        exposure_path = test_data_path('exposure', 'census.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Hazard', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Area', 'ogr')
        self.assertEqual(hazard_layer.isValid(), True)
        self.assertEqual(exposure_layer.isValid(), True)

        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.requested_extent = rect_extent
        function.run()
        impact = function.impact

        impact = safe_to_qgis_layer(impact)

        # self.assertEqual(impact.dataProvider().featureCount(), 3)
        features = {}
        for f in impact.getFeatures():
            area = f.geometry().area() * 1e8
            features[f['id']] = round(area, 1)
        expected_features = {
            1: 7552.2,
            2: 12341.9,
            3: 1779.0,
            4: 12944.1
        }
        self.assertEqual(features, expected_features)

    def test_keywords(self):

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'exposure': 'area',
            'structure_class_field': 'type',
        }

        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'hazard': 'generic',
            'hazard_category': 'single_event',
            'field': 'level',
            'vector_hazard_classification': 'generic_vector_hazard_classes',
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        function_title = ImpactFunctionManager.get_function_title(
                        impact_functions[0])
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
