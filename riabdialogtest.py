"""
Disaster risk assessment tool developed by AusAid - **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or 
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import sys
import sys
#todo - softcode in a configuration file
sys.path.append("/usr/local/share/qgis/python/")
import unittest
from PyQt4.QtGui import QWidget
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
from riabdialog import RiabDialog

class RiabDialogTest(unittest.TestCase):
    '''Test the risk in a box GUI'''
    
    def setUp(self):
        '''Create an app that all tests can use'''
        myGuiFlag = True #we need to enable qgis app in gui mode
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
        '''Set all form elements to default state'''
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


if __name__ == "__main__":
    unittest.main()
