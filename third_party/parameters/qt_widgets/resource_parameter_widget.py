# coding=utf-8
"""Docstring for this file."""
__author__ = 'Christian Christelis christian@kartoza.com'
__project_name = 'parameters'
__filename = 'float_parameter_widget'
__date__ = '12/11/14'
__copyright__ = 'kartoza.com'
__doc__ = ''

from float_parameter_widget import FloatParameterWidget


class ResourceParameterWidget(FloatParameterWidget):
    """Widget class for Resource parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.3

        :param parameter: A ResourceParameter object.
        :type parameter: ResourceParameter

        """
        super(ResourceParameterWidget, self).__init__(parameter, parent)
