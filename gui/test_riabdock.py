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
from gui.riabexceptions import QgisPathException
from utilities import get_exception_with_stacktrace

# Check if a qgispath.txt file exists in the plugin folder (you
# need to rename it from qgispath.txt.templ in the standard plugin
# distribution) and if it does, read the qgis path

ROOT = os.path.dirname(__file__)
PATH = os.path.abspath(os.path.join(ROOT, 'qgispath.txt'))
QGIS_PATH = None  # e.g. /usr/local if QGIS is installed under there
if os.path.isfile(PATH):
    try:
        QGIS_PATH = file(PATH, 'rt').readline().rstrip()
        sys.path.append(os.path.join(QGIS_PATH, 'share', 'qgis', 'python'))
        #print sys.path
    except Exception, e:
        raise QgisPathException


from qgis.core import QgsApplication
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgisinterface import QgisInterface
from gui.riabdock import RiabDock


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""
    app = None

    def setUp(self):
        """Create an app that all tests can use"""
        print 'RiabDockTest - setUp called'
        if not self.app:
            myGuiFlag = True  # We need to enable qgis app in gui mode
            self.app = QgsApplication(sys.argv, myGuiFlag)
            myUseDefaultPathFlag = True
            self.app.setPrefixPath(QGIS_PATH, myUseDefaultPathFlag)
            self.app.initQgis()
            self.parent = QtGui.QWidget()
            self.canvas = QgsMapCanvas(self.parent)
            self.canvas.resize(QtCore.QSize(400, 400))
            self.iface = QgisInterface(self.canvas)
            myGuiContextFlag = False

        self.form = RiabDock(self.iface, myGuiContextFlag)

    def tearDown(self):
        """Tear down - destroy the QGIS app"""
        print 'RiabDockTest tearDown called'
        self.form.destroy()

    def __del__(self):
        """Destructor reimplemented to gracefully exit QGIS."""
        print 'Destoying dialog'
        self.form.destroy()
        print 'Destroying canvas'
        self.canvas.destroy()
        print 'Destroying parent widget'
        self.parent.destroy()
        print 'Unloading all layers'
        for myLayer in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

        print 'Exiting QGIS'
        self.app.exitQgis()

    def clearForm(self):
        """Helper function to  set all form elements to default state"""
        self.form.ui.cboHazard.clear()
        self.form.ui.cboExposure.clear()
        self.form.ui.cboFunction.setCurrentIndex(0)

    def populateForm(self):
        """A helper function to populate the form and set it to a
        valid state."""
        self.loadLayers()
        self.form.ui.cboHazard.setCurrentIndex(0)
        self.form.ui.cboExposure.setCurrentIndex(0)
        #QTest.mouseClick(myHazardItem, Qt.LeftButton)
        #QTest.mouseClick(myExposureItem, Qt.LeftButton)

    def Xtest_defaults(self):
        """Test the GUI in its default state"""
        self.assertEqual(self.form.ui.cboHazard.currentIndex(), -1)
        self.assertEqual(self.form.ui.cboExposure.currentIndex(), -1)
        self.assertNotEqual(self.form.ui.cboFunction.currentIndex(), -1)

    def Xtest_validate(self):
        """Test that the validate function works as expected."""
        # First check that we DONT validate a clear form
        self.clearForm()
        myFlag, myMessage = self.form.validate()
        self.assertIsNot(myMessage, None, 'No reason for failure given')
        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)
        # Now check we DO validate a populated form
        self.populateForm()
        myFlag = self.form.validate()
        myMessage = ('Validation expected to pass on' +
                     ' a populated for with selections.')
        assert(myFlag), myMessage

    def Xtest_setOkButtonStatus(self):
        """Test that the OK button changes properly according to
        form validity."""
        # First check that we ok ISNT enabled on a clear form
        self.clearForm()
        myFlag, myMessage = self.form.validate()
        self.assertIsNot(myMessage, None, 'No reason for failure given')
        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)
        # Now check OK IS enabled on a populated form
        self.populateForm()
        myFlag = self.form.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated form with selections.')
        assert(myFlag), myMessage

    def Xtest_run(self):
        """Test that the ok button works as expected"""
        # Push OK with the left mouse button
        self.clearForm()
        self.loadLayers()
        myOkWidget = self.form.ui.pbnRunStop
        QTest.mouseClick(myOkWidget, QtCore.Qt.LeftButton)
        #QTest.keyClicks(
        #  self.form.ui.buttonBox.button(self.form.ui.buttonBox.Cancel), " ")

    def loadLayers(self):
        """Helper function to load layers into the dialog."""
        # First unload any layers that may already be loaded
        for myLayer in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(myLayer)
        # Now go ahead and load our layers
        myVectorPath = os.path.join(ROOT, 'testdata', 'Jakarta_sekolah.shp')
        myVectorLayer = QgsVectorLayer(myVectorPath, 'points', 'ogr')
        msg = 'Vector layer "%s" is not valid' % str(myVectorLayer.source())
        assert myVectorLayer.isValid(), msg

        myRasterPath = os.path.join(ROOT, 'testdata',
                                    'current_flood_depth_jakarta.asc')
        myFileInfo = QtCore.QFileInfo(myRasterPath)
        myBaseName = myFileInfo.baseName()
        myRasterLayer = QgsRasterLayer(myRasterPath, myBaseName)
        msg = 'Raster layer "%s" is not valid' % str(myRasterLayer.source())
        assert myRasterLayer.isValid(), msg

        QgsMapLayerRegistry.instance().addMapLayer(myVectorLayer)
        myVectorCanvasLayer = QgsMapCanvasLayer(myVectorLayer)
        QgsMapLayerRegistry.instance().addMapLayer(myRasterLayer)
        myRasterCanvasLayer = QgsMapCanvasLayer(myRasterLayer)
        self.canvas.setLayerSet([myVectorCanvasLayer, myRasterCanvasLayer])
        self.form.getLayers()

    def Xtest_loadLayers(self):
        """Load some layers in the canvas, call load layers
         and verify that the list widget was update appropriately
        """

        self.clearForm()
        self.loadLayers()
        msg = 'Expect 1 layer in hazard list widget but got %s' % \
              self.form.ui.cboHazard.count()
        self.assertEqual(self.form.ui.cboExposure.count(), 1), msg

        msg = 'Expect 1 layer in exposure list widget but got %s' % \
              self.form.ui.cboExposure.count()
        self.assertEqual(self.form.ui.cboExposure.count(), 1), msg

    def Xtest_stacktrace(self):
        """Test HTML wrapping of stacktrace
        """

        myCalculator = ImpactCalculator()
        try:
            myCalculator.getOptimalExtent('aoeu', 'oaeu', [])
        except Exception, e:
            # Display message and traceback
            msg = get_exception_with_stacktrace(e, html=True)

            #print msg
            self.form.ui.wvResults.setHtml(msg)

            # Look at state of
            myContent = self.form.ui.wvResults.html()
            #print myContent


if __name__ == '__main__':
    unittest.main()
