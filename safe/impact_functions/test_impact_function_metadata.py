# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Metadata**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '17/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.impact_functions.earthquake.earthquake_building_impact import (
    EarthquakeBuildingImpactFunction)
from safe.impact_functions.inundation.flood_OSM_building_impact import (
    FloodBuildingImpactFunction)
from safe.impact_functions.generic.categorised_hazard_population import (
    CategorisedHazardPopulationImpactFunction)
from safe.metadata import (
    unit_wetdry,
    unit_metres_depth,
    unit_feet_depth,
    unit_mmi,
    exposure_structure,
    hazard_earthquake,
    unit_building_type_type,
    layer_raster_numeric,
    layer_vector_polygon,
    layer_vector_point,
    unit_normalised,
    hazard_all,
    unit_building_generic)


# noinspection PyUnresolvedReferences
class TestImpactFunctionMetadata(unittest.TestCase):
    """Test for ImpactFunctionMetadata.

    .. versionadded:: 2.1
    """
    def test_init(self):
        """Test init base class."""
        ifm = ImpactFunctionMetadata()
        with self.assertRaises(NotImplementedError):
            ifm.get_metadata()
            ifm.allowed_data_types('flood')

    def test_is_subset(self):
        """Test for is_subset function."""
        assert ImpactFunctionMetadata.is_subset('a', ['a'])
        assert ImpactFunctionMetadata.is_subset('a', ['a', 'b'])
        assert ImpactFunctionMetadata.is_subset(['a'], ['a', 'b'])
        assert ImpactFunctionMetadata.is_subset('a', 'a')
        assert not ImpactFunctionMetadata.is_subset('a', 'ab')
        assert not ImpactFunctionMetadata.is_subset(['a', 'c'], ['a', 'b'])

    def test_inner_class(self):
        """Test call inner class."""
        impact_function = EarthquakeBuildingImpactFunction()
        # call from an object
        metadata = impact_function.Metadata()
        metadata_dictionary = metadata.get_metadata()
        assert isinstance(metadata_dictionary, dict), 'I did not got a dict'
        # call from the class
        metadata = impact_function.Metadata
        metadata_dictionary = metadata.get_metadata()
        assert isinstance(metadata_dictionary, dict), 'I did not got a dict'

    def test_allowed_subcategories(self):
        """Test for allowed_subcategories API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.allowed_subcategories(
            category='hazard')
        expected_result = [hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata.allowed_subcategories(
            category='exposure')
        expected_result = [exposure_structure]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata.allowed_subcategories()
        expected_result = [exposure_structure, hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = CategorisedHazardPopulationImpactFunction()
        result = impact_function.Metadata.allowed_subcategories(
            category='hazard')
        expected_result = hazard_all
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_allowed_data_types(self):
        """Test for allowed_data_types API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.allowed_data_types('structure')
        expected_result = ['polygon', 'point']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function.Metadata .allowed_data_types('earthquake')
        expected_result = ['numeric', 'polygon']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_allowed_units(self):
        """Test for allowed_units API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata .allowed_units(
            'structure', 'polygon')
        expected_result = [unit_building_type_type, unit_building_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function.Metadata .allowed_units(
            'structure', 'numeric')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodBuildingImpactFunction
        result = impact_function.Metadata.allowed_units(
            'structure', 'polygon')
        expected_result = [unit_building_type_type, unit_building_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function.Metadata .allowed_units('flood', 'numeric')
        expected_result = [unit_wetdry, unit_metres_depth, unit_feet_depth]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_allowed_layer_constraints(self):
        """Test for allowed_layer_constraints API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.allowed_layer_constraints()
        expected_result = [
            layer_vector_polygon, layer_raster_numeric, layer_vector_point]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata. allowed_layer_constraints(
            'hazard')
        expected_result = [layer_vector_polygon, layer_raster_numeric]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata.allowed_layer_constraints(
            'exposure')
        expected_result = [layer_vector_polygon, layer_vector_point]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_units_for_layer(self):
        """Test for units_for_layer API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.units_for_layer(
            subcategory='earthquake', layer_type='raster', data_type='numeric')
        expected_result = [unit_mmi]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata.units_for_layer(
            subcategory='flood', layer_type='raster', data_type='numeric')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata.units_for_layer(
            subcategory='earthquake', layer_type='vector', data_type='numeric')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.Metadata.units_for_layer(
            subcategory='earthquake', layer_type='raster', data_type='polygon')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = CategorisedHazardPopulationImpactFunction()
        result = impact_function.Metadata.units_for_layer(
            subcategory='flood', layer_type='raster', data_type='numeric')
        expected_result = [unit_normalised]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_categories_for_layer(self):
        """Test for categories_for_layer API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.categories_for_layer(
            layer_type='raster', data_type='numeric')
        expected_result = ['hazard']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.categories_for_layer(
            layer_type='vector', data_type='line')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodBuildingImpactFunction()
        result = impact_function.Metadata.categories_for_layer(
            layer_type='vector', data_type='polygon')
        expected_result = ['hazard', 'exposure']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_subcategories_for_layer(self):
        """Test for subcategories_for_layer API."""
        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata. subcategories_for_layer(
            category='hazard', layer_type='raster', data_type='numeric')
        expected_result = [hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = EarthquakeBuildingImpactFunction()
        result = impact_function.Metadata.subcategories_for_layer(
            category='exposure', layer_type='vector', data_type='polygon')
        expected_result = [exposure_structure]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

if __name__ == '__main__':
    unittest.main()
