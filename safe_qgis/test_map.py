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
from unittest import expectedFailure
import os
import logging

# Add PARENT directory to path to make test aware of other modules
#pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.append(pardir)

from PyQt4 import QtGui
from qgis.core import (QgsMapLayerRegistry,
                       QgsRectangle,
                       QgsComposerPicture)
from qgis.gui import QgsMapCanvasLayer
from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities_test import (getQgisTestApp,
                                      assertHashForFile,
                                      assertHashesForFile,
                                      hashForFile,
                                      loadLayer,
                                      setJakartaGeoExtent)
from safe_qgis.map import Map

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


class MapTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""
    def setUp(self):
        """Setup fixture run before each tests"""
        myRegistry = QgsMapLayerRegistry.instance()
        for myLayer in myRegistry.mapLayers():
            myRegistry.removeMapLayer(myLayer)

    def test_renderComposition(self):
        """Test making a pdf of the map only."""
        LOGGER.info('Testing renderComposition')
        myLayer, _ = loadLayer('test_shakeimpact.shp')
        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myMap = Map(IFACE)
        myRect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(myRect)
        CANVAS.refresh()
        myMap.setImpactLayer(myLayer)
        myPath = myMap.renderComposition()
        LOGGER.debug(myPath)
        myMessage = 'Rendered output does not exist'
        assert os.path.exists(myPath), myMessage

        # .. note:: Template writing is experimental
        myPath = unique_filename(prefix='composerTemplate',
                                 suffix='.qpt',
                                 dir=temp_dir('test'))
        myMap.writeTemplate(myPath)
        LOGGER.debug(myPath)
        myExpectedHashes = ['a7e58a5527cbe29ce056ee7b8e88cb6a',  # ub12.04-64
                            '']
        assertHashesForFile(myExpectedHashes, myPath)
        #QGISAPP.exec_()

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
        myPath = unique_filename(prefix='impactTable',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myPixmap.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        myExpectedHash = 'c9164d5c2bb85c6081905456ab827f3e'
        assertHashForFile(myExpectedHash, myPath)

    @expectedFailure
    def test_renderTemplate(self):
        """Test that load template works"""
        #Use the template from our resources bundle
        myInPath = ':/plugins/inasafe/basic.qpt'
        myLayer, _ = loadLayer('test_shakeimpact.shp')

        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myMap = Map(IFACE)
        setJakartaGeoExtent()
        myMap.setImpactLayer(myLayer)
        myPath = unique_filename(prefix='outTemplate',
                                    suffix='.pdf',
                                    dir=temp_dir('test'))
        LOGGER.debug(myPath)
        myMap.renderTemplate(myInPath, myPath)
        assert os.path.exists(myPath)
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
        myPath = unique_filename(prefix='artifactsTest',
                                    suffix='.pdf',
                                    dir=temp_dir('test'))
        myMap.setupPrinter(myPath)
        LOGGER.debug(myPath)

        myPixmap = QtGui.QPixmap(10, 10)
        myPixmap.fill(QtGui.QColor(250, 250, 250))
        myFilename = os.path.join(temp_dir(), 'greyBox')
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

        myMap.renderCompleteReport()
        myUnwantedHash = 'd05e9223d50baf8bb147475aa96d6ba3'
        myHash = hashForFile(myPath)
        # when this test no longer matches our broken render hash
        # we know the issue is fixed
        myMessage = 'Windows map render still draws with artifacts.'
        assert myHash != myUnwantedHash, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(MapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
