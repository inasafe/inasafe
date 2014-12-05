# coding=utf-8
"""Tests for integer parameter."""

from unittest import TestCase

from safe_extras.parameters.integer_parameter import IntegerParameter
from safe_extras.parameters.parameter_exceptions import (
    InvalidMaximumError, InvalidMinimumError, ValueOutOfBounds)


class TestIntegerParameter(TestCase):
    """Test class for IntegerParameter."""
    def test_all(self):
        """Basic test of all properties."""
        parameter = IntegerParameter()
        parameter.is_required = True
        parameter.minimum_allowed_value = 1
        parameter.maximum_allowed_value = 5
        parameter.value = 3

        self.assertEqual(3, parameter.value)

        with self.assertRaises(TypeError):
            parameter.value = 'Test'

        with self.assertRaises(TypeError):
            parameter.value = 1.5

        with self.assertRaises(ValueOutOfBounds):
            parameter.value = 10

        with self.assertRaises(ValueOutOfBounds):
            parameter.value = -1

    def test_set_minimum_allowed_value(self):
        """Test setter for minimum allowed value."""
        parameter = IntegerParameter()

        with self.assertRaises(TypeError):
            parameter.maximum_allowed_value = 'One thousand'

        with self.assertRaises(TypeError):
            parameter.maximum_allowed_value = 1.5

        parameter.minimum_allowed_value = 1

        # Also check that it raises an error if it exceeds max
        parameter.maximum_allowed_value = 10
        with self.assertRaises(InvalidMinimumError):
            parameter.minimum_allowed_value = 15

        # Also check that when we set a value it falls within [min, max]
        parameter.value = 5

    def test_set_maximum_allowed_value(self):
        """Test setter for maximum allowed value."""
        parameter = IntegerParameter()

        with self.assertRaises(TypeError):
            parameter.maximum_allowed_value = 'One million'

        with self.assertRaises(TypeError):
            parameter.maximum_allowed_value = 100.0

        parameter.maximum_allowed_value = 1000

        # Also check that it raises an error if it precedes min
        parameter.minimum_allowed_value = 10

        with self.assertRaises(InvalidMaximumError):
            parameter.maximum_allowed_value = 1

        # Also check that when we set a value it falls within [min, max]
        parameter.value = 17
