# coding=utf-8
"""Tests for dict parameter."""

from unittest import TestCase

from safe_extras.parameters.dict_parameter import DictParameter
from safe_extras.parameters.parameter_exceptions import (
    CollectionLengthError,  InvalidMinimumError, InvalidMaximumError)


good_dict = {'foo': True, 'bar': False, 'woo': False}
bad_dict = {'foo': True, 'bar': 'wawa', '': ''}


class TestListParameter(TestCase):

    def setUp(self):
        self.parameter = DictParameter()
        self.parameter.is_required = True
        self.parameter.element_type = str

        self.parameter.minimum_item_count = 1
        self.parameter.maximum_item_count = 3
        self.parameter.value = good_dict

    def test_all(self):
        """General test."""

        self.assertEqual(good_dict, self.parameter.value)

        with self.assertRaises(TypeError):
            self.parameter.value = 'Test'

        with self.assertRaises(TypeError):
            self.parameter.value = 3.0

        with self.assertRaises(TypeError):
            self.parameter.value = 3

    def test_minimum_item_count(self):
        """Test minimum item count mutator."""
        with self.assertRaises(InvalidMinimumError):
            # Test what happens if the minimum is set to greater than max
            self.parameter.minimum_item_count = 4

        with self.assertRaises(CollectionLengthError):
            # and what happens if you try to load a list with less items
            # than the required minimum
            self.parameter.maximum_item_count = 8
            self.parameter.minimum_item_count = 4
            self.parameter.value = good_dict

    def test_maximum_item_count(self):
        """Test maximum item count mutator."""
        with self.assertRaises(InvalidMaximumError):
            # Test what happens if the maximum is set to less than min
            self.parameter.maximum_item_count = 0

        with self.assertRaises(CollectionLengthError):
            # and what happens if you try to load a list with less items
            # than the required minimum
            self.parameter.minimum_item_count = 1
            self.parameter.maximum_item_count = 2
            self.parameter.value = good_dict

    def test_count(self):
        """Text count method."""
        self.parameter.value = good_dict
        self.assertEqual(len(good_dict), self.parameter.count())

    def test_element_type(self):
        """Test element type method."""
        self.parameter.element_type = int
        with self.assertRaises(TypeError):
            self.parameter.value = bad_dict

    def test_value(self):
        """Test value mutator."""
        self.parameter.value = good_dict
        self.assertEqual(good_dict, self.parameter.value)
