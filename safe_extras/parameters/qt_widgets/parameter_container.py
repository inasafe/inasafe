# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'parameter_container'
__date__ = '8/22/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

from PyQt4.QtGui import (
    QWidget, QScrollArea, QVBoxLayout, QGridLayout, QSizePolicy, QColor)
from qt4_parameter_factory import Qt4ParameterFactory


class ParameterContainer(QWidget, object):
    """Container to hold Parameter Widgets."""

    def __init__(self, parameters, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameters: List of Parameter Widget
        :type parameters: list

        """
        QWidget.__init__(self, parent)

        self._parameters = parameters

        # Vertical layout to place the parameter widgets
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setSpacing(0)

        # Widget to hold the vertical layout
        self.widget = QWidget()
        self.widget.setLayout(self.vertical_layout)

        # Scroll area to make the container scroll-able
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setSizePolicy(QSizePolicy.Expanding)
        self.scroll_area.setWidget(self.widget)

        # Main layout of the container
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        qt4_parameter_factory = Qt4ParameterFactory()
        color_odd = QColor(220, 220, 220)
        color_even = QColor(192, 192, 192)

        i = 0
        for parameter in parameters:
            parameter_widget = qt4_parameter_factory.get_widget(parameter)
            if i % 2:
                color = color_even
            else:
                color = color_odd
            i += 1
            parameter_widget.setAutoFillBackground(True)
            palette = parameter_widget.palette()
            palette.setColor(parameter_widget.backgroundRole(), color)
            parameter_widget.setPalette(palette)
            self.vertical_layout.addWidget(parameter_widget)

    def get_parameters(self):
        """Return list of parameters from the current state of widget.

        :returns: List of parameter
        :rtype: list
        """

        parameter_widgets = (self.vertical_layout.itemAt(i) for i in range(
            self.vertical_layout.count()))

        parameters = []

        for widget_item in parameter_widgets:
            parameter_widget = widget_item.widget()

            parameter = parameter_widget.get_parameter()
            parameters.append(parameter)

        return parameters
