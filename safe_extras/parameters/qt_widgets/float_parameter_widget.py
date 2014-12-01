# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'float_parameter_widget'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

from PyQt4.QtGui import QDoubleSpinBox

from numeric_parameter_widget import NumericParameterWidget


class FloatParameterWidget(NumericParameterWidget):
    """Widget class for Float parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A FloatParameter object.
        :type parameter: FloatParameter

        """
        super(FloatParameterWidget, self).__init__(parameter, parent)

        self._input = QDoubleSpinBox()
        self._input.setDecimals(self._parameter.precision)
        self._input.setValue(self._parameter.value)
        self._input.setMinimum(
            self._parameter.minimum_allowed_value)
        self._input.setMaximum(
            self._parameter.maximum_allowed_value)
        self._input.setSingleStep(
            10 ** -self._parameter.precision)
        # is it possible to use dynamic precision ?
        string_min_value = '%.*f' % (
            self._parameter.precision, self._parameter.minimum_allowed_value)
        string_max_value = '%.*f' % (
            self._parameter.precision, self._parameter.maximum_allowed_value)
        tool_tip = 'Choose a number between %s and %s' % (
            string_min_value, string_max_value)
        self._input.setToolTip(tool_tip)

        self._input.setSizePolicy(self._spin_box_size_policy)

        self._inner_input_layout.addWidget(self._input)
        self._inner_input_layout.addWidget(self._unit_widget)
