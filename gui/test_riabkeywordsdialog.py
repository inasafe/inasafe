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
from qgisinterface import QgisInterface
from utilities_test import getQgisTestApp
from riabkeywordsdialog import RiabKeywordsDialog

from qgis.core import (QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry)
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from storage.utilities_test import TESTDATA
from storage.utilities import read_keywords
# Get QGis app handle
QGISAPP = getQgisTestApp()
# Set DOCK to test against
PARENT = QtGui.QWidget()
CANVAS = QgsMapCanvas(PARENT)
CANVAS.resize(QtCore.QSize(400, 400))

# QgisInterface is a stub implementation of the QGIS plugin interface
IFACE = QgisInterface(CANVAS)


def loadStandardLayers():
    """Helper function to load standard layers into the dialog."""
    # List all layers in the correct order.
    # NOTE: New layers *must* be added to the end of this list, otherwise
    #       tests will break.
    myFileList = ['Padang_WGS84.shp',
                  'glp10ag.asc',
                  'Shakemap_Padang_2009.asc',
                  'tsunami_max_inundation_depth_BB_utm.asc',
                  'tsunami_exposure_BB.shp',
                  'Flood_Current_Depth_Jakarta_geographic.asc',
                  'Population_Jakarta_geographic.asc',
                  'eq_yogya_2006.asc',
                  'OSM_building_polygons_20110905.shp']
    myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList)
    return myHazardLayerCount, myExposureLayerCount


def loadLayers(theLayerList, theClearFlag=True):
    """Helper function to load layers as defined in a python list."""
    # First unload any layers that may already be loaded
    if theClearFlag:
        for myLayer in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

    # Now go ahead and load our layers
    myExposureLayerCount = 0
    myHazardLayerCount = 0
    myCanvasLayers = []

    # Now create our new layers
    for myFile in theLayerList:
        # Extract basename and absolute path
        myBaseName, myExt = os.path.splitext(myFile)
        myPath = os.path.join(TESTDATA, myFile)
        myKeywordPath = myPath[:-4] + '.keywords'

        # Determine if layer is hazard or exposure
        myKeywords = read_keywords(myKeywordPath)
        msg = 'Could not read %s' % myKeywordPath
        assert myKeywords is not None, msg
        if myKeywords['category'] == 'hazard':
            myHazardLayerCount += 1
        elif myKeywords['category'] == 'exposure':
            myExposureLayerCount += 1

        # Create QGis Layer Instance
        if myExt in ['.asc', '.tif']:
            myLayer = QgsRasterLayer(myPath, myBaseName)
        elif myExt in ['.shp']:
            myLayer = QgsVectorLayer(myPath, myBaseName, 'ogr')
        else:
            myMessage = 'File %s had illegal extension' % myPath
            raise Exception(myMessage)

        myMessage = 'Layer "%s" is not valid' % str(myLayer.source())
        assert myLayer.isValid(), myMessage

        # Add layer to the registry (that QGis knows about)
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)

        # Create Map Canvas Layer Instance and add to list
        myCanvasLayers.append(QgsMapCanvasLayer(myLayer))

    # Quickly add any existing CANVAS layers to our list first
    for myLayer in CANVAS.layers():
        myCanvasLayers.append(QgsMapCanvasLayer(myLayer))
    # now load all these layers in the CANVAS
    CANVAS.setLayerSet(myCanvasLayers)

    # Add MCL's to the CANVAS
    return myHazardLayerCount, myExposureLayerCount


class RiabKeywordsDialogTest(unittest.TestCase):
    """Test the risk in a box keywords GUI"""
    dialog = None

    def setUp(self):
        """Create fresh dialog for each test"""
        loadStandardLayers()
        self.dialog = RiabKeywordsDialog(PARENT, IFACE)

    def tearDown(self):
        """Destroy the dialog after each test"""
        self.dialog.close()
        self.dialog = None

    def testDialogLoads(self):
        """Basic test to ensure the keyword dialog has loaded"""
        assert self.dialog is not None

    def test_showHelp(self):
        myButton = self.dialog.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = 'Help dialog was not created when help button pressed'
        assert self.dialog.helpDialog is not None, myMessage

    def test_on_pbnAdvanced_toggled(self):
        myButton = self.dialog.pbnAdvanced
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Advanced options did not become visible when'
                     ' the advanced button was clicked')
        assert self.dialog.grpAdvanced.isVisible(), myMessage
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Advanced options did not become hidden when'
                     ' the advanced button was clicked again')
        assert not self.dialog.grpAdvanced.isVisible(), myMessage

    def test_on_radHazard_toggled(self):
        myButton = self.dialog.radHazard
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the hazard radio did not add a category '
                     'to the keywords list.')
        assert self.dialog.getValueForKey('category') == 'hazard', myMessage

    def test_on_radExposure_toggled(self):
        myButton = self.dialog.radExposure
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myMessage = ('Toggling the exposure radio did not add a category '
                     'to the keywords list.')
        assert self.dialog.getValueForKey('category') == 'exposure', myMessage

    def test_on_cboSubcategory_currentIndexChanged(self):
        myButton = self.dialog.radExposure
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myCombo = self.dialog.cboSubcategory
        QTest.mouseClick(myCombo, QtCore.Qt.LeftButton)
        QTest.keyClick(myCombo, QtCore.Qt.Key_Down)
        QTest.keyClick(myCombo, QtCore.Qt.Key_Enter)
        myMessage = ('Changing the subcategory did not add '
                     'to the keywords list for %s' %
                     myCombo.currentText())
        myKey = self.dialog.getValueForKey('subcategory')
        assert myKey is not None, myMessage
        assert myKey in str(myCombo.currentText()), myMessage

    def test_setSubcategoryList(self, theList, theSelectedItem=None):
        pass

    def test_on_pbnAddToList1_clicked(self):
        pass

    def test_on_pbnAddToList2_clicked(self):
        pass

    def test_on_pbnRemove_clicked(self):
        pass

    def test_addListEntry(self, theKey, theValue):
        pass

    def test_setCategory(self, theCategory):
        pass

    def test_reset(self, thePrimaryKeywordsOnlyFlag=True):
        pass

    def test_removeItemByKey(self, theKey):
        pass

    def test_removeItemByValue(self, theValue):
        pass

    def test_getValueForKey(self, theKey):
        pass

    def test_loadStateFromKeywords(self):
        myFile = 'Shakemap_Padang_2009.asc'
        myPath = os.path.join(TESTDATA, myFile)
        myBaseName = os.path.splitext(myFile)[0]
        myLayer = QgsRasterLayer(myPath, myBaseName)
        self.dialog.layer = myLayer
        self.dialog.loadStateFromKeywords()
        myKeywords = self.dialog.getKeywords()
        print myKeywords
        assert myKeywords == {'category': 'hazard',
                              'subcategory': 'earthquake',
                              'unit': 'MMI',
                              'title': 'Banjir Jakarta seperti 2007'}

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabKeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
