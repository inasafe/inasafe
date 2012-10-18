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
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '10/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import (QtGui, QtCore, QtWebKit,)
from impact_functions_doc_base import Ui_ImpactFunctionsDocBase
from safe.impact_functions import core
from safe_qgis.help import Help
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
        self.parent = theParent
        self.header = None  # for storing html header template
        self.footer = None  # for storing html footer template
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.setWindowTitle(self.tr(
                            'InaSAFE %s Impact Functions Doc' % __version__))
        self.no_filter = self.tr('No Filter')
        if dict_filter is None:
            dict_filter = {'id': [],
                           'title': [],
                           'category': [],
                           'subcategory': [],
                           'layertype': [],
                           'datatype': [],
                           'unit': []}

        self.dict_filter = dict_filter
        self.if_table = None  # for storing impact functions table
        self.showImpactFunctionsTable()
        self.combo_box_content = None  # for storing combo box content
        self.populate_combo_box()
        resetButton = self.myButtonBox.button(QtGui.QDialogButtonBox.Reset)
        QtCore.QObject.connect(resetButton, QtCore.SIGNAL('clicked()'),
                                   self.reset_button_clicked)

        # Set up help dialog showing logic.
        self.helpDialog = None
        helpButton = self.myButtonBox.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(helpButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)
        # Combo box change event
        QtCore.QObject.connect(self.comboBox_id,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)
        QtCore.QObject.connect(self.comboBox_title,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)
        QtCore.QObject.connect(self.comboBox_category,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)
        QtCore.QObject.connect(self.comboBox_subcategory,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)
        QtCore.QObject.connect(self.comboBox_layertype,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)
        QtCore.QObject.connect(self.comboBox_datatype,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)
        QtCore.QObject.connect(self.comboBox_unit,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.update_table)

    def showImpactFunctionsTable(self):
        '''Show table of impact functions.
        '''
        self.if_table = core.get_plugins_as_table(self.dict_filter)
        self.webView.settings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.displayHtml(QtCore.QString(str(self.if_table)))

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
        self.dict_filter['category'] = (
                                [str(self.comboBox_category.currentText())])
        self.dict_filter['subcategory'] = (
                            [str(self.comboBox_subcategory.currentText())])
        self.dict_filter['layertype'] = (
                            [str(self.comboBox_layertype.currentText())])
        self.dict_filter['datatype'] = (
                                [str(self.comboBox_datatype.currentText())])
        self.dict_filter['unit'] = [str(self.comboBox_unit.currentText())]
        for key, value in self.dict_filter.iteritems():
            for val in value:
                if str(val) == self.no_filter:
                    self.dict_filter[key] = list()
                    break
        # update table
        self.showImpactFunctionsTable()

    def reset_button_clicked(self):
        """Function when reset button is clicked.
            All combo box become No Filter.
            Updating table according to the filter."""
        self.comboBox_title.setCurrentIndex(0)
        self.comboBox_id.setCurrentIndex(0)
        self.comboBox_category.setCurrentIndex(0)
        self.comboBox_subcategory.setCurrentIndex(0)
        self.comboBox_layertype.setCurrentIndex(0)
        self.comboBox_datatype.setCurrentIndex(0)
        self.comboBox_unit.setCurrentIndex(0)

        self.update_table()

    def showHelp(self):
        """Load the help text for the keywords safe_qgis"""
        if self.helpDialog:
            del self.helpDialog
        self.helpDialog = Help(self, 'impact_functions')

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
        self.webView.setHtml(myHtml)
