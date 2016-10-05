# coding=utf-8
"""Select Parameter Widget"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QComboBox
from qt_widgets.generic_parameter_widget import GenericParameterWidget

__author__ = 'ismailsunni'
__project_name__ = 'parameters'
__filename__ = 'select_parameter_widget'
__date__ = '05/10/2016'
__copyright__ = 'imajimatika@gmail.com'


class SelectParameterWidget(GenericParameterWidget):
    """Widget class for List parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        :param parameter: A ListParameter object.
        :type parameter: ListParameter

        """
        super(SelectParameterWidget, self).__init__(parameter, parent)

        self._input = QComboBox()

        index = -1
        current_index = -1
        for opt in self._parameter.options_list:
            index += 1
            if opt == self._parameter.value:
                current_index = index
            self._input.addItem(opt)
            self._input.setItemData(index, opt, Qt.UserRole)

        self._input.setCurrentIndex(current_index)

        self._inner_input_layout.addWidget(self._input)

        # override self._input_layout arrangement to make the label at the top
        # reset the layout
        self._input_layout.setParent(None)
        self._help_layout.setParent(None)

        self._label.setParent(None)
        self._inner_input_layout.setParent(None)

        self._input_layout = QVBoxLayout()
        self._input_layout.setSpacing(0)

        # put element into layout
        self._input_layout.addWidget(self._label)
        self._input_layout.addLayout(self._inner_input_layout)

        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addLayout(self._help_layout)

    def raise_invalid_type_exception(self):
        message = 'Expecting element type of %s' % (
            self._parameter.element_type.__name__)
        err = ValueError(message)
        return err

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A ListParameter from the current state of widget

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

        return self._parameter
