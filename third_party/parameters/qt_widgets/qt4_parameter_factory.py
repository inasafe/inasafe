# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'qt4_parameter_factory'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

from boolean_parameter_widget import BooleanParameterWidget
from float_parameter_widget import FloatParameterWidget
from integer_parameter_widget import IntegerParameterWidget
from string_parameter_widget import StringParameterWidget
from resource_parameter_widget import ResourceParameterWidget


class Qt4ParameterFactory(object):
    """A factory class that will generate a widget given a parameter."""

    def __init__(self):
        """Constructor."""
        pass


    @staticmethod
    def get_widget(parameter):
        """Create parameter widget from current
        :param parameter: Parameter object.
        :type parameter: BooleanParameter, FloatParameter, IntegerParameter,
            StringParameter

        :returns: Widget of given parameter.
        :rtype: BooleanParameterWidget, FloatParameterWidget,
            IntegerParameterWidget, StringParameterWidget
        """
        class_name = parameter.__class__.__name__

        if class_name == 'BooleanParameter':
            return BooleanParameterWidget(parameter)
        elif class_name == 'FloatParameter':
            return FloatParameterWidget(parameter)
        elif class_name == 'IntegerParameter':
            return IntegerParameterWidget(parameter)
        elif class_name == 'StringParameter':
            return StringParameterWidget(parameter)
        elif class_name == 'ResourceParameter':
            return ResourceParameterWidget(parameter)
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
