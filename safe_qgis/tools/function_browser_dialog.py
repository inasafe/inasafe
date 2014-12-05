# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Functions Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ismailsunni@yahoo.co.id'
__revision__ = '$Format:%H$'
__date__ = '10/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import QtGui, QtWebKit
from safe_qgis.ui.function_browser_base import Ui_FunctionBrowserBase
from safe_qgis.utilities.help import show_context_help
from safe_qgis.safe_interface import (
    get_version,
    get_unique_values,
    get_plugins_as_table)
from safe_qgis.utilities.utilities import html_footer, html_header


class FunctionBrowser(QtGui.QDialog, Ui_FunctionBrowserBase):
    """ImpactFunctions Dialog for InaSAFE.
    """

    def __init__(self, parent=None, dict_filter=None):
        """Constructor for the dialog.

        This dialog will show the user impact function documentation.

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param dict_filter: Optional filter to use to limit which functions
            are show to the user. See below.
        :type dict_filter: dict

        Example dict_filter::

            {'id': [],
             'title': [],
             'category': [],
             'subcategory': [],
             'layertype': [],
             'datatype': [],
             'unit': []}
        """
        QtGui.QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.setWindowTitle(
            self.tr('InaSAFE %s Impact Functions Browser' % get_version()))
        self.parent = parent

        self.no_filter = self.tr('No Filter')
        if dict_filter is None:
            dict_filter = {
                'id': [],
                'title': [],
                'category': [],
                'subcategory': [],
                'layertype': [],
                'datatype': [],
                'unit': []}

        self.dict_filter = dict_filter
        self.table = None  # for storing impact functions table
        self.show_table()
        self.combo_box_content = None  # for storing combo box content
        self.populate_combo_box()
        # Hey we should be using autoconnect here TS
        reset_button = self.myButtonBox.button(QtGui.QDialogButtonBox.Reset)
        reset_button.clicked.connect(self.reset_button_clicked)

        # and autoconenct here too! TS
        help_button = self.myButtonBox.button(QtGui.QDialogButtonBox.Help)
        help_button.clicked.connect(self.show_help)

        # Combo box change event ... and all of these! TS
        self.comboBox_id.currentIndexChanged.connect(self.update_table)
        self.comboBox_title.currentIndexChanged.connect(self.update_table)
        self.comboBox_category.currentIndexChanged.connect(self.update_table)
        self.comboBox_subcategory.currentIndexChanged.connect(
            self.update_table)
        self.comboBox_layertype.currentIndexChanged.connect(self.update_table)
        self.comboBox_datatype.currentIndexChanged.connect(self.update_table)
        self.comboBox_unit.currentIndexChanged.connect(self.update_table)

    def show_table(self):
        """Show table of impact functions.
        """
        self.table = get_plugins_as_table(self.dict_filter)
        self.webView.settings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.display_html(str(self.table))

    def generate_combo_box_content(self):
        """Generate list for each combo box's content."""
        unique_values = get_unique_values()
        for item in unique_values.itervalues():
            item.insert(0, self.no_filter)

        return unique_values

    def populate_combo_box(self):
        """Populate item in each combo box."""
        if self.combo_box_content is None:
            self.combo_box_content = self.generate_combo_box_content()

        self.comboBox_title.addItems(self.combo_box_content['title'])
        self.comboBox_id.addItems(self.combo_box_content['id'])
        self.comboBox_category.addItems(self.combo_box_content['category'])
        self.comboBox_subcategory.addItems(
            self.combo_box_content['subcategory'])
        self.comboBox_layertype.addItems(
            self.combo_box_content['layertype'])
        self.comboBox_datatype.addItems(self.combo_box_content['datatype'])
        self.comboBox_unit.addItems(self.combo_box_content['unit'])

    def update_table(self):
        """Updating table according to the filter."""
        # get filter
        self.dict_filter['title'] = [str(self.comboBox_title.currentText())]
        self.dict_filter['id'] = [str(self.comboBox_id.currentText())]
        self.dict_filter['category'] = \
            ([str(self.comboBox_category.currentText())])
        self.dict_filter['subcategory'] = \
            ([str(self.comboBox_subcategory.currentText())])
        self.dict_filter['layertype'] = \
            ([str(self.comboBox_layertype.currentText())])
        self.dict_filter['datatype'] = \
            ([str(self.comboBox_datatype.currentText())])
        self.dict_filter['unit'] = [str(self.comboBox_unit.currentText())]
        for key, value in self.dict_filter.iteritems():
            for val in value:
                if str(val) == self.no_filter:
                    self.dict_filter[key] = list()
                    break
        # update table
        self.show_table()

    def reset_button_clicked(self):
        """Function when reset button is clicked.

        All combo box become No Filter. Updating table according to the filter.
        """
        self.comboBox_title.setCurrentIndex(0)
        self.comboBox_id.setCurrentIndex(0)
        self.comboBox_category.setCurrentIndex(0)
        self.comboBox_subcategory.setCurrentIndex(0)
        self.comboBox_layertype.setCurrentIndex(0)
        self.comboBox_datatype.setCurrentIndex(0)
        self.comboBox_unit.setCurrentIndex(0)

        self.update_table()

    def show_help(self):
        """Load the help text for the impact functions dialog."""
        show_context_help('impact_functions')

    def display_html(self, message):
        """Display rendered html output in the widget.

        Given an html snippet, wrap it in a page header and footer
        and display it in the wvResults widget.

        :param message: An html snippet (typically a table in this context)
            to display.
        :type message: str or QString
        """
        html = html_header() + message + html_footer()
        self.webView.setHtml(html)
