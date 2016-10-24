# coding=utf-8
"""Default Select Parameter Widget."""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QHBoxLayout, QGridLayout, QDoubleSpinBox,
    QRadioButton, QButtonGroup, QWidget, QLabel)

from safe_extras.parameters.qt_widgets.select_parameter_widget import (
    SelectParameterWidget)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class DefaultSelectParameterWidget(SelectParameterWidget):
    """Widget class for Default Select Parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        :param parameter: A DefaultSelectParameter object.
        :type parameter: DefaultSelectParameter

        """
        super(DefaultSelectParameterWidget, self).__init__(parameter, parent)

        self.default_layout = QHBoxLayout()
        self.radio_button_layout = QHBoxLayout()
        self.radio_button_widget = QWidget()

        self._default_label = QLabel('Use default')

        # Add label for default
        # self.radio_button_layout.addWidget(self._default_label)

        # Create radio button group
        self._default_input_button_group = QButtonGroup()

        for i in range(len(self._parameter.default_labels)):
            if '%s' in self._parameter.default_labels[i]:
                label = (
                    self._parameter.default_labels[i] %
                    self._parameter.default_values[i])
            else:
                label = self._parameter.default_labels[i]

            radio_button = QRadioButton(label)
            self.radio_button_layout.addWidget(radio_button)
            self._default_input_button_group.addButton(radio_button, i)
            if self._parameter.default_value == \
                    self._parameter.default_values[i]:
                radio_button.setChecked(True)

        # Create double spin box for custom value
        self.custom_value = QDoubleSpinBox()
        if self._parameter.default_values[-1]:
            self.custom_value.setValue(self._parameter.default_values[-1])
        self.radio_button_layout.addWidget(self.custom_value)

        self.toggle_custom_value()

        # Reset the layout
        self._input_layout.setParent(None)
        self._help_layout.setParent(None)

        self._label.setParent(None)
        self._inner_input_layout.setParent(None)

        self._input_layout = QGridLayout()
        self._input_layout.setSpacing(0)

        self._input_layout.addWidget(self._label, 0, 0)
        self._input_layout.addLayout(self._inner_input_layout, 0, 1)
        self._input_layout.addWidget(self._default_label, 1, 0)
        self._input_layout.addLayout(self.radio_button_layout, 1, 1)

        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addLayout(self._help_layout)

        # Connect
        # noinspection PyUnresolvedReferences
        self._default_input_button_group.buttonClicked.connect(
            self.toggle_custom_value)

    def raise_invalid_type_exception(self):
        message = 'Expecting element type of %s' % (
            self._parameter.element_type.__name__)
        err = ValueError(message)
        return err

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A DefaultSelectParameter from the current state of widget

        """
        current_index = self._input.currentIndex()
        selected_value = self._input.itemData(current_index, Qt.UserRole)
        if hasattr(selected_value, 'toPyObject'):
            selected_value = selected_value.toPyObject()

        try:
            self._parameter.value = selected_value
        except ValueError:
            err = self.raise_invalid_type_exception()
            raise err

        radio_button_checked_id = self._default_input_button_group.checkedId()
        # No radio button checked, then default value = None
        if radio_button_checked_id == -1:
            self._parameter.default = None
        # The last radio button (custom) is checked, get the value from the
        # line edit
        elif (radio_button_checked_id ==
                len(self._parameter.default_values) - 1):
            self._parameter.default_values[radio_button_checked_id] \
                = self.custom_value.value()
            self._parameter.default = self.custom_value.value()
        else:
            self._parameter.default = self._parameter.default_values[
                radio_button_checked_id]

        return self._parameter

    def set_default(self, default):
        """Set default value by item's string.

        :param default: The default.
        :type default: str, int

        :returns: True if success, else False.
        :rtype: bool
        """
        # Find index of choice
        try:
            default_index = self._parameter.default_values.index(default)
            self._default_input_button_group.button(default_index).setChecked(
                True)
        except ValueError:
            last_index = len(self._parameter.default_values) - 1
            self._default_input_button_group.button(last_index).setChecked(
                True)
            self.custom_value.setValue(default)

        self.toggle_custom_value()

    def toggle_custom_value(self):
        radio_button_checked_id = self._default_input_button_group.checkedId()
        if (radio_button_checked_id ==
                len(self._parameter.default_values) - 1):
            self.custom_value.setDisabled(False)
        else:
            self.custom_value.setDisabled(True)
