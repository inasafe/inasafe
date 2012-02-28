"""Helper module for gui test suite
"""

import os
import sys
from PyQt4 import QtGui, QtCore
from qgis.core import (QgsApplication,
                      QgsVectorLayer,
                      QgsRasterLayer)
from qgis.gui import QgsMapCanvas
from qgisinterface import QgisInterface
from storage.utilities_test import TESTDATA
from storage.utilities import read_keywords
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
