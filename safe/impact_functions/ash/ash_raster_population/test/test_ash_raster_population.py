# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Ash Raster on Population Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from safe.storage.core import read_layer
from safe.test.utilities import standard_data_path, get_qgis_app, clip_layers
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.impact_functions.ash.ash_raster_population.impact_function import \
    AshRasterPopulationFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.storage.safe_layer import SafeLayer


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'test_ash_raster_people.py'
__date__ = '7/13/16'
__copyright__ = 'imajimatika@gmail.com'


class TestAshRasterPopulationFunction(unittest.TestCase):
    """Test for Ash Raster Population Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(AshRasterPopulationFunction)

    def test_run(self):
        function = AshRasterPopulationFunction.instance()

        hazard_path = standard_data_path('hazard', 'ash_raster_wgs84.tif')
        exposure_path = standard_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')
        # We need clipping for both layers to be in the same dimension
        clipped_hazard, clipped_exposure = clip_layers(
            hazard_path, exposure_path)

        hazard_layer = read_layer(clipped_hazard.source())
        exposure_layer = read_layer(clipped_exposure.source())

        # Let's set the extent to the hazard extent
        function.hazard = SafeLayer(hazard_layer)
        function.exposure = SafeLayer(exposure_layer)
        function.run()
        impact = function.impact
        expected = [
            [u'Population in very low hazard zone', '0'],
            [u'Population in medium hazard zone',
             '1,400'],
            [u'Population in high hazard zone', '20'],
            [u'Population in very high hazard zone', '0'],
            [u'Population in low hazard zone', '8,500'],
            [u'Total affected population', '9,900'],
            [u'Unaffected population', '0'],
            [u'Total population', '9,900'],
            [u'Population needing evacuation <sup>1</sup>', '9,900']
        ]
        self.assertListEqual(
            expected, impact.impact_data['impact summary']['fields'])

    def test_keywords(self):
        """Test filtering IF from layer keywords"""

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'exposure': 'population',
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
