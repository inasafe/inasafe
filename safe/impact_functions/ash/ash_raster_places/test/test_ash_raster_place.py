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

__author__ = 'etienne'
__project_name__ = 'inasafe-dev'
__filename__ = 'test_ash_raster_place.py'
__date__ = '7/13/16'
__copyright__ = 'etienne@kartoza.com'


import unittest
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer
)
from safe.test.utilities import get_qgis_app, standard_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_functions.ash.ash_raster_places.impact_function import \
    AshRasterPlacesFunction


class TsunamiRasterBuildingFunctionTest(unittest.TestCase):
    """Test for Tsunami Raster Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(AshRasterPlacesFunction)

    def test_run_without_population_field(self):
        impact_function = AshRasterPlacesFunction.instance()

        hazard_path = standard_data_path('hazard', 'ash_raster_wgs84.tif')
        exposure_path = standard_data_path('exposure', 'places.shp')
        hazard_layer = QgsRasterLayer(hazard_path, 'Ash')
        exposure_layer = QgsVectorLayer(exposure_path, 'Places', 'ogr')
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

        # 1 = inundated, 2 = wet, 3 = dry
        expected_result = {
            0: 0,
            1: 0,
            2: 197,
            3: 1,
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
        self.assertDictEqual(expected_result, result)

    def test_keywords(self):
        """Test filtering IF from layer keywords"""

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'layer_geometry': 'point',
            'exposure': 'place',
            'exposure_unit': 'count'
        }

        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'volcanic_ash',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'centimetres'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
