"""
Disaster risk assessment tool developed by AusAid - **RiabClipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from riabexceptions import QgisPathException

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

from qgis.core import QgsApplication, QgsRectangle, QgsVectorLayer
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
import unittest
from riabclipper import clipLayer


class RiabTest(unittest.TestCase):
    """Test the risk in a box clipper"""
    app = None

    def setUp(self):
        """Test if we can clip a layer nicely."""
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
            myRoot = os.path.dirname(__file__)
            self.vectorPath = os.path.join(myRoot, 'riab_test_data',
                                       'Padang_WGS84.shp')
            self.rasterPath = os.path.join(myRoot, 'riab_test_data',
                                        'Shakemap_Padang_2009.asc')

    def test_clipVector(self):
        # create a vector
        myName = 'padang'
        myVectorLayer = QgsVectorLayer(self.vectorPath, myName, 'ogr')
        # create a bounding box
        myRect = QgsRectangle(100.03, -1.14, 100.81, -0.73)
        # clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myRect)
        # check the output is valid
        assert(os.path.exists(myResult))


if __name__ == '__main__':
    unittest.main()
