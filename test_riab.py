'''
Disaster risk assessment tool developed by AusAid - **QGIS plugin test suite.**

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

from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
from PyQt4.QtGui import QWidget
import unittest
from riab import Riab


class RiabTest(unittest.TestCase):
    """Test the risk in a box plugin stub"""

    def setUp(self):
        """Create an app that all tests can use"""
        myGuiFlag = True  # We need to enable qgis app in gui mode
        self.app = QgsApplication(sys.argv, myGuiFlag)
        #todo - softcode these paths
        myUseDefaultPathFlag = True
        self.app.setPrefixPath('/usr/local', myUseDefaultPathFlag)
        self.app.initQgis()

    def tearDown(self):
        '''Tear down - destroy the QGIS app'''
        self.app.exitQgis()

    def test_load(self):
        """Test if we are able to load our plugin"""
        print 'Testing load'
        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        Riab(myIface)


if __name__ == "__main__":
    unittest.main()
