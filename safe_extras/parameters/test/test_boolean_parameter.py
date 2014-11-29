# coding=utf-8
"""Tests for boolean parameter."""
from unittest import TestCase
from safe_extras.parameters.boolean_parameter import BooleanParameter


class TestBooleanParameter(TestCase):

    def test_boolean(self):
        """Test a bool parameter works properly.

        .. versionadded:: 2.2

        """
        parameter = BooleanParameter('1231231')
        parameter.name = 'Boolean'
        parameter.help_text = 'A boolean parameter'
        parameter.description = 'A test _description'
        parameter.is_required = True

        parameter.value = True
        self.assertEqual(True, parameter.value)

        with self.assertRaises(TypeError):
            parameter.value = 'Test'


