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
        """TestClassifiedPolygonPeopleFunction: Test running the IF."""

        # 1. Initializing function with necessary data
        function = ClassifiedPolygonHazardPolygonPeopleFunction.instance()

        hazard_path = test_data_path(
                'hazard', 'classified_generic_polygon.shp')
        exposure_path = test_data_path('exposure', 'census.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Hazard', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Area', 'ogr')

        # 1.1 Asserting if the provided data are valid
        self.assertEqual(hazard_layer.isValid(), True)
        self.assertEqual(exposure_layer.isValid(), True)

        # 2.Choosing the extent to run analysis
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.requested_extent = rect_extent

        # 3. Running the analysis
        function.run()
        impact = function.impact

        impact = safe_to_qgis_layer(impact)

        # Asserting for the number of features in the impact
        # layer

        self.assertEqual(impact.dataProvider().featureCount(), 6L)

        # 4. Asserting about the results found
        features = {}
        for feature in impact.getFeatures():
            area = feature.geometry().area() * 1e8
            features[feature['id']] = round(area, 1)

        expected_features = {
            1: 2460.7,
            2: 6755.5,
            3: 948.4
        }
        self.assertEqual(features, expected_features)

    def test_keywords(self):
        """TestClassifiedPolygonPeopleFunction: Test keywords IF"""

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'continuous',
            'layer_geometry': 'polygon',
            'exposure': 'population',
            'structure_class_field': '',
            'exposure_unit': 'density'
        }

        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'hazard': 'generic',
            'hazard_category': 'multiple_event',
            'field': 'h_zone',
            'vector_hazard_classification': 'generic_vector_hazard_classes',
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
