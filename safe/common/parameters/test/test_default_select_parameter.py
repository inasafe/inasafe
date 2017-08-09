# coding=utf-8
"""Tests for default select parameter."""

from unittest import TestCase

from parameters.parameter_exceptions import ValueNotAllowedException

from safe.common.parameters.default_select_parameter import (
    DefaultSelectParameter)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

selected = 'one'
options = ['one', 'two', 'three', 'four', 'five']
default_labels = ['Setting', 'Do not report', 'Custom']
default_values = [0.1, None]


class TestDefaultSelectParameter(TestCase):

    """Test For Default Select Parameter."""

    def setUp(self):
        """Setup common thing for test."""
        self.parameter = DefaultSelectParameter()

        self.parameter.options_list = options
        self.parameter.default_labels = default_labels
        self.parameter.default_values = default_values

    def test_set_value(self):
        """Test set value."""
        self.parameter.value = selected
        self.assertEqual(selected, self.parameter.value)
        with self.assertRaises(ValueNotAllowedException):
            self.parameter.value = 'six'

    def test_default(self):
        """Test default value."""
        self.assertEqual(self.parameter.default_labels, default_labels)
        self.parameter.default_value = 0.2
        self.assertEqual(
            self.parameter.default_values[-1], self.parameter.default_value)
