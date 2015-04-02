# coding=utf-8
"""Docstring for this file."""
__author__ = 'Jannes Engelbrecht jannes@kartoza.com'
__project_name = 'parameters'
__filename = 'dict_parameter_widget'
__date__ = '12/11/14'
__copyright__ = 'kartoza.com'
__doc__ = ''

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtGui import QTableWidget, QTableWidgetItem
from safe_extras.parameters.qt_widgets.generic_parameter_widget import (
    GenericParameterWidget)

import logging
LOGGER = logging.getLogger('InaSAFE')


# pylint: disable=super-on-old-class
class ListParameterWidget(GenericParameterWidget):
    """Widget class for DictParameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 3.1

        :param parameter: A ListParameter object.
        :type parameter: ListParameter

        """
        # pylint: disable=E1002
        super(ListParameterWidget, self).__init__(parameter, parent)
        # pylint: enable=E1002

        self._table_edit_input = QTableWidget(
            1, self._parameter.__len__())

        # pack parameter into table
        for (i, label) in enumerate(sorted(self._parameter.value)):
            self._table_edit_input.setHorizontalHeaderItem(
                i, QTableWidgetItem(str(i)))
            t_item = QTableWidgetItem(str(self._parameter[i]))
            self._table_edit_input.setItem(0, i, t_item)

        self._table_edit_input.verticalHeader().setVisible(False)
        self._inner_input_layout.addWidget(self._table_edit_input)

    def get_parameter(self):
        """Obtain the parameter object from the current widget state.

        :returns: A ListParameter from the current state of widget

        """
        # step through QTableWidget and build dict
        columns = self._table_edit_input.columnCount()
        for c in range(0, columns, 1):
            label = self._table_edit_input.horizontalHeaderItem(c).text()
            value = self._table_edit_input.item(0, c).text()
            self._parameter[int(label)] = str(value)
        return self._parameter


# pylint: enable=super-on-old-class
