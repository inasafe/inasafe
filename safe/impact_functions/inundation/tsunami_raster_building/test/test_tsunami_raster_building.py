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

__author__ = 'ismailsunni'
__project_name__ = 'inasafe'
__filename__ = 'test_tsunami_raster_building'
__date__ = '12/31/15'
__copyright__ = 'imajimatika@gmail.com'


import unittest

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_functions.inundation.tsunami_raster_building\
    .impact_function import TsunamiRasterBuildingFunction
from safe.storage.core import read_layer
from safe.test.utilities import get_qgis_app, test_data_path
from safe.storage.safe_layer import SafeLayer


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TsunamiRasterBuildingFunctionTest(unittest.TestCase):
    """Test for Tsunami Raster Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(TsunamiRasterBuildingFunction)

    def test_run(self):
        impact_function = TsunamiRasterBuildingFunction.instance()

        hazard_path = test_data_path('hazard', 'continuous_flood_20_20.asc')
        exposure_path = test_data_path('exposure', 'buildings.shp')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        impact_function.hazard = SafeLayer(hazard_layer)
        impact_function.exposure = SafeLayer(exposure_layer)
        impact_function.run()
        impact_layer = impact_function.impact

        # Extract calculated result
        impact_data = impact_layer.get_data()
        self.assertEqual(len(impact_data), 181)

        # 1 = inundated, 2 = wet, 3 = dry
        expected_result = {
            0: 1,
            1: 116,
            2: 64,
            3: 0,
            4: 0
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
            TsunamiRasterBuildingFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
