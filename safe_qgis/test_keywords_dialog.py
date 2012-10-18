"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.1'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import shutil
from safe.engine.core import unique_filename

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest

from qgis.core import (QgsRasterLayer,
                       QgsVectorLayer,
                       QgsMapLayerRegistry)

from third_party.odict import OrderedDict
from safe_qgis.utilities_test import (getQgisTestApp,
                                      unitTestDataPath)
from safe_qgis.safe_interface import readKeywordsFromFile
from safe_qgis.keywords_dialog import KeywordsDialog
from safe_qgis.exceptions import KeywordNotFoundException
from safe_qgis.utilities import getDefaults


# For testing and demoing
from safe.common.testing import HAZDATA, TESTDATA

# Get QGis app handle
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


def makePadangLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'Shakemap_Padang_2009.asc'
    myPath = os.path.join(HAZDATA, myFile)
    myTitle = readKeywordsFromFile(myPath, 'title')
    # myTitle = 'An earthquake in Padang like in 2009'
    myLayer = QgsRasterLayer(myPath, myTitle)
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def makePadangLayerClone():
    """Helper function that copies padang keyword for testing and return it."""
    mySourceFileName = 'Shakemap_Padang_2009'
    myExts = ['.asc', '.asc.aux.xml', '.keywords',
              '.lic', '.prj', '.qml', '.sld']
    myFileName = unique_filename()
    # copy to temp file
    for ext in myExts:
        mySourcePath = os.path.join(HAZDATA, mySourceFileName + ext)
        myDestPath = os.path.join(HAZDATA, myFileName + ext)
        shutil.copy2(mySourcePath, myDestPath)
    # return a single predefined layer
    myFile = myFileName + '.asc'
    myPath = os.path.join(HAZDATA, myFile)
    myTitle = readKeywordsFromFile(myPath, 'title')
    myLayer = QgsRasterLayer(myPath, myTitle)
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer, myFileName


def makePolygonLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'kabupaten_jakarta_singlepart_3_good_attr.shp'
    myPath = os.path.join(TESTDATA, myFile)
    try:
        myTitle = readKeywordsFromFile(myPath, 'title')
    except KeywordNotFoundException:
        myTitle = 'kabupaten_jakarta_singlepart_3_good_attr'
    myLayer = QgsVectorLayer(myPath, myTitle, 'ogr')
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def makePointLayer():
    """Helper function that returns a single predefined layer"""
    myFile = 'test_buildings.shp'
    myPath = os.path.join(TESTDATA, myFile)
    try:
        myTitle = readKeywordsFromFile(myPath, 'title')
    except KeywordNotFoundException:
        myTitle = 'kabupaten_jakarta_singlepart_3_good_attr'
    myLayer = QgsVectorLayer(myPath, myTitle, 'ogr')
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def removeTempFile(myFileName='temp_Shakemap_Padang_2009'):
    """Helper function that removes temp file that created during test"""
    #myFileName = 'temp_Shakemap_Padang_2009'
    myExts = ['.asc', '.asc.aux.xml', '.keywords',
              '.lic', '.prj', '.qml', '.sld']
    for ext in myExts:
        os.remove(os.path.join(HAZDATA, myFileName + ext))


def makeKeywordlessLayer():
    """Helper function that returns a single predefined keywordless layer"""
    myFile = 'keywordless_layer.tif'
    myBasePath = unitTestDataPath('hazard')
    myPath = os.path.abspath(os.path.join(myBasePath, myFile))
    myTitle = 'Keywordless Layer'
    myLayer = QgsRasterLayer(myPath, myTitle)
    QgsMapLayerRegistry.instance().addMapLayer(myLayer)
    return myLayer


def clearLayers():
    """Clear all the loaded layers"""
    for myLayer in QgsMapLayerRegistry.instance().mapLayers():
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer)


class KeywordsDialogTest(unittest.TestCase):
    """Test the InaSAFE keywords GUI"""

    def setUp(self):
        """Create fresh dialog for each test"""
        pass

    def tearDown(self):
        """Destroy the dialog after each test"""
        clearLayers()

    def test_showHelp(self):
        """Test that help button works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = 'Help dialog was not created when help button pressed'
        assert myDialog.helpDialog is not None, myMessage

    def test_on_pbnAdvanced_toggled(self):
        """Test advanced button toggle behaviour works"""
        makePadangLayer()
        myDialog = KeywordsDialog(PARENT, IFACE)
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
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radHazard
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the hazard radio did not add a category '
                     'to the keywords list.')
        assert myDialog.getValueForKey('category') == 'hazard', myMessage

    def test_on_radPostprocessing_toggled(self):
        """Test hazard radio button toggle behaviour works"""
        myLayer = makePolygonLayer()
        myDefaults = getDefaults()
        myDialog = KeywordsDialog(PARENT, IFACE, theLayer=myLayer)
        myButton = myDialog.radPostprocessing
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the postprocessing radio did not add a '
                     'category to the keywords list.')
        assert myDialog.getValueForKey(
            'category') == 'postprocessing', myMessage

        myMessage = ('Toggling the postprocessing radio did not add an '
                     'aggregation attribute to the keywords list.')
        assert myDialog.getValueForKey(
            myDefaults['AGGR_ATTR_KEY']) == 'KAB_NAME', myMessage

        myMessage = ('Toggling the postprocessing radio did not add a '
                     'female ratio attribute to the keywords list.')

        assert myDialog.getValueForKey(
            myDefaults['FEM_RATIO_ATTR_KEY']) == \
               myDialog.tr('Use default'), myMessage

        myMessage = ('Toggling the postprocessing radio did not add a '
                     'female ratio default value to the keywords list.')
        assert float(myDialog.getValueForKey(
            myDefaults['FEM_RATIO_KEY'])) == \
               myDefaults['FEM_RATIO'], myMessage

    def test_on_dsbFemaleRatioDefault_valueChanged(self):
        """Test hazard radio button toggle behaviour works"""
        myLayer = makePolygonLayer()
        myDefaults = getDefaults()
        myDialog = KeywordsDialog(PARENT, IFACE, theLayer=myLayer)
        myButton = myDialog.radPostprocessing
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myFemaleRatioAttrBox = myDialog.cboFemaleRatioAttribute

        #set to Don't use
        myIndex = myFemaleRatioAttrBox.findText(
            myDialog.tr('Don\'t use'))
        myMessage = (myDialog.tr('Don\'t use') + ' not found')
        assert (myIndex != -1), myMessage
        myFemaleRatioAttrBox.setCurrentIndex(myIndex)

        myMessage = ('Toggling the female ratio attribute combo to'
                     ' "Don\'t use" did not add it to the keywords list.')
        assert myDialog.getValueForKey(
            myDefaults['FEM_RATIO_ATTR_KEY']) ==\
               myDialog.tr('Don\'t use'), myMessage

        myMessage = ('Toggling the female ratio attribute combo to'
                     ' "Don\'t use" did not disable dsbFemaleRatioDefault.')
        myIsEnabled = myDialog.dsbFemaleRatioDefault.isEnabled()
        assert not myIsEnabled, myMessage

        myMessage = ('Toggling the female ratio attribute combo to'
                     ' "Don\'t use" did not remove the keyword.')
        assert (myDialog.getValueForKey(myDefaults['FEM_RATIO']) is
            None), myMessage

        #set to TEST_REAL
        myIndex = myFemaleRatioAttrBox.findText('TEST_REAL')
        myMessage = ('TEST_REAL not found')
        assert (myIndex != -1), myMessage
        myFemaleRatioAttrBox.setCurrentIndex(myIndex)

        myMessage = ('Toggling the female ratio attribute combo to "TEST_REAL"'
                     ' did not add it to the keywords list.')
        assert myDialog.getValueForKey(
            myDefaults['FEM_RATIO_ATTR_KEY']) == 'TEST_REAL', myMessage

        myMessage = ('Toggling the female ratio attribute combo to "TEST_REAL"'
                     ' did not disable dsbFemaleRatioDefault.')
        myIsEnabled = myDialog.dsbFemaleRatioDefault.isEnabled()
        assert not myIsEnabled, myMessage

        myMessage = ('Toggling the female ratio attribute combo to "TEST_REAL"'
                     ' did not remove the keyword.')
        assert (myDialog.getValueForKey(myDefaults['FEM_RATIO']) is
                None), myMessage

    def Xtest_on_radExposure_toggled(self):
        """Test exposure radio button toggle behaviour works"""

        # Cannot get this test to work, but it works fine in the safe_qgis
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radExposure
        myButton.setChecked(False)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the exposure radio did not add a category '
                     'to the keywords list.')
        assert myDialog.getValueForKey('category') == 'exposure', myMessage

    def test_on_cboSubcategory_currentIndexChanged(self):
        """Test subcategory combo change event works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myButton = myDialog.radHazard
        myButton.setChecked(True)
        myButton = myDialog.radExposure
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myCombo = myDialog.cboSubcategory
        QTest.mouseClick(myCombo, QtCore.Qt.LeftButton)
        QTest.keyClick(myCombo, QtCore.Qt.Key_Up)
        QTest.keyClick(myCombo, QtCore.Qt.Key_Enter)
        myMessage = ('Changing the subcategory did not add '
                     'to the keywords list for %s' %
                     myCombo.currentText())
        myKey = myDialog.getValueForKey('subcategory')

        assert myKey is not None, myMessage
        assert myKey in str(myCombo.currentText()), myMessage

    def test_setSubcategoryList(self):
        """Test set subcategory list works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myList = OrderedDict([('population [density]',
                                      'population [density]'),
                                     ('population [count]',
                                      'population [count]'),
                                     ('building',
                                      'building'),
                                     ('building [osm]',
                                      'building [osm]'),
                                     ('building [sigab]',
                                      'building [sigab]'),
                                     ('roads',
                                      'roads')])
        mySelectedItem = 'building'
        myDialog.setSubcategoryList(myList, mySelectedItem)
        myResult = str(myDialog.cboSubcategory.currentText())
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, mySelectedItem))

        assert myResult == mySelectedItem, myMessage

    def test_on_pbnAddToList1_clicked(self):
        """Test adding an item to the list using predefined form works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.radPredefined.setChecked(True)
        myDialog.cboKeyword.setCurrentIndex(2)
        myExpectedResult = 'foo'
        myDialog.lePredefinedValue.setText(myExpectedResult)
        # Work around for commented out line below
        myDialog.on_pbnAddToList1_clicked()
        #QTest.mouseClick(myDialog.pbnAddToList1, QtCore.Qt.LeftButton)
        myResult = myDialog.getValueForKey('datatype')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))

        assert myResult == myExpectedResult, myMessage

    def test_on_pbnAddToList2_clicked(self):
        """Test adding an item to the list using user defened form works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.radUserDefined.setChecked(True)
        myDialog.leKey.setText('foo')
        myDialog.leValue.setText('bar')
        myExpectedResult = 'bar'
        myDialog.lePredefinedValue.setText(myExpectedResult)
        # Work around for commented out line below
        myDialog.on_pbnAddToList2_clicked()
        #QTest.mouseClick(myDialog.pbnAddToList2, QtCore.Qt.LeftButton)
        myResult = myDialog.getValueForKey('foo')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_on_pbnRemove_clicked(self):
        """Test pressing remove works on key list"""
        myDialog = KeywordsDialog(PARENT, IFACE)
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
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.addListEntry('bar', 'foo')
        myResult = myDialog.getValueForKey('bar')
        myExpectedResult = 'foo'
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_addWarningsForColons(self):
        """Test add entry to list works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.addListEntry('bar', 'fo:o')
        myResult = myDialog.getValueForKey('bar')
        myExpectedResult = 'fo.o'
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage
        #
        # Check the user gets a message if they put colons in the value
        #
        myExpectedResult = 'Colons are not allowed, replaced with "."'
        myResult = str(myDialog.lblMessage.text())
        myMessage = ('lblMessage error \nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage
        #
        # Check the user gets a message if they put colons in the key
        #
        myDialog.addListEntry('ba:r', 'foo')
        myExpectedResult = 'Colons are not allowed, replaced with "."'
        myResult = str(myDialog.lblMessage.text())
        myMessage = ('lblMessage error \nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_setCategory(self):
        """Test set category works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.reset(False)
        myDialog.setCategory('hazard')
        myExpectedResult = 'hazard'
        myResult = myDialog.getValueForKey('category')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        #print 'Dict', myDialog.getKeywords()
        assert myResult == myExpectedResult, myMessage

    def test_reset(self):
        """Test form reset works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.leTitle.setText('Foo')
        myDialog.reset(False)
        myExpectedResult = ''
        myResult = myDialog.leTitle.text()
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

    def test_removeItemByKey(self):
        """Test remove item by its key works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
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
        myDialog = KeywordsDialog(PARENT, IFACE)
        myDialog.removeItemByValue('hazard')

        myKeywords = myDialog.getKeywords()
        myExpectedKeywords = {'source': 'USGS',
                              'title': 'An earthquake in Padang like in 2009',
                              'subcategory': 'earthquake',
                              'unit': 'MMI'}
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myKeywords, myExpectedKeywords))

        assert myKeywords == myExpectedKeywords, myMessage

    def test_getValueForKey(self):
        """Test get value for key works"""
        makePadangLayer()
        myDialog = KeywordsDialog(PARENT, IFACE)
        myExpectedValue = 'hazard'
        myValue = myDialog.getValueForKey('category')
        myMessage = ('\nExpected key value of %s\nGot %s' %
                     (myExpectedValue, myValue))
        assert myValue == myExpectedValue, myMessage

    def test_loadStateFromKeywords(self):
        """Test load state from keywords works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myLayer = makePadangLayer()
        myDialog.layer = myLayer
        myDialog.loadStateFromKeywords()
        myKeywords = myDialog.getKeywords()

        myExpectedKeywords = {'title': 'An earthquake in Padang like in 2009',
                              'category': 'hazard',
                              'source': 'USGS',
                              'subcategory': 'earthquake',
                              'unit': 'MMI'}
        myMessage = ('\nGot:\n%s\nExpected:\n%s\n' %
                     (myKeywords, myExpectedKeywords))
        assert myKeywords == myExpectedKeywords, myMessage

    def test_checkStateWhenKeywordsAbsent(self):
        """Test load state from keywords works"""
        myDialog = KeywordsDialog(PARENT, IFACE)
        myLayer = makeKeywordlessLayer()
        myDialog.layer = myLayer
        myDialog.loadStateFromKeywords()
        myKeywords = myDialog.getKeywords()
        #check that a default title is given (see
        #https://github.com/AIFDR/inasafe/issues/111)
        myExpectedKeywords = {'category': 'exposure',
                              'title': 'Keywordless Layer'}
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myKeywords, myExpectedKeywords))
        assert myKeywords == myExpectedKeywords, myMessage

    def test_addKeywordWhenPressOkButton(self):
        """Test add keyword when ok button is pressed."""
        #_, myFile = makePadangLayerClone()
        makePadangLayerClone()
        myDialog = KeywordsDialog(PARENT, IFACE)

        myDialog.radUserDefined.setChecked(True)
        myDialog.leKey.setText('foo')
        myDialog.leValue.setText('bar')
        okButton = myDialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        QTest.mouseClick(okButton, QtCore.Qt.LeftButton)

        # delete temp file
        # removeTempFile(myFile)

        myExpectedResult = 'bar'
        myResult = myDialog.getValueForKey('foo')
        myMessage = ('\nGot: %s\nExpected: %s\n' %
                     (myResult, myExpectedResult))
        assert myExpectedResult == myResult, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
