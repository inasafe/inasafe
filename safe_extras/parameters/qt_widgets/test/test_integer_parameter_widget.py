# coding=utf-8
"""Docstring for this test file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'test_integer_parameter_widget'
__date__ = '8/21/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import unittest

from PyQt4.QtGui import QApplication

from safe_extras.parameters.integer_parameter import IntegerParameter
from safe_extras.parameters.qt_widgets.integer_parameter_widget import (
    IntegerParameterWidget)
from safe_extras.parameters.metadata import unit_metres_depth, unit_feet_depth
from safe_extras.parameters.unit import Unit


application = QApplication([])


class TestFloatParameterWidget(unittest.TestCase):
    def test_init(self):

        unit_feet = Unit('130790')
        unit_feet.load_dictionary(unit_feet_depth)

        unit_metres = Unit('900713')
        unit_metres.load_dictionary(unit_metres_depth)

        integer_parameter = IntegerParameter()
        integer_parameter.name = 'Paper'
        integer_parameter.is_required = True
        integer_parameter.minimum_allowed_value = 1
        integer_parameter.maximum_allowed_value = 5
        integer_parameter.help_text = 'Number of paper'
        integer_parameter.description = (
            'A <b>test _description</b> that is very long so that you need '
            'to read it for one minute and you will be tired after read this '
            'description. You are the best user so far. Even better if you '
            'read this description loudly so that all of your friends will be '
            'able to hear you')
        integer_parameter.unit = unit_feet
        integer_parameter.allowed_units = [unit_feet]
        integer_parameter.value = 3

        widget = IntegerParameterWidget(integer_parameter)

        expected_value = integer_parameter.name
        real_value = widget._label.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = integer_parameter.value
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(1.5)

        expected_value = 1
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(1.55555)

        expected_value = 1
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(7)

        expected_value = 5
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = 'QLabel'
        real_value = widget._unit_widget.__class__.__name__
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = 'feet'
        real_value = widget._unit_widget.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

if __name__ == '__main__':
    unittest.main()
