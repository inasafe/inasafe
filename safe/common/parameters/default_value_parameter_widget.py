# coding=utf-8
"""Default Value Parameter Widget."""

from qgis.PyQt.QtWidgets import (
    QButtonGroup,
    QDoubleSpinBox,
    QHBoxLayout,
    QRadioButton
)

from parameters.qt_widgets.generic_parameter_widget import (
    GenericParameterWidget
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class DefaultValueParameterWidget(GenericParameterWidget):

    """Widget class for Default Value Parameter."""

    def __init__(self, parameter, parent=None):
        """Constructor.

        :param parameter: A DefaultValueParameter object.
        :type parameter: DefaultValueParameter

        """
        super(DefaultValueParameterWidget, self).__init__(parameter, parent)

        self.radio_button_layout = QHBoxLayout()

        # Create radio button group
        self.input_button_group = QButtonGroup()

        for i in range(len(self._parameter.labels)):
            if '%s' in self._parameter.labels[i]:
                label = (
                    self._parameter.labels[i] %
                    self._parameter.options[i])
            else:
                label = self._parameter.labels[i]

            radio_button = QRadioButton(label)
            self.radio_button_layout.addWidget(radio_button)
            self.input_button_group.addButton(radio_button, i)
            if self._parameter.value == \
                    self._parameter.options[i]:
                radio_button.setChecked(True)

        # Create double spin box for custom value
        self.custom_value = QDoubleSpinBox()
        self.custom_value.setSingleStep(0.1)
        if self._parameter.options[-1]:
            self.custom_value.setValue(self._parameter.options[-1])
        self.radio_button_layout.addWidget(self.custom_value)

        self.toggle_custom_value()

        self.inner_input_layout.addLayout(self.radio_button_layout)

        # Connect
        # noinspection PyUnresolvedReferences
        self.input_button_group.buttonClicked.connect(
            self.toggle_custom_value)

    def raise_invalid_type_exception(self):
        """Raise invalid type."""
        message = 'Expecting element type of %s' % (
            self._parameter.element_type.__name__)
        err = ValueError(message)
        return err

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A DefaultValueParameter from the current state of widget
        :rtype: DefaultValueParameter
        """
        radio_button_checked_id = self.input_button_group.checkedId()
        # No radio button checked, then default value = None
        if radio_button_checked_id == -1:
            self._parameter.value = None
        # The last radio button (custom) is checked, get the value from the
        # line edit
        elif radio_button_checked_id == len(self._parameter.options) - 1:
            self._parameter.options[radio_button_checked_id] = \
                self.custom_value.value()
            self._parameter.value = self.custom_value.value()
        else:
            self._parameter.value = self._parameter.options[
                radio_button_checked_id]

        return self._parameter

    def set_value(self, value):
        """Set value by item's string.

        :param value: The value.
        :type value: str, int

        :returns: True if success, else False.
        :rtype: bool
        """
        # Find index of choice
        try:
            value_index = self._parameter.options.index(value)
            self.input_button_group.button(value_index).setChecked(True)
        except ValueError:
            last_index = len(self._parameter.options) - 1
            self.input_button_group.button(last_index).setChecked(
                True)
            self.custom_value.setValue(value)

        self.toggle_custom_value()

    def toggle_custom_value(self):
        """Enable or disable the custom value line edit."""
        radio_button_checked_id = self.input_button_group.checkedId()
        if (radio_button_checked_id
                == len(self._parameter.options) - 1):
            self.custom_value.setDisabled(False)
        else:
            self.custom_value.setDisabled(True)
