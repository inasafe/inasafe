# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Flood Population Evacuation Raster Impact Function.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'
__date__ = '20/03/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from safe.test.utilities import get_qgis_app, test_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager \
    import ImpactFunctionManager
from safe.impact_functions.inundation.flood_raster_population.impact_function\
    import FloodEvacuationRasterHazardFunction
from safe.common.utilities import OrderedDict
from safe.storage.safe_layer import SafeLayer


class TestFloodEvacuationFunctionRasterHazard(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodEvacuationRasterHazardFunction)

    def test_run(self):
        function = FloodEvacuationRasterHazardFunction.instance()

        hazard_path = test_data_path('hazard', 'continuous_flood_20_20.asc')
        exposure_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        function.parameters['thresholds'].value = [0.5, 0.7, 1.0]
        function.hazard = SafeLayer(hazard_layer)
        function.exposure = SafeLayer(exposure_layer)
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # print "keywords", keywords
        keywords = impact.get_keywords()
        evacuated = float(keywords['evacuated'])
        total_needs_full = keywords['total_needs']
        total_needs_weekly = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['weekly']
        ])
        total_needs_single = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['single']
        ])

        expected_evacuated = 100
        self.assertEqual(evacuated, expected_evacuated)
        self.assertEqual(total_needs_weekly['Rice [kg]'], 280)
        self.assertEqual(total_needs_weekly['Family Kits'], 20)
        self.assertEqual(total_needs_weekly['Drinking Water [l]'], 1750)
        self.assertEqual(total_needs_weekly['Clean Water [l]'], 6700)
        self.assertEqual(total_needs_single['Toilets'], 5)

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
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'exposure': 'population',
            'exposure_unit': 'count'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            FloodEvacuationRasterHazardFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
