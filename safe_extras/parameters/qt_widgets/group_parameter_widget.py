# coding=utf-8

__author__ = 'lucernae'
__project_name__ = 'parameters'
__filename__ = 'list_parameter_widget'
__date__ = '02/04/15'
__copyright__ = 'lana.pcfre@gmail.com'

from PyQt4.QtGui import QVBoxLayout, QCheckBox

from qt_widgets.generic_parameter_widget import GenericParameterWidget


class GroupParameterWidget(GenericParameterWidget):
    """Widget class for List parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A GroupParameter object.
        :type parameter: GroupParameter

        """
        super(GroupParameterWidget, self).__init__(parameter, parent)

        # Get the parameter label and use its value as the checkbox text
        label_item = self._input_layout.itemAt(0)
        label_widget = label_item.widget()
        text = label_widget.text()
        self._enable_check_box = QCheckBox(text)
        # Tooltips
        self.setToolTip('Tick here to enable ' + self._parameter.name)

        # add all widget in the group
        self._group_layout = QVBoxLayout()
        self._group_layout.setSpacing(0)

        if not self._parameter.is_required:
            self._input_layout.insertWidget(0, self._enable_check_box)
            # now we don't need the parameter label anymore so chuck it
            self._input_layout.removeItem(label_item)
            # Make the sub group appear indented
            self._group_layout.setContentsMargins(20, 0, 0, 0)
        else:
            self._parameter.enable_parameter = True

        self._main_layout.addLayout(self._group_layout)

        # Why are we doing imports here? TS
        from qt_widgets.parameter_container import ParameterContainer

        self.param_container = ParameterContainer(
            parameters=self._parameter.value)
        self.param_container.setup_ui(must_scroll=parameter.must_scroll)

        # add handlers
        # noinspection PyUnresolvedReferences
        self._enable_check_box.stateChanged.connect(
            self.on_enable_checkbox_changed)
        self._enable_check_box.setChecked(self._parameter.enable_parameter)
        self.on_enable_checkbox_changed(self._parameter.enable_parameter)

        self._group_layout.addWidget(self.param_container)

    def on_enable_checkbox_changed(self, state):
        if state:
            self.param_container.show()
        else:
            self.param_container.hide()
        self._parameter.enable_parameter = state

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A ListParameter from the current state of widget

        """
        if self._parameter.enable_parameter:
            parameters = self.param_container.get_parameters()
            self._parameter.value = parameters
            self._parameter.validate()

        return self._parameter
