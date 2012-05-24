"""Helper module for gui test suite
"""

import os
import sys
from PyQt4 import QtGui, QtCore
from qgis.core import (QgsApplication,
                      QgsVectorLayer,
                      QgsRasterLayer,
                      QgsRectangle,
                      QgsCoordinateReferenceSystem)
from qgis.gui import QgsMapCanvas
from qgis_interface import QgisInterface
from storage.utilities_test import TESTDATA
from storage.utilities import read_keywords
import hashlib

QGISAPP = None  # Static vainasafele used to hold hand to running QGis app
CANVAS = None
PARENT = None
IFACE = None
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 900913  # constant for EPSG:GOOGLECRS Google Mercator id


def assertHashesForFile(theHashes, theFilename):
    """Assert that a files has matches one of a list of expected hashes"""
    myHash = hashForFile(theFilename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s' % (myHash, theHashes))
    assert myHash in theHashes, myMessage


def assertHashForFile(theHash, theFilename):
    """Assert that a files has matches its expected hash"""
    myHash = hashForFile(theFilename)
    myMessage = ('Unexpected hash'
                 '\nGot: %s'
                 '\nExpected: %s' % (myHash, theHash))
    assert myHash == theHash, myMessage


def hashForFile(theFilename):
    """Return an md5 checksum for a file"""
    myPath = theFilename
    myData = file(myPath).read()
    myHash = hashlib.md5()
    myHash.update(myData)
    myHash = myHash.hexdigest()
    return myHash


def getQgisTestApp():
    """ Start one QGis application to test agaist

    Input
        NIL

    Output
        handle to qgis app


    If QGis is already running the handle to that app will be returned
    """

    global QGISAPP

    if QGISAPP is None:
        myGuiFlag = True  # All test will run qgis in gui mode
        QGISAPP = QgsApplication(sys.argv, myGuiFlag)
        if 'QGISPATH' in os.environ:
            myPath = os.environ['QGISPATH']
            myUseDefaultPathFlag = True
            QGISAPP.setPrefixPath(myPath, myUseDefaultPathFlag)

        QGISAPP.initQgis()
        s = QGISAPP.showSettings()
        print s

    global PARENT
    if PARENT is None:
        PARENT = QtGui.QWidget()

    global CANVAS
    if CANVAS is None:
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        IFACE = QgisInterface(CANVAS)

    return QGISAPP, CANVAS, IFACE, PARENT


def loadLayer(theLayerFile):
    """Helper to load and return a single QGIS layer"""
    # Extract basename and absolute path
    myBaseName, myExt = os.path.splitext(theLayerFile)
    myPath = os.path.join(TESTDATA, theLayerFile)
    myKeywordPath = myPath[:-4] + '.keywords'
    # Determine if layer is hazard or exposure
    myKeywords = read_keywords(myKeywordPath)
    myType = 'undefined'
    if 'category' in myKeywords:
        myType = myKeywords['category']
    msg = 'Could not read %s' % myKeywordPath
    assert myKeywords is not None, msg

    # Create QGis Layer Instance
    if myExt in ['.asc', '.tif']:
        myLayer = QgsRasterLayer(myPath, myBaseName)
    elif myExt in ['.shp']:
        myLayer = QgsVectorLayer(myPath, myBaseName, 'ogr')
    else:
        myMessage = 'File %s had illegal extension' % myPath
        raise Exception(myMessage)

    myMessage = 'Layer "%s" is not valid' % str(myLayer.source())
    assert myLayer.isValid(), myMessage
    return myLayer, myType


def setCanvasCrs(theEpsgId, theOtfpFlag=False):
    """Helper to set the crs for the CANVAS before a test is run.

    Args:

        * theEpsgId  - Valid EPSG identifier (int)
        * theOtfpFlag - whether on the fly projections should be enabled
                        on the CANVAS. Default to False.
    """
        # Enable on-the-fly reprojection
    CANVAS.mapRenderer().setProjectionsEnabled(theOtfpFlag)

    # Create CRS Instance
    myCrs = QgsCoordinateReferenceSystem()
    myCrs.createFromId(theEpsgId, QgsCoordinateReferenceSystem.EpsgCrsId)

    # Reproject all layers to WGS84 geographic CRS
    CANVAS.mapRenderer().setDestinationCrs(myCrs)


def setPadangGeoExtent():
    """Zoom to an area occupied by both both Padang layers"""
    myRect = QgsRectangle(100.21, -1.05, 100.63, -0.84)
    CANVAS.setExtent(myRect)


def setJakartaGeoExtent():
    """Zoom to an area occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(106.52, -6.38, 107.14, -6.07)
    CANVAS.setExtent(myRect)


def setJakartaGoogleExtent():
    """Zoom to an area occupied by both Jakarta layers in 900913 crs
    """
    myRect = QgsRectangle(11873524, -695798, 11913804, -675295)
    CANVAS.setExtent(myRect)


def setBatemansBayGeoExtent():
    """Zoom to an area occupied by both Batemans Bay
     layers in geo crs"""
    myRect = QgsRectangle(150.152, -35.710, 150.187, -35.7013)
    CANVAS.setExtent(myRect)


def setYogyaGeoExtent():
    """Zoom to an area occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(110.348, -7.732, 110.368, -7.716)
    CANVAS.setExtent(myRect)


def setGeoExtent(theBoundingBox):
    """Zoom to an area specified given bounding box (list)"""
    myRect = QgsRectangle(*theBoundingBox)
    CANVAS.setExtent(myRect)
