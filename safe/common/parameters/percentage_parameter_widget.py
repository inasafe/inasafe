# coding=utf-8
"""Percentage Parameter Widget."""
from qgis.PyQt.QtWidgets import QDoubleSpinBox

from parameters.qt_widgets.float_parameter_widget import FloatParameterWidget

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class PercentageParameterWidget(FloatParameterWidget):

    """Percentage Parameter Widget."""

    def __init__(self, parameter, parent=None):
        """Constructor

        :param parameter: A FloatParameter object.
        :type parameter: FloatParameter
        """
        super(FloatParameterWidget, self).__init__(parameter, parent)

        self.inner_input_layout.removeWidget(self._input)
        self._input.deleteLater()
        self.inner_input_layout.removeWidget(self._unit_widget)

        self._input = PercentageSpinBox(self)
        self._input.setValue(self._parameter.value)
        if 1 > self._parameter.minimum_allowed_value > 0:
            self._input.setMinimum(self._parameter.minimum_allowed_value)
        if 1 > self._parameter.maximum_allowed_value > 0:
            self._input.setMaximum(self._parameter.maximum_allowed_value)
        self._input.setSizePolicy(self._spin_box_size_policy)

        self.inner_input_layout.addWidget(self._input)
        self.inner_input_layout.addWidget(self._unit_widget)


class PercentageSpinBox(QDoubleSpinBox):

    """Custom Spinbox for percentage 0 % - 100 %."""

    def __init__(self, parent):
        """Constructor."""
        super(PercentageSpinBox, self).__init__(parent)
        self.setRange(0.0, 100.0)
        self.setSingleStep(0.1)
        self.setDecimals(1)
        self.setSuffix(' %')

    def setValue(self, p_float):
        """Override method to set a value to show it as 0 to 100.

        :param p_float: The float number that want to be set.
        :type p_float: float
        """
        p_float = p_float * 100

        super(PercentageSpinBox, self).setValue(p_float)

    def value(self):
        """Override method to get a value to to 0.0 to 1.0

        :returns: The float number that want to be set.
        :rtype: float
        """
        return super(PercentageSpinBox, self).value() / 100
