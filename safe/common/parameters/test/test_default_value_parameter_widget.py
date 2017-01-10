# coding=utf-8
"""Test class for default_value_parameter_widget."""


import unittest

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.common.parameters.default_value_parameter import (
    DefaultValueParameter)
from safe.common.parameters.default_value_parameter_widget import (
    DefaultValueParameterWidget)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestDefaultValueParameterWidget(unittest.TestCase):
    """Test for DefaultSelectParameterWidget"""
    def test_init(self):
        default_value_parameter = DefaultValueParameter()
        default_value_parameter.name = 'Default Value Affected Field'
        default_value_parameter.is_required = True
        default_value_parameter.help_text = 'Default value for affected field'
        default_value_parameter.description = (
            'Value to be used for affected field.')
        default_value_parameter.element_type = str
        default_value_parameter.labels = [
            'Setting (%s)', 'Do not use', 'Custom']
        default_value_parameter.options = [0.1, None, 0.2]
        default_value_parameter.value = 0.1

        widget = DefaultValueParameterWidget(default_value_parameter)

        expected_value = default_value_parameter.value
        real_value = widget.get_parameter().value
        self.assertEqual(expected_value, real_value)

        self.assertFalse(widget.custom_value.isEnabled())

    def test_set_choice(self):
        """Test for set_choice method."""
        default_value_parameter = DefaultValueParameter()
        default_value_parameter.name = 'Default Value Affected Field'
        default_value_parameter.is_required = True
        default_value_parameter.help_text = 'Default value for affected field'
        default_value_parameter.description = (
            'Value to be used for affected field.')
        default_value_parameter.element_type = str
        default_value_parameter.labels = [
            'Setting (%s)', 'Do not use', 'Custom']
        default_value_parameter.options = [0.1, None, 0.2]
        default_value_parameter.default_value = 0.1

        widget = DefaultValueParameterWidget(default_value_parameter)

        expected = 0.1
        widget.set_value(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertFalse(widget.custom_value.isEnabled())
        self.assertEqual(widget._input_button_group.checkedId(), 0)
        self.assertEqual(widget.custom_value.value(), 0.2)

        expected = 0.2
        widget.set_value(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertTrue(widget.custom_value.isEnabled())
        self.assertEqual(widget._input_button_group.checkedId(), 2)
        self.assertEqual(widget.custom_value.value(), 0.2)

        expected = None
        widget.set_value(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertFalse(widget.custom_value.isEnabled())
        self.assertEqual(widget._input_button_group.checkedId(), 1)
        self.assertEqual(widget.custom_value.value(), 0.2)

        expected = 0.3
        widget.set_value(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertTrue(widget.custom_value.isEnabled())
        self.assertEqual(widget._input_button_group.checkedId(), 2)
        self.assertEqual(widget.custom_value.value(), 0.3)
