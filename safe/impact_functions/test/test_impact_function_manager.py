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

from safe.impact_functions import register_impact_functions
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model \
    .impact_function import PAGFatalityFunction
from safe.impact_functions.generic.continuous_hazard_population\
    .impact_function import ContinuousHazardPopulationFunction
from safe.impact_functions.inundation.flood_vector_building_impact\
    .impact_function import FloodPolygonBuildingFunction
from safe.definitions import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    hazard_category_single_event,
    hazard_category_multiple_event,
    hazard_flood,
    hazard_tsunami,
    hazard_generic,
    hazard_earthquake,
    hazard_volcanic_ash,
    hazard_volcano,
    exposure_structure,
    exposure_road,
    exposure_population,
    count_exposure_unit,
    density_exposure_unit,
    continuous_hazard_unit_all,
    layer_mode_continuous,
    layer_geometry_raster,
    layer_mode_classified,
    layer_geometry_polygon,
    affected_field,
    affected_value,
    hazard_zone_field,
    building_type_field
)


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
        print 'Your impact functions:'
        for impact_function in \
                impact_function_manager.registry.impact_functions:
            i += 1
            print i, impact_function.metadata().as_dict()['name']
        result = len(impact_function_manager.registry.list())
        message = (
            'I expect %s but I got %s, please check the number of current '
            'enabled impact functions' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_get_function_title(self):
        """TestImpactFunctionManager: Test getting function title."""
        impact_function_title = ImpactFunctionManager().get_function_title(
            FloodPolygonBuildingFunction)
        expected_title = 'Be flooded'
        message = 'Expecting %s but got %s' % (
            impact_function_title, expected_title)
        self.assertEqual(
            impact_function_title, expected_title, message)

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

    def test_purposes_for_layer(self):
        """Test for purposes_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        layer_purposes = impact_function_manager.purposes_for_layer('polygon')
        expected = [layer_purpose_hazard, layer_purpose_exposure]
        self.assertItemsEqual(layer_purposes, expected)

        layer_purposes = impact_function_manager.purposes_for_layer('line')
        expected = [layer_purpose_exposure]
        self.assertItemsEqual(layer_purposes, expected)

        layer_purposes = impact_function_manager.purposes_for_layer('point')
        expected = [layer_purpose_hazard, layer_purpose_exposure]
        self.assertItemsEqual(layer_purposes, expected)

        layer_purposes = impact_function_manager.purposes_for_layer('raster')
        expected = [layer_purpose_hazard, layer_purpose_exposure]
        self.assertItemsEqual(layer_purposes, expected)

    def test_hazard_categories_for_layer(self):
        """Test for hazard_categories_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        hazard_categories = impact_function_manager.\
            hazard_categories_for_layer('polygon')
        expected = [
            hazard_category_single_event,
            hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager.\
            hazard_categories_for_layer('line')
        expected = []
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager.\
            hazard_categories_for_layer('point')
        expected = [hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager.\
            hazard_categories_for_layer('raster')
        expected = [
            hazard_category_single_event,
            hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager. \
            hazard_categories_for_layer('raster', 'earthquake')
        expected = [
            hazard_category_single_event,
            hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

    def test_hazards_for_layer(self):
        """Test for hazards_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        hazards = impact_function_manager.hazards_for_layer(
            'polygon', 'single_event')
        expected = [hazard_flood, hazard_tsunami, hazard_earthquake,
                    hazard_volcano, hazard_volcanic_ash, hazard_generic]
        self.assertItemsEqual(hazards, expected)

        hazards = impact_function_manager.hazards_for_layer('polygon')
        expected = [hazard_flood, hazard_tsunami, hazard_earthquake,
                    hazard_volcano, hazard_volcanic_ash, hazard_generic]
        self.assertItemsEqual(hazards, expected)

        hazards = impact_function_manager.hazards_for_layer(
            'point', 'single_event')
        expected = []
        self.assertItemsEqual(hazards, expected)

    def test_exposures_for_layer(self):
        """Test for exposures_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        exposures = impact_function_manager.exposures_for_layer(
            'polygon')
        expected = [exposure_structure]
        self.assertItemsEqual(exposures, expected)

        exposures = impact_function_manager.exposures_for_layer(
            'line')
        expected = [exposure_road]
        self.assertItemsEqual(exposures, expected)

    def test_exposure_units_for_layer(self):
        """Test for exposure_units_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        exposure_units = impact_function_manager.exposure_units_for_layer(
            'population', 'raster', 'continuous')
        expected = [count_exposure_unit, density_exposure_unit]
        self.assertItemsEqual(exposure_units, expected)

    def test_continuous_hazards_units_for_layer(self):
        """Test for continuous_hazards_units_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        continuous_hazards_units = impact_function_manager.\
            continuous_hazards_units_for_layer(
                'tsunami', 'raster', 'continuous', 'single_event')
        expected = continuous_hazard_unit_all
        self.assertItemsEqual(continuous_hazards_units, expected)

    def test_available_hazards(self):
        """Test available_hazards API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.available_hazards(
            'single_event')
        expected_result = [hazard_flood,
                           hazard_tsunami,
                           hazard_generic,
                           hazard_earthquake,
                           hazard_volcanic_ash,
                           hazard_volcano]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_available_exposures(self):
        """Test available_exposures API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.available_exposures()
        expected_result = [
            exposure_structure, exposure_road, exposure_population]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

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
            PAGFatalityFunction.metadata().as_dict(),
            ContinuousHazardPopulationFunction.metadata().as_dict()]

        for key in impact_functions[0].keys():
            if key == 'parameters':
                # We do not check the parameters since they are mutable.
                continue
            result = [x[key] for x in impact_functions]
            hope = [x[key] for x in expected]
            message = key
            self.assertItemsEqual(result, hope, message)

    def test_available_hazard_constraints(self):
        """Test for available_hazard_constraints."""
        ifm = ImpactFunctionManager()
        hazard_constraints = ifm.available_hazard_constraints(
            'earthquake', 'single_event')
        expected = [
            (layer_mode_continuous, layer_geometry_raster),
            (layer_mode_classified, layer_geometry_raster),
            (layer_mode_classified, layer_geometry_polygon),
        ]

        self.assertItemsEqual(hazard_constraints, expected)

    def test_available_exposure_constraints(self):
        """Test for available_exposure_constraints."""
        ifm = ImpactFunctionManager()
        exposure_constraints = ifm.available_exposure_constraints(
            'population')
        expected = [
            (layer_mode_continuous, layer_geometry_raster),
        ]

        self.assertItemsEqual(exposure_constraints, expected)

    def test_available_hazard_layer_modes(self):
        """Test for available_hazard_layer_modes."""
        ifm = ImpactFunctionManager()
        hazard_layer_mode = ifm.available_hazard_layer_modes(
            'earthquake', 'raster', 'single_event')
        expected = [layer_mode_continuous, layer_mode_classified]

        self.assertItemsEqual(hazard_layer_mode, expected)

    def test_available_exposure_layer_modes(self):
        """Test for available_exposure_layer_modes."""
        ifm = ImpactFunctionManager()
        exposure_layer_mode = ifm.available_exposure_layer_modes(
            'population', 'raster')
        expected = [layer_mode_continuous]

        self.assertItemsEqual(exposure_layer_mode, expected)

    def test_hazard_additional_keywords(self):
        """Test for hazard_additional_keywords."""
        ifm = ImpactFunctionManager()
        additional_keywords = ifm.hazard_additional_keywords(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            hazard_category_key='single_event',
            hazard_key='flood'
        )
        expected = [affected_field, affected_value, hazard_zone_field]

        self.assertItemsEqual(additional_keywords, expected)

    def test_exposure_additional_keywords(self):
        """Test for exposure_additional_keywords."""
        ifm = ImpactFunctionManager()
        additional_keywords = ifm.exposure_additional_keywords(
            layer_mode_key='none',
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = [building_type_field]

        self.assertItemsEqual(additional_keywords, expected)

if __name__ == '__main__':
    unittest.main()
