# coding=utf-8
__author__ = 'lucernae'
__project_name__ = 'parameters'
__filename__ = 'list_parameter_widget'
__date__ = '02/04/15'
__copyright__ = 'lana.pcfre@gmail.com'

from PyQt4.QtGui import QListWidget, QAbstractItemView, QMessageBox
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

        # for idx, opt in enumerate(self._parameter.options_list):
        #     list_item = QListWidgetItem()
        #     list_item.setText(opt.__str__())
        #     list_item.setData(0, idx)
        #     self._input.addItem(list_item)
        self._input.addItems(self._parameter.options_list)
        self._inner_input_layout.addWidget(self._input)

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
