# coding=utf-8
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'test_boolean_parameter_widget'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import unittest

from PyQt4.QtGui import QApplication

from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.qt_widgets.boolean_parameter_widget import (
    BooleanParameterWidget)


application = QApplication([])


class TestBooleanParameterWidget(unittest.TestCase):
    def test_init(self):
        parameter = BooleanParameter('1231231')
        parameter.name = 'Boolean'
        parameter.help_text = 'A boolean parameter'
        parameter.description = 'A test _description'
        parameter.is_required = True

        parameter.value = True

        widget = BooleanParameterWidget(parameter)

        expected_value = parameter.name
        real_value = widget._label.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = parameter.value
        real_value = widget._check_box_input.isChecked()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        # change value
        widget._check_box_input.setChecked(False)

        expected_value = False
        real_value = widget._check_box_input.isChecked()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

if __name__ == '__main__':
    unittest.main()

