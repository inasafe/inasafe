# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'point_parameter_widget'
__date__ = '12/15/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''


from qt_widgets.generic_parameter_widget import GenericParameterWidget

from PyQt4.QtGui import QSpinBox, QSizePolicy


class PointParameterWidget(GenericParameterWidget):
    """Widget class for Integer parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A IntegerParameter object.
        :type parameter: IntegerParameter

        """
        # Size policy
        self._spin_box_size_policy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)

        super(PointParameterWidget, self).__init__(parameter, parent)

        self._input_x = QSpinBox()
        self._input_x.setValue(self._parameter.value[0])
        tool_tip = 'X'
        self._input_x.setToolTip(tool_tip)
        self._input_x.setSizePolicy(self._spin_box_size_policy)

        self._input_y = QSpinBox()
        self._input_y.setValue(self._parameter.value[1])
        tool_tip = 'Y'
        self._input_y.setToolTip(tool_tip)
        self._input_y.setSizePolicy(self._spin_box_size_policy)

        self._inner_input_layout.addWidget(self._input_x)
        self._inner_input_layout.addWidget(self._input_y)

    def get_parameter(self):
        """Obtain boolean parameter object from the current widget state.

        :returns: A BooleanParameter from the current state of widget

        """
        self._parameter.value = (self._input_x.value(), self._input_y.value())
        return self._parameter
