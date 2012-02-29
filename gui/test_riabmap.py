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
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)


from utilities_test import (getQgisTestApp, assertHashForFile)
from gui.riabmap import RiabMap
from PyQt4 import QtGui
from qgis.core import QgsSymbol
from utilities_test import loadLayer
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""

    def test_riabMap(self):
        """Test making a pdf using the RiabMap class."""
        loadLayer('issue58.tif')
        myMap = RiabMap(IFACE)
        myPath = '/tmp/out.pdf'
        if os.path.exists(myPath):
            os.remove(myPath)
        myMap.makePdf(myPath)
        assert os.path.exists(myPath)
        os.remove(myPath)

    def test_getLegend(self):
        """Getting a legend for a generic layer works."""
        myLayer, myType = loadLayer('issue58.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myLegend = myMap.getLegend()
        myPath = '/tmp/getLegend.png'
        myLegend.save(myPath, 'PNG')
        myExpectedHash = '1234'
        assertHashForFile(myExpectedHash, myPath)

    def test_getVectorLegend(self):
        """Getting a legend for a vector layer works."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getVectorLegend()
        myPath = '/tmp/getVectorLegend.png'
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = 'b2f37386f57cea585ce995a1339661d6'
        assertHashForFile(myExpectedHash, myPath)

    def test_getRasterLegend(self):
        """Getting a legend for a raster layer works."""
        myLayer, myType = loadLayer('issue58.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getRasterLegend()
        myPath = '/tmp/getRasterLegend.png'
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '1234'
        assertHashForFile(myExpectedHash, myPath)

    def addSymbolToLegend(self):
        """Test we can add a symbol to the legend."""
        myLayer, myType = loadLayer('issue58.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.legend = None
        mySymbol = QgsSymbol()
        mySymbol.setColor(QtGui.QColor(12, 34, 56))
        myMap.addSymbolToLegend(mySymbol,
                                theMin=0,
                                theMax=2,
                                theCategory=None,
                                theLabel='Foo')
        myPath = '/tmp/addSymbolToLegend.png'
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '1234'
        assertHashForFile(myExpectedHash, myPath)

    def test_addClassToLegend(self):
        """Test we can add a class to the map legend."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.legend = None
        myColour = QtGui.QColor(12, 34, 126)
        myMap.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory='foo',
                               theLabel='bar')
        myMap.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory='foo',
                               theLabel='foo')
        myPath = '/tmp/addClassToLegend.png'
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = 'fd28fa6703453a8aa3198e0362e56d01'
        assertHashForFile(myExpectedHash, myPath)

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabDockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
