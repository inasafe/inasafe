# coding=utf-8
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'test_qt4_parameter_factory'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import unittest

from PyQt4.QtGui import QApplication

from safe_extras.parameters.qt_widgets.qt4_parameter_factory import (
    Qt4ParameterFactory)
from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.qt_widgets.boolean_parameter_widget import (
    BooleanParameterWidget)
from safe_extras.parameters.qt_widgets.float_parameter_widget import (
    FloatParameterWidget)


application = QApplication([])


class TestQt4ParameterFactory(unittest.TestCase):
    def test_init(self):
        """Test initialize qt4 parameter factory."""

        boolean_parameter = BooleanParameter('1231231')
        boolean_parameter.name = 'Boolean'
        boolean_parameter.help_text = 'A boolean parameter'
        boolean_parameter.description = 'A test _description'
        boolean_parameter.is_required = True
        boolean_parameter.value = True

        float_parameter = FloatParameter()
        float_parameter.name = 'Float Parameter'
        float_parameter.is_required = True
        float_parameter.precision = 3
        float_parameter.minimum_allowed_value = 1.0
        float_parameter.maximum_allowed_value = 2.0
        float_parameter.help_text = 'Short help.'
        float_parameter.description = 'Long description for parameter.'
        float_parameter.unit = 'metres'
        float_parameter.value = 1.1

        parameters = [boolean_parameter, float_parameter]

        qt4_parameter_factory = Qt4ParameterFactory()
        widgets = []
        widget_classes = []

        for parameter in parameters:
            widget = qt4_parameter_factory.get_widget(parameter)
            widgets.append(widget)
            widget_classes.append(widget.__class__)

        expected_classes = [BooleanParameterWidget, FloatParameterWidget]
        message = 'Expected %s got %s' % (expected_classes, widget_classes)
        self.assertListEqual(widget_classes, expected_classes, message)


if __name__ == '__main__':
    unittest.main()

