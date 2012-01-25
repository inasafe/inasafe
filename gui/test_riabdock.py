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
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os
import unittest
from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from utilities import get_exception_with_stacktrace
from utilities import get_qgis_test_app
from qgis.core import (QgsApplication,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry)
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgisinterface import QgisInterface
from gui.riabdock import RiabDock
from impactcalculator import ImpactCalculator

qgis_app = get_qgis_test_app()

# Set form to test against
parent = QtGui.QWidget()
canvas = QgsMapCanvas(parent)
canvas.resize(QtCore.QSize(400, 400))
iface = QgisInterface(canvas)
myGuiContextFlag = False
form = RiabDock(iface, myGuiContextFlag)


def clearForm():
    """Helper function to  set all form elements to default state"""
    form.ui.cboHazard.clear()
    form.ui.cboExposure.clear()
    form.ui.cboFunction.setCurrentIndex(0)


def populateForm():
    """A helper function to populate the form and set it to a valid state."""
    loadLayers()
    form.ui.cboHazard.setCurrentIndex(0)
    form.ui.cboExposure.setCurrentIndex(0)
    #QTest.mouseClick(myHazardItem, Qt.LeftButton)
    #QTest.mouseClick(myExposureItem, Qt.LeftButton)


def loadLayers():
    """Helper function to load layers into the dialog."""

    # First unload any layers that may already be loaded
    for myLayer in QgsMapLayerRegistry.instance().mapLayers():
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

    # Now go ahead and load our layers
    myRoot = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
    myVectorPath = os.path.join(myRoot, 'riab_test_data',
                                'Padang_WGS84.shp')
    myVectorLayer = QgsVectorLayer(myVectorPath, 'points', 'ogr')
    msg = 'Vector layer "%s" is not valid' % str(myVectorLayer.source())
    assert myVectorLayer.isValid(), msg

    myRasterPath = os.path.join(myRoot, 'riab_test_data',
                                'Shakemap_Padang_2009.asc')
    myFileInfo = QtCore.QFileInfo(myRasterPath)
    myBaseName = myFileInfo.baseName()
    myRasterLayer = QgsRasterLayer(myRasterPath, myBaseName)
    msg = 'Raster layer "%s" is not valid' % str(myRasterLayer.source())
    assert myRasterLayer.isValid(), msg

    QgsMapLayerRegistry.instance().addMapLayer(myVectorLayer)
    myVectorCanvasLayer = QgsMapCanvasLayer(myVectorLayer)
    QgsMapLayerRegistry.instance().addMapLayer(myRasterLayer)
    myRasterCanvasLayer = QgsMapCanvasLayer(myRasterLayer)
    canvas.setLayerSet([myVectorCanvasLayer, myRasterCanvasLayer])
    form.getLayers()


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""

    def test_defaults(self):
        """Test the GUI in its default state"""
        self.assertEqual(form.ui.cboHazard.currentIndex(), -1)
        self.assertEqual(form.ui.cboExposure.currentIndex(), -1)
        self.assertEqual(form.ui.cboFunction.currentIndex(), -1)

    def test_validate(self):
        """Test that the validate function works as expected."""

        # First check that we DONT validate a clear form
        clearForm()
        myFlag, myMessage = form.validate()
        assert myMessage is not None, 'No reason for failure given'

        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check we DO validate a populated form
        populateForm()
        myFlag = form.validate()
        myMessage = ('Validation expected to pass on' +
                     ' a populated for with selections.')
        assert(myFlag), myMessage

    def test_setOkButtonStatus(self):
        """Test that the OK button changes properly according to
        form validity."""

        # First check that we ok ISNT enabled on a clear form
        clearForm()
        myFlag, myMessage = form.validate()

        assert myMessage is not None, 'No reason for failure given'
        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check OK IS enabled on a populated form
        populateForm()
        myFlag = form.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated form with selections.')
        assert(myFlag), myMessage

    def test_run(self):
        """Test that the ok button works as expected"""

        # Push OK with the left mouse button
        clearForm()
        loadLayers()
        myOkWidget = form.ui.pbnRunStop
        QTest.mouseClick(myOkWidget, QtCore.Qt.LeftButton)
        #QTest.keyClicks(
        #  form.ui.buttonBox.button(form.ui.buttonBox.Cancel), " ")

    def test_loadLayers(self):
        """Load some layers in the canvas, call load layers
         and verify that the list widget was update appropriately
        """

        clearForm()
        loadLayers()
        msg = 'Expect 1 layer in hazard list widget but got %s' % \
              form.ui.cboHazard.count()
        self.assertEqual(form.ui.cboExposure.count(), 1), msg

        msg = 'Expect 1 layer in exposure list widget but got %s' % \
              form.ui.cboExposure.count()
        self.assertEqual(form.ui.cboExposure.count(), 1), msg


if __name__ == '__main__':
    unittest.main()
