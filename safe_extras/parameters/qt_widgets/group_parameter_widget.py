# coding=utf-8

__author__ = 'lucernae'
__project_name__ = 'parameters'
__filename__ = 'list_parameter_widget'
__date__ = '02/04/15'
__copyright__ = 'lana.pcfre@gmail.com'

from PyQt4.QtGui import (
    QVBoxLayout, QCheckBox)
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

        self._enable_check_box = QCheckBox()
        # Tooltips
        self.setToolTip('Tick here to enable ' + self._parameter.name)
        self._enable_check_box.setChecked(self._parameter.enable_parameter)

        # add handlers
        # noinspection PyUnresolvedReferences
        self._enable_check_box.stateChanged.connect(
            self.on_enable_checkbox_changed)

        self._inner_input_layout.addWidget(self._enable_check_box)

        # add all widget in the group
        self._group_layout = QVBoxLayout()
        self._group_layout.setSpacing(0)

        self._main_layout.addLayout(self._group_layout)

        from qt_widgets.parameter_container import ParameterContainer

        self.param_container = ParameterContainer(
            parameters=self._parameter.value)
        self.param_container.setup_ui(must_scroll=parameter.must_scroll)

        self._group_layout.addWidget(self.param_container)

    def on_enable_checkbox_changed(self, state):
        if state:
            self.param_container.show()
        else:
            self.param_container.hide()

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A ListParameter from the current state of widget

        """
        parameters = self.param_container.get_parameters()
        self._parameter.value = parameters
        self._parameter.validate()

        return self._parameter
