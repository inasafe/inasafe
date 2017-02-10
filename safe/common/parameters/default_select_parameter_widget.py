# coding=utf-8
"""Default Select Parameter Widget."""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QHBoxLayout, QGridLayout, QDoubleSpinBox,
    QRadioButton, QButtonGroup, QWidget, QLabel)
from safe.utilities.i18n import tr

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

        self.default_label = QLabel(tr('Default'))

        # Create radio button group
        self.default_input_button_group = QButtonGroup()

        for i in range(len(self._parameter.default_labels)):
            if '%s' in self._parameter.default_labels[i]:
                label = (
                    self._parameter.default_labels[i] %
                    self._parameter.default_values[i])
            else:
                label = self._parameter.default_labels[i]

            radio_button = QRadioButton(label)
            self.radio_button_layout.addWidget(radio_button)
            self.default_input_button_group.addButton(radio_button, i)
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
        self.input_layout.setParent(None)
        self.help_layout.setParent(None)

        self.label.setParent(None)
        self.inner_input_layout.setParent(None)

        self.input_layout = QGridLayout()
        self.input_layout.setSpacing(0)

        self.input_layout.addWidget(self.label, 0, 0)
        self.input_layout.addLayout(self.inner_input_layout, 0, 1)
        self.input_layout.addWidget(self.default_label, 1, 0)
        self.input_layout.addLayout(self.radio_button_layout, 1, 1)

        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.help_layout)

        # Connect
        # noinspection PyUnresolvedReferences
        self.input.currentIndexChanged.connect(self.toggle_input)
        self.default_input_button_group.buttonClicked.connect(
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
        current_index = self.input.currentIndex()
        selected_value = self.input.itemData(current_index, Qt.UserRole)
        if hasattr(selected_value, 'toPyObject'):
            selected_value = selected_value.toPyObject()

        try:
            self._parameter.value = selected_value
        except ValueError:
            err = self.raise_invalid_type_exception()
            raise err

        radio_button_checked_id = self.default_input_button_group.checkedId()
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
            self.default_input_button_group.button(default_index).setChecked(
                True)
        except ValueError:
            last_index = len(self._parameter.default_values) - 1
            self.default_input_button_group.button(last_index).setChecked(
                True)
            self.custom_value.setValue(default)

        self.toggle_custom_value()

    def toggle_custom_value(self):
        radio_button_checked_id = self.default_input_button_group.checkedId()
        if (radio_button_checked_id ==
                len(self._parameter.default_values) - 1):
            self.custom_value.setDisabled(False)
        else:
            self.custom_value.setDisabled(True)

    def toggle_input(self):
        """Change behaviour of radio button based on input."""
        # If input is a field, then disable all radio button.
        current_index = self.input.currentIndex()
        if self.input.itemData(current_index, Qt.UserRole) != (
                self.input.itemData(0, Qt.UserRole)):
            checked = self.default_input_button_group.checkedButton()
            if checked:
                self.default_input_button_group.setExclusive(False)
                checked.setChecked(False)
                self.default_input_button_group.setExclusive(True)
            for button in self.default_input_button_group.buttons():
                button.setDisabled(True)
            self.custom_value.setDisabled(True)
        # Otherwise, enable all radio button set selected radio button to
        # 'Do not use'.
        else:
            for button in self.default_input_button_group.buttons():
                button.setEnabled(True)
            self.set_selected_radio_button()
            self.custom_value.setEnabled(True)

    def set_selected_radio_button(self):
        """Set selected radio button to 'Do not use'."""
        dont_use_button = self.default_input_button_group.button(
            len(self._parameter.default_values) - 2)
        dont_use_button.setChecked(True)
