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
import hashlib  # for checking files are like we expect them to be

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)


from utilities_test import getQgisTestApp
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
        myPdf = '/tmp/out.pdf'
        if os.path.exists(myPdf):
            os.remove(myPdf)
        myMap.makePdf(myPdf)
        assert os.path.exists(myPdf)
        os.remove(myPdf)

    def test_getLegend(self):
        """Getting a legend for a generic layer works."""
        myLayer, myType = loadLayer('issue58.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myLegend = myMap.getLegend()
        myLegend.save('/tmp/getVectorLegend.png', 'PNG')
        assert False

    def test_getVectorLegend(self):
        """Getting a legend for a vector layer works."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getVectorLegend()
        myPath = '/tmp/getVectorLegend.png'
        myMap.legend.save(myPath, 'PNG')
        myData = file(myPath).read()
        myHash = hashlib.md5()
        myHash.update(myData)
        myExpectedHash = 'b2f37386f57cea585ce995a1339661d6'
        myHash = myHash.hexdigest()
        myMessage = ('Unexpected hash for vectorLegend'
                     '\nGot: %s'
                     '\nExpected: %s' % (myHash, myExpectedHash))
        assert myHash == myExpectedHash, myMessage

    def test_getRasterLegend(self):
        """Getting a legend for a raster layer works."""
        myLayer, myType = loadLayer('issue58.tif')
        del myType
        myMap = RiabMap(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getRasterLegend()
        myMap.legend.save('/tmp/getRasterLegend.png', 'PNG')
        assert False

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
        myMap.legend.save('/tmp/addSymbolToLegend.png', 'PNG')
        assert False

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
        #
        #myMap.legend.save('/tmp/addClassToLegend.png', 'PNG')
        assert False

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabDockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
