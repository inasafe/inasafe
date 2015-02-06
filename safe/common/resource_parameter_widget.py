# coding=utf-8
"""Docstring for this file."""
__author__ = 'Christian Christelis christian@kartoza.com'
__project_name = 'parameters'
__filename = 'float_parameter_widget'
__date__ = '12/11/14'
__copyright__ = 'kartoza.com'
__doc__ = ''

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtGui import QLabel

from safe_extras.parameters.qt_widgets.float_parameter_widget import (
    FloatParameterWidget)


class ResourceParameterWidget(FloatParameterWidget):
    """Widget class for Resource parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.3

        :param parameter: A ResourceParameter object.
        :type parameter: ResourceParameter, FloatParameter

        """
        # pylint: disable=E1002
        super(ResourceParameterWidget, self).__init__(parameter, parent)
        # pylint: enable=E1002
        self.set_unit()

    def get_parameter(self):
        """Obtain the parameter object from the current widget state.

        :returns: A BooleanParameter from the current state of widget

        """
        self._parameter.value = self._input.value()
        return self._parameter

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
