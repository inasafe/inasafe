# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '20/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.loader import register_impact_functions
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model \
    .impact_function import PAGFatalityFunction
from safe.impact_functions.earthquake.itb_bayesian_earthquake_fatality_model \
    .impact_function import ITBBayesianFatalityFunction

from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.definitionsv4.layer_modes import layer_mode_continuous, \
    layer_mode_classified
from safe.definitionsv4.fields import structure_class_field
from safe.definitionsv4.exposure import exposure_population, exposure_road, \
    exposure_structure, exposure_place, exposure_land_cover
from safe.definitionsv4.hazard import (
    hazard_generic,
    hazard_earthquake,
    hazard_flood,
    hazard_volcanic_ash,
    hazard_tsunami,
    hazard_volcano)
from safe.definitionsv4.hazard_category import hazard_category_single_event, \
    hazard_category_multiple_event
from safe.definitionsv4.layer_geometry import layer_geometry_polygon, \
    layer_geometry_raster


class TestImpactFunctionManager(unittest.TestCase):
    """Test for ImpactFunctionManager.

    .. versionadded:: 2.1
    """

    def setUp(self):
        register_impact_functions()

    def test_init(self):
        """TestImpactFunctionManager: Test initialize ImpactFunctionManager."""
        impact_function_manager = ImpactFunctionManager()
        expected_result = len(impact_function_manager.registry.list())
        i = 0
        '''
        print 'Your impact functions:'
        for impact_function in \
                impact_function_manager.registry.impact_functions:
            i += 1
            print i, impact_function.metadata().as_dict()['name']
        '''
        result = len(impact_function_manager.registry.list())
        message = (
            'I expect %s but I got %s, please check the number of current '
            'enabled impact functions' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_get_function_title(self):
        """TestImpactFunctionManager: Test getting function title."""
        impact_function_title = ImpactFunctionManager().get_function_title(
            ITBFatalityFunction)
        expected_title = 'Be flooded'
        message = 'Expecting %s but got %s' % (
            impact_function_title, expected_title)
        self.assertEqual(
            impact_function_title, expected_title, message)

    @unittest.skip('This test is not a test.')
    def test_get_all_layer_requirements(self):
        """Test to generate all layer requirements from all IFs."""
        impact_function_manager = ImpactFunctionManager()
        for impact_function in impact_function_manager.impact_functions:
            # from pprint import pprint
            print '##', impact_function.metadata().get_name()
            layer_req = impact_function.metadata().get_layer_requirements()
            for key, value in layer_req.iteritems():
                print '###', key
                for k, v in value.iteritems():
                    print '1. ', k
                    if isinstance(v, dict):
                        print '\t-', v['key']
                    else:
                        for the_v in v:
                            print '\t-', the_v['key']
                print ''
            print ''

    def test_available_hazards(self):
        """Test available_hazards API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.available_hazards(
            'single_event')
        expected_result = [hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_available_exposures(self):
        """Test available_exposures API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.available_exposures()
        expected_result = [
            exposure_structure,
            exposure_road,
            exposure_population,
            exposure_place,
            exposure_land_cover]
        self.assertItemsEqual(result, expected_result)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_functions_for_constraint(self):
        """Test functions_for_constraint."""
        ifm = ImpactFunctionManager()
        impact_functions = ifm.functions_for_constraint(
            'earthquake',
            'population',
            'raster',
            'raster',
            'continuous',
            'continuous',
        )
        expected = [
            ITBFatalityFunction.metadata().as_dict(),
            ITBBayesianFatalityFunction.metadata().as_dict(),
            PAGFatalityFunction.metadata().as_dict()]

        for key in impact_functions[0].keys():
            if key == 'parameters':
                # We do not check the parameters since they are mutable.
                continue
            result = [x[key] for x in impact_functions]
            hope = [x[key] for x in expected]
            message = key
            self.assertItemsEqual(result, hope, message)

    def test_exposure_class_fields(self):
        """Test for exposure_class_fields."""
        ifm = ImpactFunctionManager()
        additional_keywords = ifm.exposure_class_fields(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = [structure_class_field]

        self.assertItemsEqual(additional_keywords, expected)

if __name__ == '__main__':
    unittest.main()
