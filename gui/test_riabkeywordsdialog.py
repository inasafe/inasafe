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
#from PyQt4.QtTest import QTest
from qgisinterface import QgisInterface
from utilities_test import getQgisTestApp
from riabkeywordsdialog import RiabKeywordsDialog
from qgis.gui import QgsMapCanvas
# Get QGis app handle
QGISAPP = getQgisTestApp()

# Set DOCK to test against
PARENT = QtGui.QWidget()
CANVAS = QgsMapCanvas(PARENT)
CANVAS.resize(QtCore.QSize(400, 400))

# QgisInterface is a stub implementation of the QGIS plugin interface
IFACE = QgisInterface(CANVAS)
DIALOG = RiabKeywordsDialog(PARENT, IFACE)


class RiabKeywordsDialogTest(unittest.TestCase):
    """Test the risk in a box keywords GUI"""
    def testDialogLoads(self):
        """Basic test to ensure the keyword dialog has loaded"""
        assert DIALOG is not None

    def test_showHelp(self):
        pass

    def test_on_pbnAdvanced_toggled(self, theFlag):
        pass

    def test_on_radHazard_toggled(self, theFlag):
        pass

    def test_on_radExposure_toggled(self, theFlag):
        pass

    def test_on_cboSubcategory_currentIndexChanged(self, theIndex=None):
        pass

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
        pass

    def test_accept(self):
        pass

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabKeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
