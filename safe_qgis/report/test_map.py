"""**Tests for map creation in QGIS plugin.**

"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '01/11/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest
from unittest import expectedFailure
import os
import logging

# Add PARENT directory to path to make test aware of other modules
#pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.append(pardir)

from PyQt4 import QtGui
from qgis.core import (
    QgsMapLayerRegistry,
    QgsRectangle,
    QgsComposerPicture)
from qgis.gui import QgsMapCanvasLayer
from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities.utilities_test import (
    getQgisTestApp,
    loadLayer,
    setJakartaGeoExtent,
    checkImages)
from safe_qgis.utilities.utilities import (
    setupPrinter, dpiToMeters, qgisVersion)
from safe_qgis.report.map import Map

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


class MapTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""

    def setUp(self):
        """Setup fixture run before each tests"""
        # noinspection PyArgumentList
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
        myExpectedSizes = [
            441541,  # as rendered on ub 13.04 post 17 May 2013
            447217,  # Nadia Linux Mint 14
            447051,  # as rendered on Jenkins post 24 April 2013
            447138,  # Windows 7 SP1 AMD64
            233989,  # OSX 10.8
        ]
        myMessage = '%s\nExpected rendered map pdf to be in %s, got %s' % (
            myPath, myExpectedSizes, mySize)
        self.assertIn(mySize, myExpectedSizes, myMessage)

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
        myImagePath, myControlImage, myTargetArea = myMap.renderComposition()
        LOGGER.debug(myImagePath)

        assert myControlImage is not None

        myDimensions = [myTargetArea.left(),
                        myTargetArea.top(),
                        myTargetArea.bottom(),
                        myTargetArea.right()]
        myExpectedDimensions = [0.0, 0.0, 3507.0, 2480.0]
        myMessage = 'Expected target area to be %s, got %s' % (
            str(myExpectedDimensions), str(myDimensions))
        assert myExpectedDimensions == myDimensions, myMessage

        myMessage = 'Rendered output does not exist'
        assert os.path.exists(myImagePath), myMessage

        # Beta version and version changes  can introduce a few extra chars
        # into the metadata section so we set a reasonable tolerance to cope
        # with this.
        myTolerance = 8000
        myFlag, myMessage = checkImages(
            'renderComposition',
            myImagePath,
            myTolerance)
        assert myFlag, myMessage

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
        myPath = unique_filename(
            prefix='outTemplate',
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
        myPath = unique_filename(
            prefix='artifacts',
            suffix='.pdf',
            dir=temp_dir('test'))
        myMap = Map(IFACE)
        setupPrinter(myPath)
        myMap.setupComposition()

        myImage = QtGui.QImage(10, 10, QtGui.QImage.Format_RGB32)
        myImage.setDotsPerMeterX(dpiToMeters(300))
        myImage.setDotsPerMeterY(dpiToMeters(300))
        #myImage.fill(QtGui.QColor(250, 250, 250))
        # Look at the output, you will see antialiasing issues around some
        # of the boxes drawn...
        # myImage.fill(QtGui.QColor(200, 200, 200))
        myImage.fill(200 + 200 * 256 + 200 * 256 * 256)
        myFilename = os.path.join(temp_dir(), 'greyBox')
        myImage.save(myFilename, 'PNG')
        for i in range(10, 190, 10):
            myPicture = QgsComposerPicture(myMap.composition)
            myPicture.setPictureFile(myFilename)
            if qgisVersion() >= 10800:  # 1.8 or newer
                myPicture.setFrameEnabled(False)
            else:
                myPicture.setFrame(False)
            myPicture.setItemPosition(i,  # x
                                      i,  # y
                                      10,  # width
                                      10)  # height
            myMap.composition.addItem(myPicture)
            # Same drawing drawn directly as a pixmap
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            myPixmapItem = myMap.composition.addPixmap(
                QtGui.QPixmap.fromImage(myImage))
            myPixmapItem.setOffset(i, i + 20)
            # Same drawing using our drawImage Helper
            myWidthMM = 1
            myMap.drawImage(myImage, myWidthMM, i, i + 40)

        myImagePath, _, _ = myMap.renderComposition()
        # when this test no longer matches our broken render hash
        # we know the issue is fixed

        myTolerance = 0
        myFlag, myMessage = checkImages(
            'windowsArtifacts',
            myImagePath,
            myTolerance)
        myMessage += ('\nWe want these images to match, if they do not '
                      'there may be rendering artifacts in windows.\n')
        assert myFlag, myMessage


if __name__ == '__main__':
    suite = unittest.makeSuite(MapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
