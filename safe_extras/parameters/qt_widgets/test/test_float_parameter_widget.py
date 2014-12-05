# coding=utf-8
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'test_float_parameter_widget'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import unittest

from PyQt4.QtGui import QApplication

from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.qt_widgets.float_parameter_widget import (
    FloatParameterWidget)
from safe_extras.parameters.metadata import unit_metres_depth, unit_feet_depth
from safe_extras.parameters.unit import Unit


application = QApplication([])


class TestFloatParameterWidget(unittest.TestCase):
    def test_init(self):

        unit_feet = Unit('130790')
        unit_feet.load_dictionary(unit_feet_depth)

        unit_metres = Unit('900713')
        unit_metres.load_dictionary(unit_metres_depth)

        float_parameter = FloatParameter()
        float_parameter.name = 'Flood Depth'
        float_parameter.is_required = True
        float_parameter.precision = 3
        float_parameter.minimum_allowed_value = 1.0
        float_parameter.maximum_allowed_value = 2.0
        float_parameter.help_text = 'The depth of flood.'
        float_parameter.description = (
            'A <b>test _description</b> that is very long so that you need '
            'to read it for one minute and you will be tired after read this '
            'description. You are the best user so far. Even better if you '
            'read this description loudly so that all of your friends will be '
            'able to hear you')
        float_parameter.unit = unit_feet
        float_parameter.allowed_units = [unit_metres, unit_feet]
        float_parameter.value = 1.12

        widget = FloatParameterWidget(float_parameter)

        expected_value = float_parameter.name
        real_value = widget._label.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = float_parameter.value
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(1.5)

        expected_value = 1.5
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(1.55555)

        expected_value = 1.556
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget._input.setValue(7)

        expected_value = 2
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = 'QComboBox'
        real_value = widget._unit_widget.__class__.__name__
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = 'feet'
        real_value = widget.get_parameter().unit.name
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = 'metres'
        widget._unit_widget.setCurrentIndex(0)
        real_value = widget.get_parameter().unit.name
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

if __name__ == '__main__':
    unittest.main()
