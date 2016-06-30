# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Classified Hazard Building Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'lucernae'
__filename__ = 'test_classified_hazard_building'
__date__ = '23/03/15'

import unittest
import math
from safe.test.utilities import standard_data_path, get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.generic.classified_raster_building\
    .impact_function import ClassifiedRasterHazardBuildingFunction
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.storage.core import read_layer
from safe.storage.safe_layer import SafeLayer


class TestClassifiedHazardBuildingFunction(unittest.TestCase):
    """Test for ClassifiedHazardPopulationImpactFunction."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ClassifiedRasterHazardBuildingFunction)

    def test_run(self):
        function = ClassifiedRasterHazardBuildingFunction.instance()

        hazard_path = standard_data_path(
            'hazard', 'classified_hazard.tif')
        exposure_path = standard_data_path('exposure', 'small_building.shp')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        function.hazard = SafeLayer(hazard_layer)
        function.exposure = SafeLayer(exposure_layer)
        function.run()
        impact_layer = function.impact
        impact_data = impact_layer.get_data()

        # Count
        expected_impact = {
            'Not affected': 10,
            'Low hazard zone': 2,
            'Medium hazard zone': 9,
            'High hazard zone': 5
        }

        result_impact = {}
        for impact_feature in impact_data:
            hazard_class = impact_feature[function.target_field]
            if hazard_class in result_impact:
                result_impact[hazard_class] += 1
            else:
                result_impact[hazard_class] = 1
        self.assertDictEqual(expected_impact, result_impact)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'raster',
            'hazard': 'flood',
            'hazard_category': 'multiple_event',
            'raster_hazard_classification': 'generic_raster_hazard_classes'
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
            ClassifiedRasterHazardBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
