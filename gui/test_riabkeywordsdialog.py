"""
Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from utilities_test import getQgisTestApp
from riabkeywordsdialog import RiabKeywordsDialog

from qgis.core import (QgsRasterLayer,
                       QgsMapLayerRegistry)
from storage.utilities_test import TESTDATA
# Get QGis app handle
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


def makePadangLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'Shakemap_Padang_2009.asc'
    myPath = os.path.join(TESTDATA, myFile)
    myBaseName = os.path.splitext(myFile)[0]
    myLayer = QgsRasterLayer(myPath, myBaseName)
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def clearLayers():
    """Clear all the loaded layers"""
    for myLayer in QgsMapLayerRegistry.instance().mapLayers():
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer)


class RiabKeywordsDialogTest(unittest.TestCase):
    """Test the risk in a box keywords GUI"""

    def setUp(self):
        """Create fresh dialog for each test"""

    def tearDown(self):
        """Destroy the dialog after each test"""
        clearLayers()

    def test_showHelp(self):
        """Test that help button works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myButton = myDialog.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = 'Help dialog was not created when help button pressed'
        assert myDialog.helpDialog is not None, myMessage

    def test_on_pbnAdvanced_toggled(self):
        """Test advanced button toggle behaviour works"""
        makePadangLayer()
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myButton = myDialog.pbnAdvanced
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myState = myDialog.grpAdvanced.isHidden()
        myExpectedState = False
        myMessage = ('Advanced options did not become visible when'
                     ' the advanced button was clicked\nGot'
                     '%s\nExpected\%s\n' % (myState, myExpectedState))

        assert myState == myExpectedState, myMessage

        # Now hide advanced again and test...
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myState = myDialog.grpAdvanced.isHidden()
        myExpectedState = True
        myMessage = ('Advanced options did not become hidden when'
                     ' the advanced button was clicked again\nGot'
                     '%s\nExpected\%s\n' % (myState, myExpectedState))
        assert not myDialog.grpAdvanced.isVisible(), myMessage

    def test_on_radHazard_toggled(self):
        """Test hazard radio button toggle behaviour works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radHazard
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the hazard radio did not add a category '
                     'to the keywords list.')
        assert myDialog.getValueForKey('category') == 'hazard', myMessage

    def test_on_radExposure_toggled(self):
        """Test exposure radio button toggle behaviour works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radExposure
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the exposure radio did not add a category '
                     'to the keywords list.')
        assert myDialog.getValueForKey('category') == 'exposure', myMessage

    def test_on_cboSubcategory_currentIndexChanged(self):
        """Test subcategory combo change event works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radHazard
        myButton.setChecked(True)
        myButton = myDialog.radExposure
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myCombo = myDialog.cboSubcategory
        QTest.mouseClick(myCombo, QtCore.Qt.LeftButton)
        QTest.keyClick(myCombo, QtCore.Qt.Key_Down)
        QTest.keyClick(myCombo, QtCore.Qt.Key_Enter)
        myMessage = ('Changing the subcategory did not add '
                     'to the keywords list for %s' %
                     myCombo.currentText())
        myKey = myDialog.getValueForKey('subcategory')
        assert myKey is not None, myMessage
        assert myKey in str(myCombo.currentText()), myMessage

    def test_setSubcategoryList(self):
        """Test set subcategory list works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myList = ['a', 'b', 'c']
        mySelectedItem = 'c'
        myDialog.setSubcategoryList(myList, mySelectedItem)
        myResult = str(myDialog.cboSubcategory.currentText())
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, mySelectedItem))

        assert myResult == mySelectedItem, myMessage

    def test_on_pbnAddToList1_clicked(self):
        """Test adding an item to the list using predefined form works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.radPredefined.setChecked(True)
        myDialog.cboKeyword.setCurrentIndex(2)
        myExpectedResult = 'foo'
        myDialog.lePredefinedValue.setText(myExpectedResult)
        QTest.mouseClick(myDialog.pbnAddToList1, QtCore.Qt.LeftButton)
        myResult = myDialog.getValueForKey('datatype')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))

        assert myResult == myExpectedResult, myMessage

    def test_on_pbnAddToList2_clicked(self):
        """Test adding an item to the list using user defened form works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.radUserDefined.setChecked(True)
        myDialog.leKey.setText('foo')
        myDialog.leValue.setText('bar')
        myExpectedResult = 'bar'
        myDialog.lePredefinedValue.setText(myExpectedResult)
        QTest.mouseClick(myDialog.pbnAddToList2, QtCore.Qt.LeftButton)
        myResult = myDialog.getValueForKey('foo')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_on_pbnRemove_clicked(self):
        """Test pressing remove works on key list"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)

        myResult = myDialog.lstKeywords.count()
        myExpectedResult = 0
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

        myDialog.addListEntry('bar', 'foo')
        myResult = myDialog.lstKeywords.count()
        myExpectedResult = 1
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_addListEntry(self):
        """Test add entry to list works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.addListEntry('bar', 'foo')
        myResult = myDialog.getValueForKey('bar')
        myExpectedResult = 'foo'
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_setCategory(self):
        """Test set category works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.setCategory('hazard')
        myExpectedResult = 'hazard'
        myResult = myDialog.getValueForKey('category')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_reset(self, thePrimaryKeywordsOnlyFlag=True):
        """Test form reset works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.leTitle.setText('Foo')
        myDialog.reset(False)
        myExpectedResult = ''
        myResult = myDialog.leTitle.text()
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

    def test_removeItemByKey(self):
        """Test remove item by its key works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.addListEntry('bar', 'foo')
        myDialog.removeItemByKey('bar')
        myResult = myDialog.lstKeywords.count()
        myExpectedResult = 0
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_removeItemByValue(self):
        """Test remove item by its value works"""
        makePadangLayer()
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myDialog.removeItemByValue('hazard')

        myKeywords = myDialog.getKeywords()
        myExpectedKeywords = {'subcategory': 'earthquake',
                             'unit': 'MMI'}
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myKeywords, myExpectedKeywords))

        assert myKeywords == myExpectedKeywords, myMessage

    def test_getValueForKey(self):
        """Test get value for key works"""
        makePadangLayer()
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myExpectedValue = 'hazard'
        myValue = myDialog.getValueForKey('category')
        myMessage = ('\nExpected key value of %s\nGot %s' %
                     (myExpectedValue, myValue))
        assert myValue == myExpectedValue, myMessage

    def test_loadStateFromKeywords(self):
        """Test load state from keywords works"""
        myDialog = RiabKeywordsDialog(PARENT, IFACE)
        myLayer = makePadangLayer()
        myDialog.layer = myLayer
        myDialog.loadStateFromKeywords()
        myKeywords = myDialog.getKeywords()

        myExpectedKeywords = {'category': 'hazard',
                             'subcategory': 'earthquake',
                             'unit': 'MMI'}
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myKeywords, myExpectedKeywords))

        assert myKeywords == myExpectedKeywords, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabKeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
