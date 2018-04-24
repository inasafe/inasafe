# coding=utf-8
"""Test class for default_select_parameter_widget."""


import unittest

from safe.common.parameters.default_select_parameter import (
    DefaultSelectParameter)
from safe.common.parameters.default_select_parameter_widget import (
    DefaultSelectParameterWidget)
from safe.definitions.constants import INASAFE_TEST

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestDefaultSelectParameterWidget(unittest.TestCase):

    """Test for DefaultSelectParameterWidget."""

    def test_init(self):
        """Test init."""
        default_select_parameter = DefaultSelectParameter()
        default_select_parameter.name = 'Default Select Affected Field'
        default_select_parameter.is_required = True
        default_select_parameter.help_text = 'Column used for affected field'
        default_select_parameter.description = (
            'Column used for affected field in the vector')
        default_select_parameter.element_type = str
        default_select_parameter.options_list = [
            'FLOODPRONE', 'affected', 'floodprone', 'yes/no',
            '\xddounicode test']
        default_select_parameter.value = 'affected'
        default_select_parameter.default_labels = [
            'Setting (%s)', 'Do not report', 'Custom']
        default_select_parameter.default_values = [0.1, None, 0.2]
        default_select_parameter.default_value = 0.1

        widget = DefaultSelectParameterWidget(default_select_parameter)

        expected_value = default_select_parameter.value
        real_value = widget.get_parameter().value
        self.assertEqual(expected_value, real_value)

        self.assertFalse(widget.custom_value.isEnabled())

    def test_set_choice(self):
        """Test for set_choice method."""
        default_select_parameter = DefaultSelectParameter()
        default_select_parameter.name = 'Default Select Affected Field'
        default_select_parameter.is_required = True
        default_select_parameter.help_text = 'Column used for affected field'
        default_select_parameter.description = (
            'Column used for affected field in the vector')
        default_select_parameter.element_type = str
        default_select_parameter.options_list = [
            'FLOODPRONE', 'affected', 'floodprone', 'yes/no',
            '\xddounicode test']
        default_select_parameter.value = 'affected'
        default_select_parameter.default_labels = [
            'Setting (%s)', 'Do not report', 'Custom']
        default_select_parameter.default_values = [0.1, None, 0.2]

        widget = DefaultSelectParameterWidget(default_select_parameter)

        expected = 'FLOODPRONE'
        widget.set_choice(expected)
        real_value = widget.get_parameter().value
        self.assertEqual(expected, real_value)

        expected = 0.1
        widget.set_default(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertFalse(widget.custom_value.isEnabled())
        self.assertEqual(widget.default_input_button_group.checkedId(), 0)
        self.assertEqual(widget.custom_value.value(), 0.2)

        expected = 0.2
        widget.set_default(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertTrue(widget.custom_value.isEnabled())
        self.assertEqual(widget.default_input_button_group.checkedId(), 2)
        self.assertEqual(widget.custom_value.value(), 0.2)

        expected = None
        widget.set_default(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertFalse(widget.custom_value.isEnabled())
        self.assertEqual(widget.default_input_button_group.checkedId(), 1)
        self.assertEqual(widget.custom_value.value(), 0.2)

        expected = 0.3
        widget.set_default(expected)
        real_value = widget.get_parameter().default
        self.assertEqual(expected, real_value)
        self.assertTrue(widget.custom_value.isEnabled())
        self.assertEqual(widget.default_input_button_group.checkedId(), 2)
        self.assertEqual(widget.custom_value.value(), 0.3)
