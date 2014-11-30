# coding=utf-8
"""Tests for list parameter."""

from unittest import TestCase

from safe_extras.parameters.list_parameter import ListParameter
from safe_extras.parameters.parameter_exceptions import (
    CollectionLengthError,  InvalidMinimumError, InvalidMaximumError)


good_list = ['one', 'two', 'three']
bad_list = ['one', 2, 3.0]
int_list = [1, 2, 3]


class TestListParameter(TestCase):

    def setUp(self):
        self.parameter = ListParameter()
        self.parameter.is_required = True
        self.parameter.element_type = str

        self.parameter.minimum_item_count = 1
        self.parameter.maximum_item_count = 3
        self.parameter.value = good_list

    def test_all(self):
        """General test."""

        self.assertEqual(good_list, self.parameter.value)

        with self.assertRaises(TypeError):
            self.parameter.value = 'Test'

        with self.assertRaises(TypeError):
            self.parameter.value = 3.0

        with self.assertRaises(TypeError):
            self.parameter.value = 3

    def test_set_minimum_item_count(self):
        with self.assertRaises(InvalidMinimumError):
            # Test what happens if the minimum is set to greater than max
            self.parameter.minimum_item_count = 4

        with self.assertRaises(CollectionLengthError):
            # and what happens if you try to load a list with less items
            # than the required minimum
            self.parameter.maximum_item_count = 8
            self.parameter.minimum_item_count = 4
            self.parameter.value = good_list

    def test_set_maximum_item_count(self):

        with self.assertRaises(InvalidMaximumError):
            # Test what happens if the maximum is set to less than min
            self.parameter.maximum_item_count = 0

        with self.assertRaises(CollectionLengthError):
            # and what happens if you try to load a list with less items
            # than the required minimum
            self.parameter.minimum_item_count = 1
            self.parameter.maximum_item_count = 2
            self.parameter.value = good_list

    def test_count(self):
        self.parameter.value = good_list
        self.assertEqual(len(good_list), self.parameter.count())

    def test_set_element_type(self):
        self.test_set_element_type = int
        with self.assertRaises(TypeError):
            self.parameter.value = bad_list

    def test_set_value(self):
        self.parameter.value = good_list
        self.assertEqual(good_list, self.parameter.value)
