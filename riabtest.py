"""
Disaster risk assessment tool developed by AusAid - **QGIS plugin test suite.**

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
#todo - softcode in a configuration file
sys.path.append("/usr/local/share/qgis/python/")
from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
import unittest
from PyQt4.QtGui import QApplication, QWidget
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
from riab import Riab

class RiabTest(unittest.TestCase):
    '''Test the risk in a box plugin stub'''
    
    def setUp(self):
        '''Create the GUI'''
        myGuiFlag = True #we need to enable qgis app in gui mode
        self.app = QgsApplication(sys.argv, True)
        #todo - softcode these paths
        self.app.setPrefixPath('/usr/local')
        self.app.setPluginPath('/usr/local/lib/qgis/providers')
        self.app.initQgis()


    def tearDown(self):
        self.app.exitQgis()
        
  
    def test_load(self):
        print 'Testing load'
        myParent = QWidget()
        myCanvas = QgsMapCanvas(myParent)
        myIface = QgisInterface(myCanvas)
        myStub = Riab(myIface)
        myStub.run()

if __name__ == "__main__":
    unittest.main()        