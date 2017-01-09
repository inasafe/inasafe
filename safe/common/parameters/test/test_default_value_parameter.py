# coding=utf-8
"""Tests for default value parameter."""

from unittest import TestCase

from safe.common.parameters.default_value_parameter import (
    DefaultValueParameter)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

default_labels = ['Setting', 'Do not use', 'Custom']
default_values = [0.1, None]


class TestDefaultValueParameter(TestCase):
    """Test For Default Value Parameter."""

    def setUp(self):

        self.parameter = DefaultValueParameter()

        self.parameter.default_labels = default_labels
        self.parameter.default_values = default_values

    def test_default_value(self):
        """Test default value."""
        self.assertEqual(self.parameter.default_labels, default_labels)
        self.parameter.default_value = 0.2
        self.assertEqual(
            self.parameter.default_values[-1], self.parameter.default_value)
