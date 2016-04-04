# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact function Test Cases.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '11/12/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.generic.classified_polygon_building.impact_function\
    import ClassifiedPolygonHazardBuildingFunction
from safe.storage.safe_layer import SafeLayer
from safe.test.utilities import get_qgis_app, test_data_path
from qgis.core import QgsVectorLayer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestClassifiedPolygonBuildingFunction(unittest.TestCase):
    """Test for Generic Polygon on Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ClassifiedPolygonHazardBuildingFunction)

    def test_run(self):
        """TestGenericPolygonBuildingFunction: Test running the IF."""
        generic_polygon_path = test_data_path(
            'hazard', 'classified_generic_polygon.shp')
        building_path = test_data_path('exposure', 'buildings.shp')

        hazard_layer = QgsVectorLayer(generic_polygon_path, 'Hazard', 'ogr')
        exposure_layer = QgsVectorLayer(building_path, 'Buildings', 'ogr')

        # Let's set the extent to the hazard extent
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]

        impact_function = ClassifiedPolygonHazardBuildingFunction.instance()
        impact_function.hazard = SafeLayer(hazard_layer)
        impact_function.exposure = SafeLayer(exposure_layer)
        impact_function.requested_extent = rect_extent
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = ('In each of the hazard zones how many buildings '
                             'might be affected.')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)

        zone_sum = impact_layer.get_data(
            attribute=impact_function.target_field)
        high_zone_count = zone_sum.count('High Hazard Zone')
        medium_zone_count = zone_sum.count('Medium Hazard Zone')
        low_zone_count = zone_sum.count('Low Hazard Zone')
        # The result
        expected_high_count = 11
        expected_medium_count = 161
        expected_low_count = 2
        message = 'Expecting %s for High Hazard Zone, but it returns %s' % (
            high_zone_count, expected_high_count)
        self.assertEqual(high_zone_count, expected_high_count, message)

        message = 'Expecting %s for Medium Hazard Zone, but it returns %s' % (
            expected_medium_count, medium_zone_count)
        self.assertEqual(medium_zone_count, expected_medium_count, message)

        message = 'Expecting %s for Low Hazard Zone, but it returns %s' % (
            expected_low_count, low_zone_count)
        self.assertEqual(expected_low_count, low_zone_count, message)

    def test_run_point_exposure(self):
        """Run the IF for point exposure.

        See https://github.com/AIFDR/inasafe/issues/2156.
        """
        generic_polygon_path = test_data_path(
            'hazard', 'classified_generic_polygon.shp')
        building_path = test_data_path('exposure', 'building-points.shp')

        hazard_layer = QgsVectorLayer(generic_polygon_path, 'Hazard', 'ogr')
        exposure_layer = QgsVectorLayer(building_path, 'Buildings', 'ogr')

        # Let's set the extent to the hazard extent
        extent = hazard_layer.extent()
        rect_extent = [
            extent.xMinimum(), extent.yMaximum(),
            extent.xMaximum(), extent.yMinimum()]

        impact_function = ClassifiedPolygonHazardBuildingFunction.instance()
        impact_function.hazard = SafeLayer(hazard_layer)
        impact_function.exposure = SafeLayer(exposure_layer)
        impact_function.requested_extent = rect_extent
        impact_function.run()
        impact_layer = impact_function.impact

        # Check the question
        expected_question = ('In each of the hazard zones how many buildings '
                             'might be affected.')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)

        zone_sum = impact_layer.get_data(
            attribute=impact_function.target_field)
        high_zone_count = zone_sum.count('High Hazard Zone')
        medium_zone_count = zone_sum.count('Medium Hazard Zone')
        low_zone_count = zone_sum.count('Low Hazard Zone')
        # The result
        expected_high_count = 12
        expected_medium_count = 172
        expected_low_count = 3
        message = 'Expecting %s for High Hazard Zone, but it returns %s' % (
            high_zone_count, expected_high_count)
        self.assertEqual(high_zone_count, expected_high_count, message)

        message = 'Expecting %s for Medium Hazard Zone, but it returns %s' % (
            expected_medium_count, medium_zone_count)
        self.assertEqual(medium_zone_count, expected_medium_count, message)

        message = 'Expecting %s for Low Hazard Zone, but it returns %s' % (
            expected_low_count, low_zone_count)
        self.assertEqual(expected_low_count, low_zone_count, message)

    def test_filter(self):
        """TestGenericPolygonBuildingFunction: Test filtering IF"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'hazard': 'flood',
            'hazard_category': 'multiple_event',
            'vector_hazard_classification': 'generic_vector_hazard_classes'
        }

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'exposure': 'structure',
            }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            ClassifiedPolygonHazardBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
