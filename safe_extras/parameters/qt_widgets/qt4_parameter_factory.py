# coding=utf-8
"""Docstring for this file."""

__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'qt4_parameter_factory'
__date__ = '8/19/14'
__copyright__ = 'ismail@kartoza.com'
__doc__ = ''

from qt_widgets.boolean_parameter_widget import BooleanParameterWidget
from qt_widgets.float_parameter_widget import FloatParameterWidget
from qt_widgets.integer_parameter_widget import IntegerParameterWidget
from qt_widgets.string_parameter_widget import StringParameterWidget
from qt_widgets.generic_parameter_widget import GenericParameterWidget
from qt_widgets.list_parameter_widget import ListParameterWidget
from qt_widgets.input_list_parameter_widget import InputListParameterWidget
from qt_widgets.dict_parameter_widget import DictParameterWidget


class Qt4ParameterFactory(object):
    """A factory class that will generate a widget given a parameter."""

    def __init__(self):
        """Constructor."""
        self.dict_widget = {
            'BooleanParameter': BooleanParameterWidget,
            'FloatParameter': FloatParameterWidget,
            'IntegerParameter': IntegerParameterWidget,
            'StringParameter': StringParameterWidget,
            'ListParameter': ListParameterWidget,
            'InputListParameter': InputListParameterWidget,
            'DictParameter': DictParameterWidget
        }

    def register_widget(self, parameter, parameter_widget):
        """Register new custom widget.

        :param parameter:
        :type parameter: GenericParameter

        :param parameter_widget:
        :type parameter_widget: GenericParameterWidget
        """
        self.dict_widget[parameter.__name__] = parameter_widget

    def remove_widget(self, parameter):
        """Register new custom widget.

        :param parameter:
        :type parameter: GenericParameter
        """
        if parameter.__name__ in self.dict_widget.keys():
            self.dict_widget.pop(parameter.__name__)

    def get_widget(self, parameter):
        """Create parameter widget from current
        :param parameter: Parameter object.
        :type parameter: BooleanParameter, FloatParameter, IntegerParameter,
            StringParameter

        :returns: Widget of given parameter.
        :rtype: BooleanParameterWidget, FloatParameterWidget,
            IntegerParameterWidget, StringParameterWidget
        """
        class_name = parameter.__class__.__name__

        if class_name in self.dict_widget.keys():
            return self.dict_widget[class_name](parameter)
        else:
            raise TypeError(class_name)

    @staticmethod
    def get_parameter(widget):
        """Obtain parameter object from parameter widget current state.

        :param widget: An object of a ParameterWidget.
        :type widget: GenericParameterWidget

        :returns: Parameter object
        :rtype: GenericParameter

        """
        return widget.get_parameter()
