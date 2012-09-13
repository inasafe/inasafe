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
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '10/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import (QtGui, QtCore, QtWebKit,)
from impact_functions_doc_base import Ui_ImpactFunctionsDocBase
from safe.impact_functions import core
from safe.impact_functions.core import get_unique_values
from utilities import htmlFooter, htmlHeader


class ImpactFunctionsDoc(QtGui.QDialog, Ui_ImpactFunctionsDocBase):
    '''ImpactFunctions Dialog for InaSAFE.
    '''

    def __init__(self, theParent=None, dict_filter=None):
        '''Constructor for the dialog.

                This dialog will show the user impact function documentation.

        Args:
           * theParent - Optional widget to use as parent
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        '''
        QtGui.QDialog.__init__(self, theParent)
        self.header = None  # for storing html header template
        self.footer = None  # for storing html footer template
        # Set up the user interface from Designer.
        self.ui = Ui_ImpactFunctionsDocBase()
        self.ui.setupUi(self)
        self.no_filter = 'No Filter'
        if dict_filter == None:
            self.dict_filter = dict()
        self.showImpactFunctionsTable()
        self.combo_box_content = None  # for storing combo box content
        self.populate_combo_box()
        applyButton = self.ui.myButtonBox.button(QtGui.QDialogButtonBox.Apply)
        QtCore.QObject.connect(applyButton, QtCore.SIGNAL('clicked()'),
                                   self.apply_button_clicked)

    def showImpactFunctionsTable(self):
        '''Show table of impact functions.
        '''
        impact_functions_table = core.get_plugins_as_table2()
        import datetime as d
        f = open('atos_' + str(d.datetime.now()) + '.txt', 'wt')
        f.write('update Table\n\n')
        f.write(str(self.dict_filter) + '\n\n')
        f.write(impact_functions_table.toNewlineFreeString())
        f.close()
        self.ui.webView.settings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.displayHtml(QtCore.QString(str(impact_functions_table)))

    def generate_combo_box_content(self):
        '''Generate list for each combo box's content.
        '''
        unique_values = get_unique_values()
        for item in unique_values.itervalues():
            item.insert(0, self.no_filter)

        return unique_values

    def populate_combo_box(self):
        '''Populate item in each combo box.
        '''
        if self.combo_box_content == None:
            self.combo_box_content = self.generate_combo_box_content()

        self.ui.comboBox_title.addItems(self.combo_box_content['title'])
        self.ui.comboBox_id.addItems(self.combo_box_content['id'])
        self.ui.comboBox_category.addItems(self.combo_box_content['category'])
        self.ui.comboBox_subcategory.addItems(
                                        self.combo_box_content['subcategory'])
        self.ui.comboBox_layertype.addItems(
                                        self.combo_box_content['layertype'])
        self.ui.comboBox_datatype.addItems(self.combo_box_content['datatype'])
        self.ui.comboBox_unit.addItems(self.combo_box_content['unit'])

    def apply_button_clicked(self):
        """Function when apply button is clicked.
            Updating table according to the filter."""
        # get filter
        self.dict_filter['title'] = [self.ui.comboBox_title.currentText()]
        self.dict_filter['id'] = [self.ui.comboBox_id.currentText()]
        self.dict_filter['category'] = (
                                [self.ui.comboBox_category.currentText()])
        self.dict_filter['subcategory'] = (
                                [self.ui.comboBox_subcategory.currentText()])
        self.dict_filter['layertype'] = (
                                [self.ui.comboBox_layertype.currentText()])
        self.dict_filter['datatype'] = (
                                [self.ui.comboBox_datatype.currentText()])
        self.dict_filter['unit'] = [self.ui.comboBox_unit.currentText()]
        for key, value in self.dict_filter.iteritems():
            for val in value:
                if str(val) == self.no_filter:
                    self.dict_filter[key] = list()
                    break
        # update table
        self.showImpactFunctionsTable()

    def htmlHeader(self):
        """Get a standard html header for wrapping content in."""
        if self.header is None:
            self.header = htmlHeader()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            self.footer = htmlFooter()
        return self.footer

    def displayHtml(self, theMessage):
        """Given an html snippet, wrap it in a page header and footer
        and display it in the wvResults widget."""
        myHtml = self.htmlHeader() + theMessage + self.htmlFooter()
        self.ui.webView.setHtml(myHtml)
