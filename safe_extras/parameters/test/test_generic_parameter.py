# coding=utf-8
"""Tests for generic parameter."""

from unittest import TestCase

from safe_extras.parameters.generic_parameter import GenericParameter


class TestGenericParameter(TestCase):
    """Test generic parameter."""
    def test_guid(self):
        """Test mutator for guid."""
        guid = '1213231'
        parameter = GenericParameter()
        parameter.guid = guid
        self.assertEqual(guid, parameter.guid)
        parameter = GenericParameter(guid)
        self.assertEqual(guid, parameter.guid)

    def test_name(self):
        """Test mutator for name."""
        name = 'Foo'
        parameter = GenericParameter()
        parameter.name = name
        self.assertEqual(name, parameter.name)

    def test_expected_type(self):
        """Test mutator for expected type."""
        parameter_type = int
        parameter = GenericParameter()
        parameter.type = parameter_type
        self.assertEqual(parameter_type, parameter.type)

    def test_is_required(self):
        """Test mutator for is_required."""
        flag = True
        parameter = GenericParameter()
        parameter.is_required = flag
        self.assertEqual(flag, parameter.is_required)

    def test_help_text(self):
        """Test mutator for help text."""
        help_text = 'Foo'
        parameter = GenericParameter()
        parameter.help_text = help_text
        self.assertEqual(help_text, parameter.help_text)

    def test_set_description(self):
        """Test mutator for description."""
        help_description = 'Foo'
        parameter = GenericParameter()
        parameter.description = help_description
        self.assertEqual(help_description, parameter.description)

    def test_set_value(self):
        value = 'Foo'
        parameter = GenericParameter()
        parameter.type = str
        parameter.value = value
        self.assertEqual(value, parameter.value)
