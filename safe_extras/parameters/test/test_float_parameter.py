# coding=utf-8
"""Tests for float parameter."""

from unittest import TestCase

from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.parameter_exceptions import (
    InvalidMaximumError, InvalidMinimumError, ValueOutOfBounds)


class TestFloatParameter(TestCase):
    """Test class for FloatParameter."""
    def test_all(self):
        """Basic test of all properties."""
        parameter = FloatParameter()
        parameter.is_required = True
        parameter.minimum_allowed_value = 1.0
        parameter.maximum_allowed_value = 2.0
        parameter.value = 1.123

        self.assertEqual(1.123, parameter.value)

        with self.assertRaises(TypeError):
            parameter.value = 'Test'

        with self.assertRaises(ValueOutOfBounds):
            parameter.value = 3.0

        with self.assertRaises(ValueOutOfBounds):
            parameter.value = 0.5

    def test_set_minimum_allowed_value(self):
        """Test setter for minimum allowed value."""
        parameter = FloatParameter()

        with self.assertRaises(TypeError):
            parameter.maximum_allowed_value = 'One thousand'

        parameter.minimum_allowed_value = 1

        parameter.minimum_allowed_value = 1.0
        # Also check that it raises an error if it exceeds max
        parameter.maximum_allowed_value = 10.0
        with self.assertRaises(InvalidMinimumError):
            parameter.minimum_allowed_value = 11.0

        # Also check that when we set a value it falls within [min, max]
        parameter.value = 5

    def test_set_maximum_allowed_value(self):
        """Test setter for maximum allowed value."""
        parameter = FloatParameter()

        with self.assertRaises(TypeError):
            parameter.maximum_allowed_value = 'One million'

        parameter.maximum_allowed_value = 1000

        parameter.maximum_allowed_value = 11.0
        # Also check that it raises an error if it precedes min
        parameter.minimum_allowed_value = 10.0

        with self.assertRaises(InvalidMaximumError):
            parameter.maximum_allowed_value = 1.0

        # Also check that when we set a value it falls within [min, max]
        parameter.value = 10.5
