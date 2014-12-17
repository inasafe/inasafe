# coding=utf-8
"""Test class for qt4_parameter_factory."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'test_qt4_parameter_factory'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import unittest

from PyQt4.QtGui import QApplication

from qt_widgets.qt4_parameter_factory import Qt4ParameterFactory
from boolean_parameter import BooleanParameter
from float_parameter import FloatParameter
from qt_widgets.boolean_parameter_widget import BooleanParameterWidget
from qt_widgets.float_parameter_widget import FloatParameterWidget

from custom_parameter.point_parameter import PointParameter
from custom_parameter.point_parameter_widget import PointParameterWidget

application = QApplication([])


class TestQt4ParameterFactory(unittest.TestCase):

    def setUp(self):
        """SetUp for unit test."""
        self.boolean_parameter = BooleanParameter('1231231')
        self.boolean_parameter.name = 'Boolean'
        self.boolean_parameter.help_text = 'A boolean parameter'
        self.boolean_parameter.description = 'A test _description'
        self.boolean_parameter.is_required = True
        self.boolean_parameter.value = True

        self.float_parameter = FloatParameter()
        self.float_parameter.name = 'Float Parameter'
        self.float_parameter.is_required = True
        self.float_parameter.precision = 3
        self.float_parameter.minimum_allowed_value = 1.0
        self.float_parameter.maximum_allowed_value = 2.0
        self.float_parameter.help_text = 'Short help.'
        self.float_parameter.description = 'Long description for parameter.'
        self.float_parameter.unit = 'metres'
        self.float_parameter.value = 1.1

        self.point_parameter = PointParameter()
        self.point_parameter.name = 'Point Parameter'
        self.point_parameter.is_required = True
        self.point_parameter.help_text = 'Short help.'
        self.point_parameter.description = 'Long description for parameter.'
        self.point_parameter.value = (0, 1)

    def test_init(self):
        """Test initialize qt4 parameter factory."""
        parameters = [self.boolean_parameter, self.float_parameter]

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

    def test_custom_parameter(self):
        """Test adding new custom parameter to the factory"""
        qt4_parameter_factory = Qt4ParameterFactory()
        qt4_parameter_factory.register_widget(
            PointParameter, PointParameterWidget)

        parameters = [
            self.boolean_parameter, self.float_parameter, self.point_parameter]

        widgets = []
        widget_classes = []

        for parameter in parameters:
            widget = qt4_parameter_factory.get_widget(parameter)
            widgets.append(widget)
            widget_classes.append(widget.__class__)

        expected_classes = [
            BooleanParameterWidget, FloatParameterWidget, PointParameterWidget]
        message = 'Expected %s got %s' % (expected_classes, widget_classes)
        self.assertListEqual(widget_classes, expected_classes, message)

if __name__ == '__main__':
    unittest.main()
