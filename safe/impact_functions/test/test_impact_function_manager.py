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
from safe.impact_functions import register_impact_functions

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '20/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .impact_function import FloodVectorBuildingFunction
from safe.definitions import (
    unit_metres_depth,
    unit_feet_depth,
    exposure_definition,
    exposure_population,
    exposure_road,
    exposure_structure,
    hazard_definition,
    hazard_earthquake,
    hazard_flood,
    hazard_tsunami,
    hazard_volcano,
    unit_building_type_type,
    unit_people_per_pixel,
    unit_mmi,
    hazard_volcanic_ash,
    hazard_generic,
    unit_building_generic)

from safe.new_definitions import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    hazard_category_hazard_scenario,
    hazard_category_hazard_zone,
    hazard_flood,
    hazard_tsunami,
    exposure_structure,
    exposure_road,
    count_exposure_unit,
    density_exposure_unit,
    unit_feet,
    unit_metres,
    unit_millimetres,
    unit_mmi,
    unit_kilogram_per_meter_square,
    unit_kilometres,
    unit_generic
)

class TestImpactFunctionManager(unittest.TestCase):
    """Test for ImpactFunctionManager.

    .. versionadded:: 2.1
    """

    flood_raster_OSM_building_hazard_units = [
        unit_metres_depth, unit_feet_depth]

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
            FloodVectorBuildingFunction)
        expected_title = 'Be flooded'
        message = 'Expecting %s but got %s' % (
            impact_function_title, expected_title)
        self.assertEqual(
            impact_function_title, expected_title, message)

    @unittest.skip('Until updated the API')
    def test_allowed_subcategories(self):
        """TestImpactFunctionManager: Test allowed_subcategories API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.allowed_subcategories()
        expected_result = [
            exposure_structure,
            hazard_earthquake,
            exposure_population,
            hazard_flood,
            hazard_tsunami,
            exposure_road,
            hazard_volcano,
            hazard_volcanic_ash,
            hazard_generic]
        message = (
            'I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_allowed_data_types(self):
        """TestImpactFunctionManager: Test allowed_data_types API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.allowed_data_types('flood')
        expected_result = ['polygon', 'continuous', 'classified']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('volcano')
        expected_result = ['point', 'polygon', 'continuous', 'classified']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('structure')
        expected_result = ['polygon', 'point']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('earthquake')
        expected_result = ['continuous', 'classified']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('tsunami')
        expected_result = ['polygon', 'continuous', 'classified']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('population')
        expected_result = ['continuous']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_allowed_units(self):
        """TestImpactFunctionManager: Test allowed_units API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.allowed_units('structure', 'polygon')
        expected_result = [unit_building_type_type, unit_building_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function_manager.allowed_units('structure', 'raster')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(set(result), set(expected_result), message)

        result = impact_function_manager.allowed_units('flood', 'continuous')
        expected_result = self.flood_raster_OSM_building_hazard_units
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_units(
            'earthquake', 'continuous')
        expected_result = [unit_mmi]

        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_units_for_layer(self):
        """TestImpactFunctionManager: Test units_for_layer API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.units_for_layer(
            subcategory='flood', layer_type='raster', data_type='continuous')
        expected_result = self.flood_raster_OSM_building_hazard_units
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.units_for_layer(
            subcategory='volcano', layer_type='raster', data_type='continuous')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.units_for_layer(
            subcategory='population',
            layer_type='raster',
            data_type='continuous')
        expected_result = [unit_people_per_pixel]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_categories_for_layer(self):
        """TestImpactFunctionManager: Test categories_for_layer API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.categories_for_layer(
            layer_type='raster', data_type='continuous')
        expected_result = [hazard_definition, exposure_definition]
        result_list_id = [e['id'] for e in result]
        expected_list_id = [e['id'] for e in expected_result]
        message = ('I expect %s but I got %s.' % (
            expected_list_id, result_list_id))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.categories_for_layer(
            layer_type='vector', data_type='line')
        expected_result = [exposure_definition]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.categories_for_layer(
            layer_type='vector', data_type='polygon')
        expected_result = [exposure_definition, hazard_definition]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_subcategories_for_layer(self):
        """TestImpactFunctionManager: Test subcategories_for_layer API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.subcategories_for_layer(
            category='hazard', layer_type='raster', data_type='continuous')
        expected_result = [
            hazard_earthquake,
            hazard_flood,
            hazard_tsunami,
            hazard_volcano,
            hazard_volcanic_ash,
            hazard_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.subcategories_for_layer(
            category='hazard', layer_type='vector', data_type='point')
        expected_result = [hazard_volcano]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.subcategories_for_layer(
            category='hazard', layer_type='vector', data_type='polygon')
        expected_result = [hazard_flood, hazard_tsunami, hazard_volcano]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.subcategories_for_layer(
            category='exposure', layer_type='raster', data_type='continuous')
        expected_result = [exposure_population]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.subcategories_for_layer(
            category='exposure', layer_type='vector', data_type='line')
        expected_result = [exposure_road]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.subcategories_for_layer(
            category='exposure', layer_type='vector', data_type='polygon')
        expected_result = [exposure_structure]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    # def test_get_available_hazards(self):
    #     """Test get_available_hazards API."""
    #     impact_function_manager = ImpactFunctionManager()
    #
    #     result = impact_function_manager.get_available_hazards()
    #     expected_result = hazard_all
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)
    #
    #     impact_function = EarthquakeBuildingImpactFunction()
    #     result = impact_function_manager\
    #         .get_available_hazards(impact_function)
    #     expected_result = [hazard_earthquake]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)

    # def test_get_functions_for_hazard(self):
    #     """Test get_functions_for_hazard API."""
    #     impact_function_manager = ImpactFunctionManager()
    #     result = impact_function_manager.get_functions_for_hazard(
    #         hazard_volcano)
    #     expected_result = [
    #         VolcanoPolygonBuildingImpact.Metadata.as_dict(),
    #         VolcanoPointBuildingImpact.Metadata.as_dict(),
    #         VolcanoPolygonHazardPopulation.Metadata.as_dict(),
    #         ContinuousHazardPopulationImpactFunction.Metadata.as_dict(),
    #         ClassifiedHazardBuildingImpactFunction.Metadata.as_dict(),
    #         ClassifiedHazardPopulationImpactFunction.Metadata.as_dict()]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)

    # def test_get_functions_for_hazard_id(self):
    #     """Test get_functions_for_hazard_id API."""
    #     impact_function_manager = ImpactFunctionManager()
    #     result = impact_function_manager.get_functions_for_hazard_id(
    #         hazard_volcano['id'])
    #     expected_result = [
    #         VolcanoPolygonBuildingImpact.Metadata.as_dict(),
    #         VolcanoPointBuildingImpact.Metadata.as_dict(),
    #         VolcanoPolygonHazardPopulation.Metadata.as_dict(),
    #         ContinuousHazardPopulationImpactFunction.Metadata.as_dict(),
    #         ClassifiedHazardBuildingImpactFunction.Metadata.as_dict(),
    #         ClassifiedHazardPopulationImpactFunction.Metadata.as_dict()]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)

    # def test_get_available_exposures(self):
    #     """Test get_available_exposures API."""
    #     impact_function_manager = ImpactFunctionManager()
    #
    #     result = impact_function_manager.get_available_exposures()
    #     expected_result = [
    #         exposure_population,
    #         exposure_road,
    #         exposure_structure]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)
    #
    #     impact_function = EarthquakeBuildingImpactFunction()
    #     result = impact_function_manager.get_available_exposures(
    #         impact_function)
    #     expected_result = [exposure_structure]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)

    # def test_get_functions_for_exposure(self):
    #     """Test get_functions_for_exposure API."""
    #     impact_function_manager = ImpactFunctionManager()
    #     result = impact_function_manager.get_functions_for_exposure(
    #         exposure_structure)
    #     expected_result = [
    #         VolcanoPolygonBuildingImpact.Metadata.as_dict(),
    #         VolcanoPointBuildingImpact.Metadata.as_dict(),
    #         EarthquakeBuildingImpactFunction.Metadata.as_dict(),
    #         FloodRasterBuildingImpactFunction.Metadata.as_dict(),
    #         FloodVectorBuildingImpactFunction.Metadata.as_dict(),
    #         FloodNativePolygonExperimentalFunction.Metadata.as_dict(),
    #         ClassifiedHazardBuildingImpactFunction.Metadata.as_dict()]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)

    # def test_get_functions_for_exposure_id(self):
    #     """Test get_functions_for_exposure_id API."""
    #     impact_function_manager = ImpactFunctionManager()
    #     result = impact_function_manager.get_functions_for_exposure_id(
    #         exposure_structure['id'])
    #     expected_result = [
    #         VolcanoPolygonBuildingImpact.Metadata.as_dict(),
    #         VolcanoPointBuildingImpact.Metadata.as_dict(),
    #         EarthquakeBuildingImpactFunction.Metadata.as_dict(),
    #         FloodRasterBuildingImpactFunction.Metadata.as_dict(),
    #         FloodVectorBuildingImpactFunction.Metadata.as_dict(),
    #         FloodNativePolygonExperimentalFunction.Metadata.as_dict(),
    #         ClassifiedHazardBuildingImpactFunction.Metadata.as_dict()]
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(result, expected_result, message)

    # def test_get_functions_for_constraint(self):
    #     """Test get_functions_for_constraint."""
    #     impact_function_manager = ImpactFunctionManager()
    #     hazard = hazard_earthquake
    #     exposure = exposure_structure
    #
    #     expected_result = [
    #         EarthquakeBuildingImpactFunction.Metadata.as_dict(),
    #         ClassifiedHazardBuildingImpactFunction.Metadata.as_dict()]
    #     result = impact_function_manager.get_functions_for_constraint(
    #         hazard, exposure)
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(expected_result, result, message)
    #
    #     hazard_constraint = layer_raster_continuous
    #     exposure_constraint = None
    #
    #     expected_result = [
    #         EarthquakeBuildingImpactFunction.Metadata.as_dict()]
    #     result = impact_function_manager.get_functions_for_constraint(
    #         hazard, exposure, hazard_constraint, exposure_constraint)
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(expected_result, result, message)
    #
    #     hazard_constraint = layer_vector_polygon
    #     exposure_constraint = layer_vector_line
    #
    #     expected_result = []
    #     result = impact_function_manager.get_functions_for_constraint(
    #         hazard, exposure, hazard_constraint, exposure_constraint)
    #     message = ('I expect %s but I got %s.' % (expected_result, result))
    #     self.assertItemsEqual(expected_result, result, message)

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
                    if type(v) is dict:
                        print '\t-', v['key']
                    else:
                        for the_v in v:
                            print '\t-', the_v['key']
                print ''
            # pprint(impact_function.metadata().get_layer_requirements())
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
        hazard_categories = impact_function_manager.hazard_categories_for_layer(
            'polygon')
        expected = [hazard_category_hazard_scenario,
                    hazard_category_hazard_zone]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager.hazard_categories_for_layer(
            'line')
        expected = []
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager.hazard_categories_for_layer(
            'point')
        expected = [hazard_category_hazard_zone]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function_manager.hazard_categories_for_layer(
            'raster')
        expected = [hazard_category_hazard_scenario, hazard_category_hazard_zone]
        self.assertItemsEqual(hazard_categories, expected)

    def test_hazard_for_layer(self):
        """Test for hazard_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        hazards = impact_function_manager.hazard_for_layer(
            'polygon', 'hazard_scenario')
        expected = [hazard_flood, hazard_tsunami]
        self.assertItemsEqual(hazards, expected)

        hazards = impact_function_manager.hazard_for_layer(
            'point', 'hazard_scenario')
        expected = []
        self.assertItemsEqual(hazards, expected)

    def test_exposure_for_layer(self):
        """Test for exposure_for_layer"""
        impact_function_manager = ImpactFunctionManager()
        exposures = impact_function_manager.exposure_for_layer(
            'polygon')
        expected = [exposure_structure]
        self.assertItemsEqual(exposures, expected)

        exposures = impact_function_manager.exposure_for_layer(
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
                'tsunami', 'raster', 'continuous', 'hazard_scenario')
        expected = [unit_feet,
                    unit_metres,
                    unit_millimetres,
                    unit_mmi,
                    unit_kilogram_per_meter_square,
                    unit_kilometres,
                    unit_generic]
        self.assertItemsEqual(continuous_hazards_units, expected)


if __name__ == '__main__':
    unittest.main()
