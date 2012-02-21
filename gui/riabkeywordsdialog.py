"""
Disaster risk assessment tool developed by AusAid - **GUI Keywords Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui, QtCore
#from PyQt4.QtCore import pyqtSignature
#from ui_riabdock import Ui_RiabDock
#from utilities import getExceptionWithStacktrace
from riabkeywordsdialogbase import Ui_RiabKeywordsDialogBase
from PyQt4.QtCore import pyqtSignature
# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources

#see if we can import pydev - see development docs for details
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class RiabKeywordsDialog(QtGui.QDialog, Ui_RiabKeywordsDialogBase):
    """Dialog implementation class for the Risk In A Box keywords editor."""

    def __init__(self, parent, iface, guiContext=True):
        """Constructor for the dialog.

        Args:
           * parent - parent widget of this dialog
           * iface - a Quantum GIS QGisAppInterface instance.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        # set some inital ui state:
        self.pbnAdvanced.setChecked(True)
        self.pbnAdvanced.toggle()
        self.radPredefined.setChecked(True)
        self.radExposure.setChecked(True)
        self.adjustSize()
        myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        myButton.setEnabled(False)

        # Put in some dummy data while we are testing

    @pyqtSignature('bool')  # prevents actions being handled twice
    def on_pbnAdvanced_toggled(self, theFlag):
        """Automatic slot executed when the advanced button is toggled.

        .. note:: some of the behaviour for hiding widgets is done using
           the signal/slot editor in designer, so if you are trying to figure
           out how the interactions work, look there too!

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        self.adjustSize()

    @pyqtSignature('bool')  # prevents actions being handled twice
    def on_radHazard_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled.

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if theFlag:
            myHazardList = [self.tr('earthquake [mmi]'),
                            self.tr('tsunami [m]'),
                            self.tr('tsunami [wet/dry]'),
                            self.tr('tsunami [feet]'),
                            self.tr('flood [m]'),
                            self.tr('flood [wet/dry]'),
                            self.tr('flood [feet]'),
                            self.tr('volcano [kg2/m2]')]
            self.setSubcategoryList(myHazardList)

    @pyqtSignature('bool')  # prevents actions being handled twice
    def on_radExposure_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled.

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if theFlag:
            myExposureList = [self.tr('population [density]'),
                              self.tr('population [count]'),
                              self.tr('building [osm]'),
                              self.tr('building [sigab]'),
                              self.tr('building [other]'),
                              self.tr('roads')]
            self.setSubcategoryList(myExposureList)

    def setSubcategoryList(self, theList):
        """Helper to populate the subcategory list based on category context.

        Args:
           theList - a list of subcategories e.g. ['earthquake','volcano']
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        self.cboSubcategory.clear()
        for myItem in theList:
            self.cboSubcategory.addItem(myItem)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pbnAddToList1_clicked(self):
        """Automatic slot executed when the pbnAddToList1 button is pressed.

        It will add the current key/value pair to the list if it is not
        already present. The kvp will also be stored in the data of the
        listwidgetitem as a simple string delimited with a bar ('|').

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""

        myCurrentKey = self.cboKeyword.currentText()
        myCurrentValue = self.cboValue.currentText()
        myItem = QtGui.QListWidgetItem(myCurrentKey + ':' + myCurrentValue)

        # check the key does not already exist
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            if myExistingItem.text() == myItem.text():
                # .. todo:: tell the user something? TS
                return

        myData = myCurrentKey + '|' + myCurrentValue
        myItem.setData(QtCore.Qt.UserRole, myData)
        self.lstKeywords.insertItem(0, myItem)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pbnRemove_clicked(self):
        """Automatic slot executed when the pbnRemove button is pressed.

        It will remove any selected items in the keywords list.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        for myItem in self.lstKeywords.selectedItems():
            self.lstKeywords.removeItemWidget(myItem)
