# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'numeric_parameter_widget'
__date__ = '8/21/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

# noinspection PyPackageRequirements
from PyQt4.QtGui import QLabel, QSizePolicy, QWidget, QComboBox
# noinspection PyPackageRequirements
from PyQt4.QtCore import Qt

from generic_parameter_widget import GenericParameterWidget


class NumericParameterWidget(GenericParameterWidget):
    """Widget class for Numeric parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A NumericParameter object.
        :type parameter: NumericParameter

        """
        super(NumericParameterWidget, self).__init__(parameter, parent)

        self._input = QWidget()

        self._unit_widget = QLabel()
        self.set_unit()

        # Size policy
        self._spin_box_size_policy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)

        label_policy = QSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._unit_widget.setSizePolicy(label_policy)

        # Add unit description to description
        description = self._description_label.text()
        description += '<br><br>Available units:'
        description += '<ul>'
        for allowed_unit in self._parameter.allowed_units:
            description += '<li>'
            description += '<b>' + allowed_unit.name + '</b>: '
            description += allowed_unit.description
            description += '</li>'
        description += '</ul>'
        self._description_label.setText(description)

    def get_parameter(self):
        """Obtain boolean parameter object from the current widget state.

        :returns: A BooleanParameter from the current state of widget

        """
        self._parameter.value = self._input.value()
        if len(self._parameter.allowed_units) > 1:
            current_index = self._unit_widget.currentIndex()
            unit = self._unit_widget.itemData(current_index, Qt.UserRole)
            if hasattr(unit, 'toPyObject'):
                unit = unit.toPyObject()
            self._parameter.unit = unit
        return self._parameter

    def set_unit(self):
        """Set up label or combo box for unit."""
        if len(self._parameter.allowed_units) == 1:
            self._unit_widget = QLabel(self._parameter.unit.name)
            self._unit_widget.setToolTip(self._parameter.unit.help_text)
        elif len(self._parameter.allowed_units) > 1:
            self._unit_widget = QComboBox()
            index = -1
            current_index = -1
            for allowed_unit in self._parameter.allowed_units:
                name = allowed_unit.name
                tooltip = allowed_unit.help_text
                index += 1
                if allowed_unit.guid == self._parameter.unit.guid:
                    current_index = index
                self._unit_widget.addItem(name)
                self._unit_widget.setItemData(index, tooltip, Qt.ToolTipRole)
                self._unit_widget.setItemData(index, allowed_unit, Qt.UserRole)
            self._unit_widget.setCurrentIndex(current_index)
            self._unit_widget.setToolTip('Select your preferred unit')
            self._unit_widget.currentIndex()

    def set_value(self, value):
        """Set the value of the input

        :param value: The new value
        :type value: int, float
        """
        self._input.setValue(value)
