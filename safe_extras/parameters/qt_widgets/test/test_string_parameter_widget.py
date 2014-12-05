# coding=utf-8
"""Docstring for this test file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'test_string_parameter_widget.py'
__date__ = '8/28/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import unittest


from PyQt4.QtGui import QApplication

from safe_extras.parameters.string_parameter import StringParameter
from safe_extras.parameters.qt_widgets.string_parameter_widget import (
    StringParameterWidget)


application = QApplication([])


class TestBooleanParameterWidget(unittest.TestCase):
    def test_init(self):
        string_parameter = StringParameter('28082014')
        string_parameter.name = 'Province Name'
        string_parameter.help_text = 'Name of province.'
        string_parameter.description = (
            'A <b>test _description</b> that is very long so that you need to '
            'read it for one minute and you will be tired after read this '
            'description. You are the best user so far. Even better if you '
            'read this description loudly so that all of your friends will '
            'be able to hear you')
        string_parameter.is_required = True
        string_parameter.value = 'Daerah Istimewa Yogyakarta'

        widget = StringParameterWidget(string_parameter)

        expected_value = string_parameter.name
        real_value = widget._label.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = string_parameter.value
        real_value = widget._line_edit_input.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        # change value
        widget._line_edit_input.setText('Nusa Tenggara Barat')

        expected_value = 'Nusa Tenggara Barat'
        real_value = widget._line_edit_input.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

if __name__ == '__main__':
    unittest.main()

