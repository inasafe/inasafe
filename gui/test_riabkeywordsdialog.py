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
GUI_CONTEXT_FLAG = False
DIALOG = RiabKeywordsDialog(IFACE, GUI_CONTEXT_FLAG)


class RiabKeywordsDialogTest(unittest.TestCase):
    """Test the risk in a box keywords GUI"""
    pass


if __name__ == '__main__':
    suite = unittest.makeSuite(RiabKeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
