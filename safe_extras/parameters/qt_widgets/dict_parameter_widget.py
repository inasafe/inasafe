# coding=utf-8
"""Docstring for this file."""

__author__ = 'Jannes Engelbrecht jannes@kartoza.com'
__project_name = 'parameters'
__filename = 'dict_parameter_widget'
__date__ = '12/11/14'
__copyright__ = 'kartoza.com'
__doc__ = ''

# This import is to enable SIP API V2
# noinspection PyPackageRequirements
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QTreeWidget, QFont, QTreeWidgetItem, QVBoxLayout)
from qt_widgets.generic_parameter_widget import (
    GenericParameterWidget)

import logging
LOGGER = logging.getLogger('InaSAFE')


# pylint: disable=super-on-old-class
class DictParameterWidget(GenericParameterWidget):
    """Widget class for DictParameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 3.1

        :param parameter: A DictParameter object.
        :type parameter: DictParameter

        """
        # pylint: disable=E1002
        super(DictParameterWidget, self).__init__(parameter, parent)
        # pylint: enable=E1002

        self._input = QTreeWidget()

        # generate tree model
        widget_items = self.generate_tree_model(self._parameter.value)
        self._input.addTopLevelItems(widget_items)
        # set header
        self._input.headerItem().setText(0, 'Values')

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

    def generate_tree_model(self, data_dict):
        """Generate a tree model for specified dictionary

        :param data_dict: A dictionary
        :type data_dict: dict
        :return: list of QTreeWidgetItem
        :rtype list:
        """
        widget_items = []
        font = QFont()
        font.setBold(True)
        for key in data_dict.keys():
            entry = data_dict[key]
            key_item = QTreeWidgetItem()
            key_item.setText(0, str(key))
            key_item.setFont(0, font)
            if isinstance(entry, dict):
                items = self.generate_tree_model(entry)
                key_item.addChildren(items)
            else:
                value_item = QTreeWidgetItem()
                value_item.setText(0, str(entry))
                value_item.setFlags(value_item.flags() | Qt.ItemIsEditable)
                key_item.addChild(value_item)
            widget_items.append(key_item)

        return widget_items

    def extract_dict(self, widget_items):
        """Extract dictionary key and values from QTreeWidgetItems

        :param widget_items: List of QTreeWidgetItems
        :type widget_items: list
        :return: hierarchical dictionary extracted from widget_items
        :rtype dict:
        """
        data_dict = {}
        element_type = self._parameter.element_type
        if element_type == object:
            def object_cast(obj):
                return obj
            element_type = object_cast
        for key_item in widget_items:
            key = str(key_item.text(0))
            value = None
            if key_item.childCount() == 1:
                value_item = key_item.child(0)
                value = element_type(value_item.text(0))
            elif key_item.childCount() > 1:
                value_items = [key_item.child(i)
                               for i in range(key_item.childCount())]
                value = self.extract_dict(value_items)
            data_dict[key] = value
        return data_dict

    def get_parameter(self):
        """Obtain the parameter object from the current widget state.

        :returns: A DictParameter from the current state of widget

        """
        root_widget_item = self._input.invisibleRootItem()
        widget_items = [root_widget_item.child(i)
                        for i in range(root_widget_item.childCount())]
        data_dict = self.extract_dict(widget_items)
        self._parameter.value = data_dict
        return self._parameter

# pylint: enable=super-on-old-class
