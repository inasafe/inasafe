# coding=utf-8

__author__ = 'lucernae'
__project_name__ = 'parameters'
__filename__ = 'list_parameter_widget'
__date__ = '02/04/15'
__copyright__ = 'lana.pcfre@gmail.com'

from PyQt4.QtGui import (
    QListWidget, QAbstractItemView, QMessageBox,
    QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QListWidgetItem)
from PyQt4.QtCore import Qt
from input_list_parameter import InputListParameter
from qt_widgets.generic_parameter_widget import GenericParameterWidget


class InputListParameterWidget(GenericParameterWidget):
    """Widget class for List parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A ListParameter object.
        :type parameter: InputListParameter

        """
        super(InputListParameterWidget, self).__init__(parameter, parent)

        # value cache for self._parameter.value
        # copy the list so the original is unaffected
        self._value_cache = list(self._parameter.value)

        self._input = QListWidget()

        self._input.setSelectionMode(QAbstractItemView.SingleSelection)

        if self._parameter.maximum_item_count != \
                self._parameter.minimum_item_count:
            tool_tip = 'Select between %d and %d items' % (
                self._parameter.minimum_item_count,
                self._parameter.maximum_item_count)
        else:
            tool_tip = 'Select exactly %d items' % (
                       self._parameter.maximum_item_count)

        self._input.setToolTip(tool_tip)

        # arrange widget

        self._insert_item_input = QLineEdit()

        vbox_layout = QVBoxLayout()
        hbox_layout = QHBoxLayout()
        self._input_add_button = QPushButton('Add')
        self._input_remove_button = QPushButton('Remove')
        # arrange line edit, add button, remove button in horizontal layout
        hbox_layout.addWidget(self._insert_item_input)
        hbox_layout.addWidget(self._input_add_button)
        hbox_layout.addWidget(self._input_remove_button)
        # arrange vertical layout
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self._input)
        self._inner_input_layout.addLayout(vbox_layout)

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

        # connect handler
        # noinspection PyUnresolvedReferences
        self._input_add_button.clicked.connect(self.on_add_button_click)
        # noinspection PyUnresolvedReferences
        self._input_remove_button.clicked.connect(self.on_remove_button_click)
        # noinspection PyUnresolvedReferences
        self._insert_item_input.returnPressed.connect(
            self._input_add_button.click)
        # noinspection PyUnresolvedReferences
        self._input.itemChanged.connect(self.on_row_changed)

        self.refresh_list()

    def refresh_list(self):
        self._input.clear()
        if not self._parameter.ordering == InputListParameter.NotOrdered:
            self._value_cache.sort()
        if self._parameter.ordering == InputListParameter.DescendingOrder:
            self._value_cache.reverse()
        for opt in self._value_cache:
            item = QListWidgetItem()
            item.setText(str(opt))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self._input.addItem(item)

    def on_add_button_click(self):
        try:
            value = self._parameter.element_type(
                self._insert_item_input.text())
            self._value_cache.append(value)
            self.refresh_list()
        except ValueError:
            self.show_invalid_type_exception()

    def on_remove_button_click(self):
        for opt in self._input.selectedItems():
            index = self._input.indexFromItem(opt)
            del self._value_cache[index.row()]
        self.refresh_list()

    def on_row_changed(self, item):
        try:
            index = self._input.indexFromItem(item).row()
            prev_value = self._value_cache[index]
            self._value_cache[index] = self._parameter.element_type(
                item.text())
        except ValueError:
            self.show_invalid_type_exception()
            item.setText(str(prev_value))

    def show_invalid_type_exception(self):
        message = 'Expecting element type of %s' % (
            self._parameter.element_type.__name__)
        box = QMessageBox()
        box.critical(self._input, self._parameter.name, message)

    def get_parameter(self):
        """Obtain list parameter object from the current widget state.

        :returns: A ListParameter from the current state of widget

        """

        try:
            self._parameter.value = self._value_cache
        except Exception as inst:
            box = QMessageBox()
            box.critical(self._input, self._parameter.name, inst.message)

        return self._parameter
