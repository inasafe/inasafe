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
from utilities import htmlFooter, htmlHeader


class ImpactFunctionsDoc(QtGui.QDialog):
    '''ImpactFunctions Dialog for InaSAFE.
    '''

    def __init__(self, theParent=None, theImpactFunction=None):
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
        self.impact_function = theImpactFunction
        self.showImpactFunctionsTable()

    def showImpactFunctionsTable(self):
        '''Show table of impact functions.
        '''
        impact_functions_table = core.get_plugins_as_table(
                                                        self.impact_function)
        self.ui.webView.settings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.displayHtml(QtCore.QString(str(impact_functions_table)))

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
        #f = file('/tmp/h.thml', 'wa')  # for debugging
        #f.write(myHtml)
        #f.close()
        self.ui.webView.setHtml(myHtml)
