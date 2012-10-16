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
__version__ = '0.6.0'
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
                                      assertHashesForFile,
                                      hashForFile,
                                      loadLayer,
                                      setJakartaGeoExtent)
from safe_qgis.utilities import setupPrinter
from safe_qgis.map import Map

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


class MapTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""
    def setUp(self):
        """Setup fixture run before each tests"""
        myRegistry = QgsMapLayerRegistry.instance()
        myRegistry.removeAllMapLayers()

    def test_printToPdf(self):
        """Test making a pdf of the map - this is the most typical use of map.
        """
        LOGGER.info('Testing printToPdf')
        myLayer, _ = loadLayer('test_shakeimpact.shp')
        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])
        myRect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(myRect)
        CANVAS.refresh()
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.composeMap()
        myPath = unique_filename(prefix='mapPdfTest',
                                 suffix='.pdf',
                                 dir=temp_dir('test'))
        myMap.printToPdf(myPath)
        LOGGER.debug(myPath)
        myMessage = 'Rendered output does not exist: %s' % myPath
        assert os.path.exists(myPath), myMessage
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        mySize = os.stat(myPath).st_size
        myExpectedSize = 352798  # as rendered on linux ub 12.04 64
        myMessage = 'Expected rendered map pdf to be at least %s, got %s' % (
            myExpectedSize, mySize
        )
        assert mySize >= myExpectedSize, myMessage

    def test_renderComposition(self):
        """Test making an image of the map only."""
        LOGGER.info('Testing renderComposition')
        myLayer, _ = loadLayer('test_shakeimpact.shp')
        myCanvasLayer = QgsMapCanvasLayer(myLayer)
        CANVAS.setLayerSet([myCanvasLayer])

        myRect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(myRect)
        CANVAS.refresh()
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myMap.composeMap()
        myImagePath, myImage, myTargetArea = myMap.renderComposition()
        LOGGER.debug(myImagePath)

        assert myImage is not None

        myDimensions = [myTargetArea.left(),
                        myTargetArea.top(),
                        myTargetArea.bottom(),
                        myTargetArea.right()]
        myExpectedDimensions = [0.0, 0.0, 3507.0, 2480.0]
        myMessage = 'Expected target area to be %s, got %s' % (
            str(myExpectedDimensions), str(myDimensions)
        )
        assert myExpectedDimensions == myDimensions, myMessage

        myMessage = 'Rendered output does not exist'
        assert os.path.exists(myImagePath), myMessage
        # Note these hashes will be affected every time get_version
        # changes due to the version being embeded in the pdf
        myExpectedHashes = [
                            '0109d8bac8fd27677d373ebf66546d19',
                            '9a4ac96de64bbe1dda2616d01158913d',  # ub12.04-64
                            'ddf3cd2e9059e85c9d5b525d9f00c7dd',  # Jenkins
                            '7d308ea9d88ef55a101766adaabf179f',  # ub11.10-64
                            '']
        assertHashesForFile(myExpectedHashes, myImagePath)

    def test_getMapTitle(self):
        """Getting the map title from the keywords"""
        myLayer, _ = loadLayer('test_floodimpact.tif')
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
        myLayer, _ = loadLayer('population_padang_1.asc')
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myTitle = myMap.getMapTitle()
        myExpectedTitle = None
        myMessage = 'Expected: %s\nGot:\n %s' % (myExpectedTitle, myTitle)
        assert myTitle == myExpectedTitle, myMessage

    @expectedFailure
    def Xtest_renderTemplate(self):
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

    def test_windowsDrawingArtifacts(self):
        """Test that windows rendering does not make artifacts"""
        # sometimes spurious lines are drawn on the layout
        LOGGER.info('Testing windowsDrawingArtifacts')
        myPath = unique_filename(prefix='artifacts',
                                 suffix='.pdf',
                                 dir=temp_dir('test'))
        myMap = Map(IFACE)
        setupPrinter(myPath)
        myMap.setupComposition()

        myPixmap = QtGui.QPixmap(10, 10)
        #myPixmap.fill(QtGui.QColor(250, 250, 250))
        # Look at the output, you will see antialiasing issues around some
        # of the boxes drawn...
        myPixmap.fill(QtGui.QColor(200, 200, 200))
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

        myImagePath, _, _ = myMap.renderComposition()
        LOGGER.debug('Artifacts image path: %s' % myImagePath)
        LOGGER.debug('Artifacts pdf path: %s' % myPath)
        myUnwantedHash = 'd05e9223d50baf8bb147475aa96d6ba3'
        myHash = hashForFile(myImagePath)
        # when this test no longer matches our broken render hash
        # we know the issue is fixed
        myMessage = 'Windows map render still draws with artifacts.'
        assert myHash != myUnwantedHash, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(MapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
