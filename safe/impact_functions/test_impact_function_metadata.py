# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Message Modele.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe import metadata

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '17/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.earthquake.earthquake_building_impact import \
    EarthquakeBuildingImpactFunction
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

    def test_add_to_list(self):
        """Test for add_to_list function
        """
        list_original = ['a', 'b', ['a'], {'a': 'b'}]
        list_a = ['a', 'b', ['a'], {'a': 'b'}]
        # add same immutable element
        list_b = ImpactFunctionMetadata.add_to_list(list_a, 'b')
        assert list_b == list_original
        # add list
        list_b = ImpactFunctionMetadata.add_to_list(list_a, ['a'])
        assert list_b == list_original
        # add same mutable element
        list_b = ImpactFunctionMetadata.add_to_list(list_a, {'a': 'b'})
        assert list_b == list_original
        # add new mutable element
        list_b = ImpactFunctionMetadata.add_to_list(list_a, 'c')
        print list_b, 'b'
        print list_a, 'a'
        assert len(list_b) == (len(list_original) + 1)
        assert list_b[-1] == 'c'

    def test_inner_class(self):
        """Test call inner class
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        # call from an object
        metadata = my_impact_function.Metadata()
        metadata_dict = metadata.get_metadata()
        assert isinstance(metadata_dict, dict), 'I did not got a dict'
        # call from the class
        metadata = my_impact_function.Metadata
        metadata_dict = metadata.get_metadata()
        assert isinstance(metadata_dict, dict), 'I did not got a dict'

    def test_allowed_subcategories(self):
        """Test for allowed_subcategories API
        """
        my_impact_function = EarthquakeBuildingImpactFunction()
        result = my_impact_function.Metadata.\
            allowed_subcategories()
        expected_result = ['earthquake', 'structure']
        msg = 'I should get ' + str(expected_result) + ' but I got ' + str(
            result)
        self.assertEqual(set(result), set(expected_result), msg)

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
                'name': metadata.building_type_name,
                'description': metadata.building_type_text,
                'constraint': 'unique values',
                'default': 'type'
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

if __name__ == '__main__':
    unittest.main()
