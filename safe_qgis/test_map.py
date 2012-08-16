"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from PyQt4 import QtGui
from qgis.core import (QgsSymbol,
                       QgsMapLayerRegistry,
                       QgsRectangle,
                       QgsComposerPicture)
from qgis.gui import QgsMapCanvasLayer

from safe_qgis.utilities_test import (getQgisTestApp,
                                assertHashForFile,
                                hashForFile,
                                assertHashesForFile)
from safe_qgis.map import Map
from safe_qgis.utilities_test import (loadLayer, setJakartaGeoExtent)
from safe_qgis.utilities import getTempDir
try:
    from pydevd import *  # pylint: disable=F0401
    print 'Remote debugging is enabled.'
    DEBUG = True
except ImportError:
    print 'Debugging was disabled'

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class MapTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""
    def setUp(self):
        """Setup fixture run before each tests"""
        myRegistry = QgsMapLayerRegistry.instance()
        for myLayer in myRegistry.mapLayers():
            myRegistry.removeMapLayer(myLayer)

    def test_inasafeMap(self):
        """Test making a pdf using the Map class."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myMap = Map(IFACE)
        myRect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(myRect)
        CANVAS.refresh()
        myMap.setImpactLayer(myLayer)
        myPath = os.path.join(getTempDir(), 'outCustom.pdf')
        if os.path.exists(myPath):
            os.remove(myPath)
        myMap.makePdf(myPath)
        assert os.path.exists(myPath)
        # ,, note:: Template writing is experimental
        myMap.writeTemplate(os.path.join(getTempDir(), 'template.qpt'))
        #os.remove(myPath)

    def test_getLegend(self):
        """Getting a legend for a generic layer works."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        assert myMap.layer is not None
        myLegend = myMap.getLegend()
        myPath = os.path.join(getTempDir(), 'getLegend.png')
        myLegend.save(myPath, 'PNG')
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        myExpectedHashes = ['',  # win
                            'd0c3071c4babe7db4f9762b311d61184',  # ub12.04xiner
                            'b94cfd8a10d709ff28466ada425f24c8',  # ub11.04-64
                            '00dc58aa50867de9b617ccfab0d13f21',  # ub12.04
                            'e65853e217a4c9b0c2f303dd2aadb373',  # ub12.04 xvfb
                            'e4273364b33a943e1108f519dbe8e06c',  # ub12.04-64
                            '91177a81bee4400be4e85789e3be1e91',  # binary read
                            '57da6f81b4a55507e1bed0b73423244b',  # wVistaSP2-32
                            ''
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

    def test_getVectorLegend(self):
        """Getting a legend for a vector layer works."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getVectorLegend()
        myPath = os.path.join(getTempDir(), 'getVectorLegend.png')
        myMap.legend.save(myPath, 'PNG')
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        # Results currently identical to getLegend as image is same
        myExpectedHashes = ['',  # win
                            'd0c3071c4babe7db4f9762b311d61184',  # ub12.04 xinr
                            'b94cfd8a10d709ff28466ada425f24c8',  # ub11.04-64
                            '00dc58aa50867de9b617ccfab0d13f21',  # ub12.04
                            'e65853e217a4c9b0c2f303dd2aadb373',  # ub12.04 xvfb
                            'e4273364b33a943e1108f519dbe8e06c',  # ub12.04-64
                            # ub11.04-64 laptop
                            '91177a81bee4400be4e85789e3be1e91',  # Binary Read
                            '57da6f81b4a55507e1bed0b73423244b',  # wVistaSP2-32
                            ''
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

    def test_getRasterLegend(self):
        """Getting a legend for a raster layer works."""
        myLayer, myType = loadLayer('test_floodimpact.tif')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.getRasterLegend()
        myPath = os.path.join(getTempDir(), 'getRasterLegend.png')
        myMap.legend.save(myPath, 'PNG')
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        myExpectedHashes = ['',  # win
                            '9ead6ce0ac789adc65a6f00bd2d1f709',  # ub12.04xiner
                            '84bc3d518e3a0504f8dc36dfd620394e',  # ub11.04-64
                            'b68ccc328de852f0c66b8abe43eab3da',  # ub12.04
                            'cd5fb96f6c5926085d251400dd3b4928',  # ub12.04 xvfb
                            'a654d0dcb6b6d14b0a7a62cd979c16b9',  # ub12.04-64
                            # ub11.04-64 laptop
                            '9692ba8dbf909b8fe3ed27a8f4924b78',  # binary read
                            '5f4ef033bb1d6f36af4c08db55ca63be',  # wVistaSP2-32
                            '',
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

    def addSymbolToLegend(self):
        """Test we can add a symbol to the legend."""
        myLayer, myType = loadLayer('test_floodimpact.tif')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.legend = None
        mySymbol = QgsSymbol()
        mySymbol.setColor(QtGui.QColor(12, 34, 56))
        myMap.addSymbolToLegend(mySymbol,
                                theMin=0,
                                theMax=2,
                                theCategory=None,
                                theLabel='Foo')
        myPath = os.path.join(getTempDir(), 'addSymbolToLegend.png')
        myMap.legend.save(myPath, 'PNG')
        myExpectedHash = '1234'
        assertHashForFile(myExpectedHash, myPath)

    def test_addClassToLegend(self):
        """Test we can add a class to the map legend."""
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.legend = None
        myColour = QtGui.QColor(12, 34, 126)
        myMap.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory=None,
                               theLabel='bar')
        myMap.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory=None,
                               theLabel='foo')
        myPath = os.path.join(getTempDir(), 'addClassToLegend.png')
        myMap.legend.save(myPath, 'PNG')
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        myExpectedHashes = ['',  # win
                            '67c0f45792318298664dd02cc0ac94c3',  # ub12.04xiner
                            'ea0702782c2ed5d950c427fbe1743858',  # ub11.04-64
                            '53e0ba1144e071ad41756595d29bf444',  # ub12.04
                            '0681c3587305074bc9272f456fb4dd09',  # ub12.04 xvfb
                            'a37443d70604bdc8c279576b424a158c',  # ub12.04-64
                            # ub11.04-64 laptop
                            '944cee3eb9d916816b60ef41e8069683',  # binary read
                            'de3ceb6547ffc6c557d031c0b7ee9e75',  # wVistaSP2-32
                            '',
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

    def test_getMapTitle(self):
        """Getting the map title from the keywords"""
        myLayer, myType = loadLayer('test_floodimpact.tif')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myTitle = myMap.getMapTitle()
        myExpectedTitle = 'Penduduk yang Mungkin dievakuasi'
        myMessage = 'Expected: %s\nGot:\n %s' % (myExpectedTitle, myTitle)
        assert myTitle == myExpectedTitle, myMessage

    def test_handleMissingMapTitle(self):
        """Missing map title from the keywords fails gracefully"""
        # TODO running OSM Buildngs with Pendudk Jakarta
        # wasthrowing an error when requesting map title
        # that this test wasnt replicating well
        myLayer, myType = loadLayer('population_padang_1.asc')
        del myType
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myTitle = myMap.getMapTitle()
        myExpectedTitle = None
        myMessage = 'Expected: %s\nGot:\n %s' % (myExpectedTitle, myTitle)
        assert myTitle == myExpectedTitle, myMessage

    def Xtest_renderTable(self):
        """Test that html renders nicely. Commented out for now until we work
        out how to get webkit to do offscreen rendering nicely."""
        myFilename = 'test_floodimpact.tif'
        myLayer, myType = loadLayer(myFilename)
        CANVAS.refresh()
        del myType
        myMessage = 'Layer is not valid: %s' % myFilename
        assert myLayer.isValid(), myMessage
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myPixmap = myMap.renderImpactTable()
        assert myPixmap is not None
        myExpectedWidth = 500
        myExpectedHeight = 300
        myMessage = 'Invalid width - got %s expected %s' % (
                                    myPixmap.width(),
                                    myExpectedWidth)
        assert myPixmap.width() == myExpectedWidth, myMessage
        myMessage = 'Invalid height - got %s expected %s' % (
                                    myPixmap.height(),
                                    myExpectedHeight)
        assert myPixmap.height() == myExpectedHeight
        myPath = os.path.join(getTempDir(), 'renderImpactTable.png')
        myPixmap.save(myPath, 'PNG')
        myExpectedHash = 'c9164d5c2bb85c6081905456ab827f3e'
        assertHashForFile(myExpectedHash, myPath)

    def test_renderTemplate(self):
        """Test that load template works"""
        #Use the template from our resources bundle
        myInPath = ':/plugins/inasafe/basic.qpt'
        myLayer, myType = loadLayer('test_shakeimpact.shp')
        del myType

        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myMap = Map(IFACE)
        setJakartaGeoExtent()
        myMap.setImpactLayer(myLayer)
        myOutPath = os.path.join(getTempDir(), 'outTemplate.pdf')
        if os.path.exists(myOutPath):
            os.remove(myOutPath)
        myMap.renderTemplate(myInPath, myOutPath)
        assert os.path.exists(myOutPath)
        #os.remove(myPath)

    def test_mmPointConversion(self):
        """Test that conversions between pixel and page dimensions work."""
        myMap = Map(IFACE)
        myDpi = 300
        myMap.pageDpi = myDpi
        myPixels = 300
        myMM = 25.4  # 1 inch
        myResult = myMap.pointsToMM(myPixels)
        myMessage = "Expected: %s\nGot: %s" % (myMM, myResult)
        assert myResult == myMM, myMessage
        myResult = myMap.mmToPoints(myMM)
        myMessage = "Expected: %s\nGot: %s" % (myPixels, myResult)
        assert myResult == myPixels, myMessage

    def test_windowsDrawingArtifacts(self):
        """Test that windows rendering does not make artifacts"""
        # sometimes spurious lines are drawn on the layout
        myMap = Map(IFACE)
        myMap.setupComposition()
        myPdfPath = os.path.join(getTempDir(), 'outArtifactsTest.pdf')
        myMap.setupPrinter(myPdfPath)

        myPixmap = QtGui.QPixmap(10, 10)
        myPixmap.fill(QtGui.QColor(250, 250, 250))
        myFilename = os.path.join(getTempDir(), 'greyBox')
        myPixmap.save(myFilename, 'PNG')
        for i in range(10, 190, 10):
            myPicture = QgsComposerPicture(myMap.composition)
            myPicture.setPictureFile(myFilename)
            myPicture.setFrame(False)
            myPicture.setItemPosition(i,  # x
                                      i,  # y
                                      10,  # width
                                      10)  # height
            myMap.composition.addItem(myPicture)
            # Same drawing drawn directly as a pixmap
            myPixmapItem = myMap.composition.addPixmap(myPixmap)
            myPixmapItem.setOffset(i, i + 20)
            # Same drawing using our drawPixmap Helper
            myWidthMM = 1
            myMap.drawPixmap(myPixmap, myWidthMM, i, i + 40)

        myMap.renderPrintout()
        myUnwantedHash = 'd05e9223d50baf8bb147475aa96d6ba3'
        myHash = hashForFile(myPdfPath)
        # when this test no longer matches our broken render hash
        # we know the issue is fixed
        myMessage = 'Windows map render still draws with artifacts.'
        assert myHash != myUnwantedHash, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(MapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
