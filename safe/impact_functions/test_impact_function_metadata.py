# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Metadata**

Contact : ole.moller.nielsen@gmail.com

.. note:: This sprogram is free software; you can redistribute it and/or modify
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
from safe.metadata import small_number
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.earthquake.earthquake_building_impact import \
    EarthquakeBuildingImpactFunction
from safe.impact_functions.inundation.flood_OSM_building_impact import \
    FloodBuildingImpactFunction
from exceptions import NotImplementedError


class TestImpactFunctionMetadata(unittest.TestCase):
    def test_init(self):
        """Test init base class
        """
        ifm = ImpactFunctionMetadata()
        with self.assertRaises(NotImplementedError):
            ifm.get_metadata()
            ifm.allowed_data_types('flood')

    def test_is_subset(self):
        """Test for is_subset function
        """
        assert ImpactFunctionMetadata.is_subset('a', ['a'])
        assert ImpactFunctionMetadata.is_subset('a', ['a', 'b'])
        assert ImpactFunctionMetadata.is_subset(['a'], ['a', 'b'])
        assert ImpactFunctionMetadata.is_subset('a', 'a')
        assert not ImpactFunctionMetadata.is_subset('a', 'ab')
        assert not ImpactFunctionMetadata.is_subset(['a', 'c'], ['a', 'b'])

    def test_inner_class(self):
        """Test call inner class
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        # call from an object
        my_metadata = my_impact_function.Metadata()
        metadata_dict = my_metadata.get_metadata()
        assert isinstance(metadata_dict, dict), 'I did not got a dict'
        # call from the class
        my_metadata = my_impact_function.Metadata
        metadata_dict = my_metadata.get_metadata()
        assert isinstance(metadata_dict, dict), 'I did not got a dict'

    def test_allowed_subcategories(self):
        """Test for allowed_subcategories API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata. \
            allowed_subcategories(category='hazard')
        expected_result = ['earthquake']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata. \
            allowed_subcategories(category='exposure')
        expected_result = ['structure']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata.\
            allowed_subcategories()
        expected_result = ['earthquake', 'structure']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(set(result), set(expected_result), msg)

    def test_allowed_data_types(self):
        """Test for allowed_data_types API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata\
            .allowed_data_types('structure')
        expected_result = ['polygon']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata \
            .allowed_data_types('earthquake')
        expected_result = ['numeric', 'polygon']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(set(result), set(expected_result), msg)

    def test_allowed_units(self):
        """Test for allowed_units API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata \
            .allowed_units('structure', 'polygon')
        expected_result = [
            {
                'id': 'building_type',
                'constraint': 'unique values',
                'default_attribute': 'type'
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata \
            .allowed_units('structure', 'numeric')
        expected_result = []
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        my_impact_function = FloodBuildingImpactFunction
        result = my_impact_function.Metadata \
            .allowed_units('structure', 'polygon')
        expected_result = [
            {
                'id': 'building_type',
                'constraint': 'unique values',
                'default_attribute': 'type'
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata \
            .allowed_units('flood', 'numeric')
        expected_result = [
            {
                'id': 'wetdry',
                'constraint': 'categorical',
                'default_attribute': 'affected',
                'default_category': 'wet',
                'classes': [
                    {
                        'name': 'wet',
                        'description': 'Water above ground height.',
                        'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
                        'numeric_default_min': 1,
                        'numeric_default_max': 9999999999,
                        'optional': True,
                        },
                    {
                        'name': 'dry',
                        'description': 'No water above ground height.',
                        'string_defaults': ['dry', '0', 'No', 'n', 'no'],
                        'numeric_default_min': 0,
                        'numeric_default_max': 1 - small_number,
                        'optional': True
                    }
                ]
            },
            {
                'id': 'metres',
                'constraint': 'continuous',
                'default_attribute': 'depth'  # applies to vector only
            },
            {
                'id': 'feet',
                'constraint': 'continuous',
                'default_attribute': 'depth'  # applies to vector only
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

    def test_allowed_layer_constraints(self):
        """Test for allowed_layer_constraints API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata. \
            allowed_layer_constraints()
        expected_result = [
            {
                'layer_type': 'vector',
                'data_type': 'polygon'
            },
            {
                'layer_type': 'raster',
                'data_type': 'numeric'
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata. \
            allowed_layer_constraints('hazard')
        expected_result = [
            {
                'layer_type': 'vector',
                'data_type': 'polygon'
            },
            {
                'layer_type': 'raster',
                'data_type': 'numeric'
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata. \
            allowed_layer_constraints('exposure')
        expected_result = [
            {
                'layer_type': 'vector',
                'data_type': 'polygon'
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

    def test_units_for_layer(self):
        """Test for units_for_layer API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata. \
            units_for_layer(subcategory='earthquake', layer_type='raster',
                            data_type='numeric')
        expected_result = [
            {
                'id': 'mmi',
                'constraint': 'continuous',
                'default_attribute': 'depth'
            }
        ]
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata. \
            units_for_layer(subcategory='flood', layer_type='raster',
                            data_type='numeric')
        expected_result = []
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata. \
            units_for_layer(subcategory='earthquake', layer_type='vector',
                            data_type='numeric')
        expected_result = []
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        result = my_impact_function.Metadata. \
            units_for_layer(subcategory='earthquake', layer_type='raster',
                            data_type='polygon')
        expected_result = []
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

    def test_categories_for_layer(self):
        """Test for categories_for_layer API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata. \
            categories_for_layer(layer_type='raster', data_type='numeric')
        expected_result = ['hazard']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata. \
            categories_for_layer(layer_type='vector', data_type='line')
        expected_result = []
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(result, expected_result, msg)

        my_impact_function = FloodBuildingImpactFunction()
        result = my_impact_function.Metadata. \
            categories_for_layer(layer_type='vector', data_type='polygon')
        expected_result = ['hazard', 'exposure']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(set(result), set(expected_result), msg)

if __name__ == '__main__':
    unittest.main()
