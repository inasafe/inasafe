'''
Disaster risk assessment tool developed by AusAid - **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

'''

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os

# TODO - softcode in a configuration file
sys.path.append('/usr/local/share/qgis/python/')

import unittest
from PyQt4.QtGui import QWidget
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt, QFileInfo
from qgis.core import QgsApplication
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
from riabdialog import RiabDialog

ROOT = os.path.dirname(__file__)


class RiabDialogTest(unittest.TestCase):
    '''Test the risk in a box GUI'''

    def setUp(self):
        '''Create an app that all tests can use'''

        myGuiFlag = True  # We need to enable qgis app in gui mode
        self.app = QgsApplication(sys.argv, True)
        #todo - softcode these paths
        self.app.setPrefixPath('/usr/local')
        self.app.setPluginPath('/usr/local/lib/qgis/providers')
        self.app.initQgis()
        self.parent = QWidget()
        self.canvas = QgsMapCanvas(self.parent)
        self.iface = QgisInterface(self.canvas)
        self.form = RiabDialog(self.iface)

    def clearForm(self):
        '''Helper function to  set all form elements to default state'''
        self.form.ui.lstLayers.clear()
        self.form.ui.cboHazard.setCurrentIndex(0)
        self.form.ui.cboExposure.setCurrentIndex(0)
        self.form.ui.cboFunction.setCurrentIndex(0)

    def test_defaults(self):
        '''Test the GUI in its default state'''
        # Note you can also use almostEqual for inexact comparisons
        self.assertEqual(self.form.ui.lstLayers.count(), 0)
        self.assertEqual(self.form.ui.cboHazard.currentIndex(), 0)
        self.assertEqual(self.form.ui.cboExposure.currentIndex(), 0)
        self.assertEqual(self.form.ui.cboFunction.currentIndex(), 0)

        # Push OK with the left mouse button
        myOkWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(myOkWidget, Qt.LeftButton)
        #QTest.keyClicks(
        #  self.form.ui.buttonBox.button(self.form.ui.buttonBox.Cancel), " ")

    def test_loadLayers(self):
        '''Load some layers in the canvas, call load layers
         and verify that the list widget was update appropriately
        '''

        self.clearForm()
        myVectorPath = os.path.join(ROOT, 'testdata', 'Jakarta_sekolah.shp')
        myVectorLayer = QgsVectorLayer(myVectorPath, 'points', 'ogr')
        msg = 'Vector layer "%s" is not valid' % str(myVectorLayer.source())
        assert myVectorLayer.isValid(), msg

        myRasterPath = os.path.join(ROOT, 'testdata',
                                    'current_flood_depth_jakarta.asc')
        myFileInfo = QFileInfo(myRasterPath)
        myBaseName = myFileInfo.baseName()
        myRasterLayer = QgsRasterLayer(myRasterPath, myBaseName)
        msg = 'Raster layer "%s" is not valid' % str(myRasterLayer.source())
        assert myRasterLayer.isValid(), msg

        QgsMapLayerRegistry.instance().addMapLayer(myVectorLayer)
        myVectorCanvasLayer = QgsMapCanvas(myVectorLayer)
        QgsMapLayerRegistry.instance().addMapLayer(myRasterLayer)
        myRasterCanvasLayer = QgsMapCanvas(myRasterLayer)
        self.form.getLayers()
        self.assertEqual(self.form.ui.lstLayers.count(), 2)


if __name__ == '__main__':
    unittest.main()
