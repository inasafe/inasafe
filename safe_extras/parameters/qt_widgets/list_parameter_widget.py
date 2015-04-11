# coding=utf-8

__author__ = 'lucernae'
__project_name__ = 'parameters'
__filename__ = 'list_parameter_widget'
__date__ = '02/04/15'
__copyright__ = 'lana.pcfre@gmail.com'


from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QListWidget, QAbstractItemView, QMessageBox,
    QListWidgetItem, QVBoxLayout)
from qt_widgets.generic_parameter_widget import GenericParameterWidget


class ListParameterWidget(GenericParameterWidget):
    """Widget class for List parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A ListParameter object.
        :type parameter: ListParameter

        """
        super(ListParameterWidget, self).__init__(parameter, parent)

        self._input = QListWidget()

        self._input.setSelectionMode(QAbstractItemView.MultiSelection)

        if self._parameter.maximum_item_count != \
                self._parameter.minimum_item_count:
            tool_tip = 'Select between %d and %d items' % (
                self._parameter.minimum_item_count,
                self._parameter.maximum_item_count)
        else:
            tool_tip = 'Select exactly %d items' % (
                       self._parameter.maximum_item_count)

        self._input.setToolTip(tool_tip)

        for opt in self._parameter.options_list:
            item = QListWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setText(str(opt))
            self._input.addItem(item)
            if opt in self._parameter.value:
                item.setSelected(True)

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

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A ListParameter from the current state of widget

        """
        selected_value = []
        for opt in self._input.selectedItems():
            index = self._input.indexFromItem(opt)
            selected_value.append(self._parameter.options_list[index.row()])

        try:
            self._parameter.value = selected_value
        except Exception as inst:
            box = QMessageBox()
            box.critical(self._input, self._parameter.name, inst.message)

        return self._parameter
