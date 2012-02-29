"""Helper module for gui test suite
"""

import os
import sys
from PyQt4 import QtGui, QtCore
from qgis.core import (QgsApplication,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem)
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
QGISAPP = None  # Static variable used to hold hand to running QGis app
CANVAS = None
PARENT = None
IFACE = None


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
    """Zoom to an area known to be occupied by both both Padang layers"""
    myRect = QgsRectangle(100.21, -1.05, 100.63, -0.84)
    CANVAS.setExtent(myRect)


def setJakartaGeoExtent():
    """Zoom to an area know to be occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(106.52, -6.38, 107.14, -6.07)
    CANVAS.setExtent(myRect)


def setJakartaGoogleExtent():
    """Zoom to an area know to be occupied by both Jakarta layers in 900913 crs
    """
    myRect = QgsRectangle(11873524, -695798, 11913804, -675295)
    CANVAS.setExtent(myRect)


def setBatemansBayGeoExtent():
    """Zoom to an area know to be occupied by both Batemans Bay
     layers in geo crs"""
    myRect = QgsRectangle(150.162, -35.741, 150.207, -35.719)
    CANVAS.setExtent(myRect)


def setYogyaGeoExtent():
    """Zoom to an area know to be occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(110.348, -7.732, 110.368, -7.716)
    CANVAS.setExtent(myRect)


def setGeoExtent(theBoundingBox):
    """Zoom to an area specified given bounding box (list)"""
    myRect = QgsRectangle(*theBoundingBox)
    CANVAS.setExtent(myRect)
