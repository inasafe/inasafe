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
from safe.impact_functions.earthquake.pager_earthquake_fatality_model\
    .impact_function import PAGFatalityFunction
from safe.test.utilities import test_data_path, get_qgis_app, clip_layers
from safe.storage.core import read_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestPagerEarthquakeFatalityFunction(unittest.TestCase):
    """Test for Pager Earthquake on Population Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(PAGFatalityFunction)

    def test_run(self):
        """TestPagerEarthquakeFatalityFunction: Test running the IF."""
        eq_path = test_data_path('hazard', 'earthquake.tif')
        population_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')

        # For EQ on Pops we need to clip the hazard and exposure first to the
        #  same dimension
        clipped_hazard, clipped_exposure = clip_layers(eq_path,
                                                       population_path)

        # noinspection PyUnresolvedReferences
        eq_layer = read_layer(
            str(clipped_hazard.source()))
        # noinspection PyUnresolvedReferences
        population_layer = read_layer(
            str(clipped_exposure.source()))

        impact_function = PAGFatalityFunction.instance()
        impact_function.hazard = eq_layer
        impact_function.exposure = population_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = ('In the event of earthquake how many '
                             'population might die or be displaced according '
                             'pager model')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question)
        self.assertEqual(expected_question, impact_function.question, message)

        expected_exposed_per_mmi = {
            2.0: 0,
            2.5: 0,
            3.0: 0,
            3.5: 0,
            4.0: 0,
            4.5: 0,
            5.0: 0,
            5.5: 0,
            6.5: 0,
            6.0: 0,
            7.0: 0,
            7.5: 60,
            8.0: 140,
            8.5: 0,
            9.0: 0,
            9.5: 0}
        result = impact_layer.get_keywords('exposed_per_mmi')

        message = 'Expecting %s, but it returns %s' % (
            expected_exposed_per_mmi, result)
        self.assertEqual(expected_exposed_per_mmi, result, message)

    def test_filter(self):
        """TestPagerEarthquakeFatalityFunction: Test filtering IF"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'earthquake',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'mmi'
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
            PAGFatalityFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
