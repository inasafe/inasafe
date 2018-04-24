# coding=utf-8
"""Test class for percentage_parameter_widget."""

import unittest
from parameters.float_parameter import FloatParameter
from safe.common.parameters.percentage_parameter_widget import (
    PercentageSpinBox,
    PercentageParameterWidget,
)

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPercentageParameterWidget(unittest.TestCase):

    """Test for PercentageParameterWidget."""

    def test_init(self):
        """Test init."""

        float_parameter = FloatParameter()
        float_parameter.name = 'Female Ratio.'
        float_parameter.is_required = True
        float_parameter.minimum_allowed_value = 0
        float_parameter.maximum_allowed_value = 1
        float_parameter.help_text = 'The percentage of female..'
        float_parameter.description = (
            'A <b>test _description</b> that is very long so that you need '
            'to read it for one minute and you will be tired after read this '
            'description. You are the best user so far. Even better if you '
            'read this description loudly so that all of your friends will be '
            'able to hear you')
        float_parameter.value = 0.5

        widget = PercentageParameterWidget(float_parameter)

        expected_value = float_parameter.name
        real_value = widget.label.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = float_parameter.value
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(1.5)

        expected_value = 1
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(0.55555)

        expected_value = 0.556
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(-7)

        expected_value = 0
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = 'PercentageSpinBox'
        real_value = widget._input.__class__.__name__
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

    def test_percentage_spinbox(self):
        """Test percentage spinbox class."""
        spin_box = PercentageSpinBox(PARENT)
        decimal_separator = spin_box.locale().decimalPoint()
        spin_box.setValue(0.5)
        expected = '50.0 %'.replace('.', decimal_separator)
        self.assertEqual(spin_box.text(), expected)
        self.assertEqual(spin_box.value(), 0.5)

        spin_box.setValue(10)
        expected = '100.0 %'.replace('.', decimal_separator)
        self.assertEqual(spin_box.text(), expected)
        self.assertEqual(spin_box.value(), 1)

        spin_box.setValue(-1)
        expected = '0.0 %'.replace('.', decimal_separator)
        self.assertEqual(spin_box.text(), expected)
        self.assertEqual(spin_box.value(), 0)

        spin_box.setValue(0.112357)
        expected = '11.2 %'.replace('.', decimal_separator)
        self.assertEqual(spin_box.text(), expected)
        self.assertAlmostEqual(spin_box.value(), 0.112)


if __name__ == '__main__':
    unittest.main()
