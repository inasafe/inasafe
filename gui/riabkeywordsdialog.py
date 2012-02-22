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

import os
from PyQt4 import QtGui, QtCore
#from PyQt4.QtCore import pyqtSignature
#from ui_riabdock import Ui_RiabDock
#from utilities import getExceptionWithStacktrace
from impactcalculator import ImpactCalculator
from riabkeywordsdialogbase import Ui_RiabKeywordsDialogBase
from PyQt4.QtCore import pyqtSignature
from storage.utilities import write_keywords
from riabexceptions import InvalidParameterException
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

    def __init__(self, parent, iface):
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
        self.standardExposureList = [self.tr('population [density]'),
                                     self.tr('population [count]'),
                                     self.tr('building [osm]'),
                                     self.tr('building [sigab]'),
                                     self.tr('building [other]'),
                                     self.tr('roads')]
        self.standardHazardList = [self.tr('earthquake [mmi]'),
                                     self.tr('tsunami [m]'),
                                     self.tr('tsunami [wet/dry]'),
                                     self.tr('tsunami [feet]'),
                                     self.tr('flood [m]'),
                                     self.tr('flood [wet/dry]'),
                                     self.tr('flood [feet]'),
                                     self.tr('volcano [kg2/m2]')]
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        # set some inital ui state:
        self.pbnAdvanced.setChecked(True)
        self.pbnAdvanced.toggle()
        self.radPredefined.setChecked(True)
        self.radExposure.setChecked(True)
        self.adjustSize()
        #myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        #myButton.setEnabled(False)
        self.layer = self.iface.activeLayer()
        self.lblLayerName.setText(self.layer.name())
        self.loadStateFromKeywords()
        settrace()
        #self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)

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
        if theFlag:
            self.pbnAdvanced.setText(self.tr('Show simple editor'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced editor'))
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
            self.setSubcategoryList(self.standardHazardList)

    @pyqtSignature('bool')  # prevents actions being handled twice
    def on_radExposure_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled on.

        Args:
           theFlag - boolean indicating the new checked state of the button
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if theFlag:
            self.setSubcategoryList(self.standardExposureList)

    def setSubcategoryList(self, theList, theSelectedItem=None):
        """Helper to populate the subcategory list based on category context.

        Args:

           * theList - a list of subcategories e.g. ['earthquake','volcano']
           * theSelectedItem - optional parameter indicating which item
             should be selected in the combo. If the selected item is not
             in theList, it will be appended to it.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        self.cboSubcategory.clear()
        if theSelectedItem is not None and theSelectedItem not in theList:
            theList.append(theSelectedItem)
        myIndex = 0
        mySelectedIndex = 0
        for myItem in theList:
            if myItem == theSelectedItem:
                mySelectedIndex = myIndex
            myIndex += 1
            self.cboSubcategory.addItem(myItem)
        self.cboSubcategory.setCurrentIndex(mySelectedIndex)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pbnAddToList1_clicked(self):
        """Automatic slot executed when the pbnAddToList1 button is pressed.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""

        myCurrentKey = self.cboKeyword.currentText()
        myCurrentValue = self.lePredefinedValue.text()
        self.addListEntry(myCurrentKey, myCurrentValue)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pbnAddToList2_clicked(self):
        """Automatic slot executed when the pbnAddToList2 button is pressed.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""

        myCurrentKey = self.leKey.text()
        myCurrentValue = self.leValue.text()
        self.addListEntry(myCurrentKey, myCurrentValue)

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
            self.lstKeywords.takeItem(self.lstKeywords.row(myItem))

    def addListEntry(self, theKey, theValue):
        """Add an item to the keywords list given its key/value.

        The key and value must both be valid, non empty strings
        or an InvalidKVPException will be raised.

        If an entry with the same key exists, it's value will be
        replaced with theValue.

        It will add the current key/value pair to the list if it is not
        already present. The kvp will also be stored in the data of the
        listwidgetitem as a simple string delimited with a bar ('|').

        Args:

           * theKey - string representing the key part of the key
             value pair (kvp)
           * theValue - string representing the value part of the key
             value pair (kvp)

        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        if theKey is None or theKey == '':
            return
        if theValue is None or theValue == '':
            return
        # special rule: if the key is 'category', enforce that the
        # value is either 'exposure' or 'hazard' and toggle the
        # correct radio button in the simple editor
        if theKey == 'category':
            if not self.setCategory(theValue):
                # .. todo:: report an error to the user
                return False

        myItem = QtGui.QListWidgetItem(theKey + ':' + theValue)
        # we are going to replace, so remove it if it exists already
        self.removeItemByKey(theKey)
        myData = theKey + '|' + theValue
        myItem.setData(QtCore.Qt.UserRole, myData)
        self.lstKeywords.insertItem(0, myItem)

    def setCategory(self, theCategory):
        """Set the category radio button based on theCategory.

        Args:
           theCategory - a string which must be either 'hazard' or 'exposure'.
        Returns:
           False if the radio button could not be updated
        Raises:
           no exceptions explicitly raised."""
        # convert from QString if needed
        myCategory = str(theCategory)
        if myCategory not in ['hazard', 'exposure']:
            # .. todo:: report an error to the user
            return False
        # Special case when category changes, we start on a new slate!
        self.reset()

        if myCategory in 'hazard':
            self.radHazard.setChecked(True)
        else:
            self.radExposure.setChecked(True)
        return True

    def reset(self):
        """Reset all controls to a blank state.

        Args:
            None
        Returns:
            None
        Raises:
           no exceptions explicitly raised."""
        self.cboSubcategory.clear()
        self.lstKeywords.clear()
        self.leKey.clear()
        self.leValue.clear()
        self.lePredefinedValue.clear()

    def removeItemByKey(self, theKey):
        """Remove an item from the kvp list given its key.

        Args:
            theKey - key of item to be removed.
        Returns:
            None
        Raises:
           no exceptions explicitly raised."""
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myKey = myTokens[0]
            if myKey == theKey:
                # remove it since the key is already present
                self.lstKeywords.takeItem(myCounter)
                break

    def removeItemByValue(self, theValue):
        """Remove an item from the kvp list given its key.

        Args:
            theValue - value of item to be removed.
        Returns:
            None
        Raises:
           no exceptions explicitly raised."""
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myValue = myTokens[1]
            if myValue == theValue:
                # remove it since the key is already present
                self.lstKeywords.takeItem(myCounter)
                break

    def loadStateFromKeywords(self):
        """Set the ui state to match the keywords of the
           currently active layer.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        mySource = str(self.layer.source())
        self.calculator = ImpactCalculator()
        try:
            myKeywords = self.calculator.getKeywordFromFile(mySource)
        except InvalidParameterException:
            # layer has no keywords file so just start with a blank slate
            return

        myCategory = None
        if 'category' in myKeywords:
            myCategory = myKeywords['category']
            self.setCategory(myCategory)
        self.addListEntry('category', myCategory)
        # get the subcategory an type if it is an exposure layer
        # or the subcategory and units if it is a hazard layer
        mySubCategory = None
        myUnits = None
        myType = None
        if 'subcategory' in myKeywords:
            mySubCategory = myKeywords['subcategory']
            self.addListEntry('subcategory', mySubCategory)
        if 'datatype' in myKeywords:
            myType = myKeywords['datatype']
            self.addListEntry('datatype', myType)
        if 'units' in myKeywords:
            myUnits = myKeywords['units']
            self.addListEntry('units', myUnits)

        # .. note:: The logic here could theoritically be simpler
        #    but type and units arent guaranteed to be mutually exclusive
        #    in the future.
        if mySubCategory and myUnits:
            # also set up the combo in the 'simple' editor section
            if self.radExposure.isChecked():
                self.setSubcategoryList(self.standardExposureList,
                                         mySubCategory + ' [' + myType + ']')
            else:
                self.setSubcategoryList(self.standardExposureList,
                                         mySubCategory + ' [' + myUnits + ']')

        elif mySubCategory and myType:
            # also set up the combo in the 'simple' editor section
            # also set up the combo in the 'simple' editor section
            if self.radExposure.isChecked():
                self.setSubcategoryList(self.standardExposureList,
                                         mySubCategory + ' [' + myType + ']')
            else:
                self.setSubcategoryList(self.standardExposureList,
                                         mySubCategory + ' [' + myUnits + ']')

    def accept(self):
        """Automatic slot executed when the ok button is pressed.

        It will write out the keywords for the layer that is active.

        Args:
           None
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        myFileName = self.layer.source()
        myFileName = os.path.splitext(str(myFileName))[0] + '.keywords'
        myKeywords = {}
        for myCounter in range(self.lstKeywords.count()):
            myExistingItem = self.lstKeywords.item(myCounter)
            myText = myExistingItem.text()
            myTokens = myText.split(':')
            myKey = str(myTokens[0]).strip()
            myValue = str(myTokens[1]).strip()
            myKeywords[myKey] = myValue

        write_keywords(myKeywords, myFileName)
        return
