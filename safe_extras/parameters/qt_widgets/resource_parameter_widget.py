# coding=utf-8
"""Docstring for this file."""
__author__ = 'Christian Christelis christian@kartoza.com'
__project_name = 'parameters'
__filename = 'float_parameter_widget'
__date__ = '12/11/14'
__copyright__ = 'kartoza.com'
__doc__ = ''

from float_parameter_widget import FloatParameterWidget
# noinspection PyPackageRequirements
from PyQt4.QtGui import QLabel


class ResourceParameterWidget(FloatParameterWidget):
    """Widget class for Resource parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.3

        :param parameter: A ResourceParameter object.
        :type parameter: ResourceParameter

        """
        super(ResourceParameterWidget, self).__init__(parameter, parent)

    def set_unit(self):
        """Set the units label. (Include the frequency.)"""
        label = ''
        if self._parameter.frequency:
            label = self._parameter.frequency
        if self._parameter.unit.plural:
            label = '%s %s' % (self._parameter.unit.plural, label)
        elif self._parameter.unit.name:
            label = '%s %s' % (self._parameter.unit.name, label)
        self._unit_widget = QLabel(label)
        if self._parameter.unit.help_text:
            self._unit_widget.setToolTip(self._parameter.unit.help_text)
