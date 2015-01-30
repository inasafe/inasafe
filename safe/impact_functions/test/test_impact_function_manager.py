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
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.earthquake.earthquake_building_impact import (
    EarthquakeBuildingImpactFunction)
from safe.impact_functions.inundation.flood_OSM_building_impact import (
    FloodBuildingImpactFunction)
from safe.impact_functions.inundation.flood_building_impact_qgis import (
    FloodNativePolygonExperimentalFunction)
from safe.impact_functions.volcanic.volcano_building_impact import (
    VolcanoBuildingImpact)
from safe.impact_functions.volcanic. \
    volcano_population_evacuation_polygon_hazard import (
        VolcanoPolygonHazardPopulation)
from safe.impact_functions.generic.categorised_hazard_population import (
    CategorisedHazardPopulationImpactFunction)
from safe.impact_functions.generic.categorical_hazard_building import (
    CategoricalHazardBuildingImpactFunction)
from safe.impact_functions.generic.categorical_hazard_population import (
    CategoricalHazardPopulationImpactFunction)

from safe.metadata import (
    unit_wetdry,
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
    hazard_tephra,
    unit_normalised,
    hazard_generic,
    unit_building_generic,
    unit_categorical,
    hazard_all,
    layer_vector_polygon,
    layer_vector_line)


class TestImpactFunctionManager(unittest.TestCase):
    """Test for ImpactFunctionManager.

    .. versionadded:: 2.1
    """

    flood_OSM_building_hazard_units = [
        unit_wetdry, unit_metres_depth, unit_feet_depth, unit_normalised,
        unit_categorical]

    def test_init(self):
        """Test initialize ImpactFunctionManager."""
        impact_function_manager = ImpactFunctionManager()
        expected_result = 15
        i = 0
        print 'Your impact functions:'
        for impact_function in impact_function_manager.impact_functions:
            i += 1
            print i, impact_function.Metadata.get_metadata()['name']
        result = len(impact_function_manager.impact_functions)
        message = (
            'I expect %s but I got %s, please check the number of current '
            'enabled impact functions' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_allowed_subcategories(self):
        """Test allowed_subcategories API."""
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
            hazard_tephra,
            hazard_generic]
        message = (
            'I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_allowed_data_types(self):
        """Test allowed_data_types API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.allowed_data_types('flood')
        expected_result = ['polygon', 'numeric']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('volcano')
        expected_result = ['point', 'polygon', 'numeric']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('structure')
        expected_result = ['polygon', 'point']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('earthquake')
        expected_result = ['polygon', 'numeric']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('tsunami')
        expected_result = ['polygon', 'numeric']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_data_types('population')
        expected_result = ['numeric']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_allowed_units(self):
        """Test allowed_units API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.allowed_units('structure', 'polygon')
        expected_result = [unit_building_type_type, unit_building_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function_manager.allowed_units('structure', 'raster')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(set(result), set(expected_result), message)

        result = impact_function_manager.allowed_units('flood', 'numeric')
        expected_result = self.flood_OSM_building_hazard_units
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.allowed_units('earthquake', 'numeric')
        expected_result = [unit_mmi, unit_normalised, unit_categorical]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_units_for_layer(self):
        """Test units_for_layer API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.units_for_layer(
            subcategory='flood', layer_type='raster', data_type='numeric')
        expected_result = self.flood_OSM_building_hazard_units
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.units_for_layer(
            subcategory='volcano', layer_type='raster', data_type='numeric')
        expected_result = [unit_normalised, unit_categorical]
        print result
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.units_for_layer(
            subcategory='population', layer_type='raster', data_type='numeric')
        expected_result = [unit_people_per_pixel]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_categories_for_layer(self):
        """Test categories_for_layer API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.categories_for_layer(
            layer_type='raster', data_type='numeric')
        expected_result = [hazard_definition, exposure_definition]
        message = ('I expect %s but I got %s.' % (expected_result, result))
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

    def test_subcategories_for_layer(self):
        """Test subcategories_for_layer API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.subcategories_for_layer(
            category='hazard', layer_type='raster', data_type='numeric')
        expected_result = [
            hazard_earthquake,
            hazard_flood,
            hazard_tsunami,
            hazard_tephra,
            hazard_volcano,
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
        expected_result = [
            hazard_earthquake, hazard_flood, hazard_tsunami, hazard_volcano]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function_manager.subcategories_for_layer(
            category='exposure', layer_type='raster', data_type='numeric')
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

    def test_get_available_hazards(self):
        """Test get_available_hazards API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.get_available_hazards()
        expected_result = hazard_all
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function_manager.get_available_hazards(impact_function)
        expected_result = [hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_get_functions_for_hazard(self):
        """Test get_functions_for_hazard API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.get_functions_for_hazard(
            hazard_volcano)
        expected_result = [
            VolcanoBuildingImpact.Metadata.get_metadata(),
            VolcanoPolygonHazardPopulation.Metadata.get_metadata(),
            CategorisedHazardPopulationImpactFunction.Metadata.get_metadata(),
            CategoricalHazardBuildingImpactFunction.Metadata.get_metadata(),
            CategoricalHazardPopulationImpactFunction.Metadata.get_metadata()]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_get_functions_for_hazard_id(self):
        """Test get_functions_for_hazard_id API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.get_functions_for_hazard_id(
            hazard_volcano['id'])
        expected_result = [
            VolcanoBuildingImpact.Metadata.get_metadata(),
            VolcanoPolygonHazardPopulation.Metadata.get_metadata(),
            CategorisedHazardPopulationImpactFunction.Metadata.get_metadata(),
            CategoricalHazardBuildingImpactFunction.Metadata.get_metadata(),
            CategoricalHazardPopulationImpactFunction.Metadata.get_metadata()]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_get_available_exposures(self):
        """Test get_available_exposures API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.get_available_exposures()
        expected_result = [
            exposure_population,
            exposure_road,
            exposure_structure]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function_manager.get_available_exposures(impact_function)
        expected_result = [exposure_structure]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_get_functions_for_exposure(self):
        """Test get_functions_for_exposure API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.get_functions_for_exposure(
            exposure_structure)
        expected_result = [
            VolcanoBuildingImpact.Metadata.get_metadata(),
            EarthquakeBuildingImpactFunction.Metadata.get_metadata(),
            FloodBuildingImpactFunction.Metadata.get_metadata(),
            FloodNativePolygonExperimentalFunction.Metadata.get_metadata(),
            CategoricalHazardBuildingImpactFunction.Metadata.get_metadata()]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_get_functions_for_exposure_id(self):
        """Test get_functions_for_exposure_id API."""
        impact_function_manager = ImpactFunctionManager()
        result = impact_function_manager.get_functions_for_exposure_id(
            exposure_structure['id'])
        expected_result = [
            VolcanoBuildingImpact.Metadata.get_metadata(),
            EarthquakeBuildingImpactFunction.Metadata.get_metadata(),
            FloodBuildingImpactFunction.Metadata.get_metadata(),
            FloodNativePolygonExperimentalFunction.Metadata.get_metadata(),
            CategoricalHazardBuildingImpactFunction.Metadata.get_metadata()]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_get_functions_for_constraint(self):
        """Test get_functions_for_constraint."""
        impact_function_manager = ImpactFunctionManager()
        hazard = hazard_earthquake
        exposure = exposure_structure

        expected_result = [
            EarthquakeBuildingImpactFunction.Metadata.get_metadata(),
            CategoricalHazardBuildingImpactFunction.Metadata.get_metadata()]
        result = impact_function_manager.get_functions_for_constraint(
            hazard, exposure)
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(expected_result, result, message)

        hazard_constraint = layer_vector_polygon
        exposure_constraint = None

        expected_result = [
            EarthquakeBuildingImpactFunction.Metadata.get_metadata()]
        result = impact_function_manager.get_functions_for_constraint(
            hazard, exposure, hazard_constraint, exposure_constraint)
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(expected_result, result, message)

        hazard_constraint = layer_vector_polygon
        exposure_constraint = layer_vector_line

        expected_result = []
        result = impact_function_manager.get_functions_for_constraint(
            hazard, exposure, hazard_constraint, exposure_constraint)
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(expected_result, result, message)

    def test_available_functions(self):
        """Test that we can get available functions given some keywords."""

        exposure_keywords = {
            'category': 'exposure',
            'subcategory': 'population',
            'title': 'Orang',
            'datatype': 'density',
            'source': (
                'Center for International Earth Science Information '
                'Network (CIESIN)'),
            'layertype': 'raster'}

        hazard_keywords = {
            'category': 'hazard',
            'subcategory': 'flood',
            'title': 'Banjir di Jakarta seperti tahun 2007',
            'thresholds': (0.3, 0.5, 1.0),
            'source': 'HKV',
            'layertype': 'raster',
            'unit': 'm'
        }

        result = ImpactFunctionManager().available_functions(
            hazard_keywords,
            exposure_keywords
        )

        self.assertEqual(len(result), 3)


if __name__ == '__main__':
    unittest.main()
