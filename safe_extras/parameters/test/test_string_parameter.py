# coding=utf-8
"""Tests for string parameter."""

from unittest import TestCase

from safe_extras.parameters.string_parameter import StringParameter


class TestStringParameter(TestCase):
    def test_boolean(self):
        """Test a bool parameter works properly.

        ..versionadded:: 2.2

        """
        parameter = StringParameter('1231231')
        parameter.name = 'String parameter'
        parameter.help_text = 'A string parameter'
        parameter.description = 'A test description'
        parameter.is_required = True

        parameter.value = 'Yogyakarta'
        self.assertEqual('Yogyakarta', parameter.value)

        with self.assertRaises(TypeError):
            parameter.value = 1
