"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **Helper module for gui script functions.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'bungcip@gmail.com'
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import PyQt4.QtCore as QtCore

from qgis.core import QgsMapLayerRegistry
from qgis.utils import iface

from safe_qgis.exceptions import QgisPathError
from safe_qgis.dock import Dock
from safe_qgis.utilities import getAbsolutePath

LOGGER = logging.getLogger('InaSAFE')


def getDock():
    """ Get InaSAFE Dock widget instance.
    Returns: Dock - instance of InaSAFE Dock in QGIS main window.
    """
    return iface.mainWindow().findChild(Dock)


def runScenario():
    """Simulate pressing run button in InaSAFE dock widget.

    Returns:
        None
    """

    myDock = getDock()
    myDock.pbnRunStop.click()


def extractPath(theScenarioFilePath, thePath):
    """Get a path and basename given a scenarioFilePath and path."""
    myFilename = os.path.split(thePath)[-1]  # In case path was absolute
    myBaseName, myExt = os.path.splitext(myFilename)
    myPath = getAbsolutePath(theScenarioFilePath, thePath)
    return myPath, myBaseName


def addLayers(theScenarioFilePath, thePaths):
    """ Add vector or raster layer to current project
     Args:
        * theDirectory: str - (Required) base directory to find path.
        * thePaths: str or list - (Required) path of layer file.

    Returns:
        None.

    Raises:
        * Exception - occurs when thePaths have illegal extension
        * TypeError - occurs when thePaths is not string or list
        * QgisPathError - occurs when file not found
    """

    myPaths = []
    if isinstance(thePaths, str):
        myPaths.append(extractPath(theScenarioFilePath, thePaths))
    elif isinstance(thePaths, list):
        myPaths = [extractPath(theScenarioFilePath, x) for x in thePaths]
    else:
        myMessage = "thePaths must be string or list not %s" % type(thePaths)
        raise TypeError(myMessage)

    for myPath, myBaseName in myPaths:
        myExt = os.path.splitext(myPath)[-1]

        if not os.path.exists(myPath):
            raise QgisPathError('File not found: %s' % myPath)

        if myExt in ['.asc', '.tif']:
            LOGGER.debug("add raster layer %s" % myPath)
            iface.addRasterLayer(myPath, myBaseName)
        elif myExt in ['.shp']:
            LOGGER.debug("add vector layer %s" % myPath)
            iface.addVectorLayer(myPath, myBaseName, 'ogr')
        else:
            raise Exception('File %s had illegal extension' % myPath)


def setFunctionId(theFunctionId):
    """Set the function combo to use the function with the given id.

    Args:
        theFunctionId: str - a string representing the unique identifier for
            the desired function.

    Returns:
        bool: True on success, False in the case that the function is not
            present in the function selector (based on the context of loaded
            hazard and exposure layers.

    Exception:
        None
    """
    if theFunctionId is None or theFunctionId == '':
        return False

    myDock = getDock()
    for myCount in range(0, myDock.cboFunction.count()):
        myFunctionId = myDock.getFunctionID(myCount)
        if myFunctionId == theFunctionId:
            myDock.cboFunction.setCurrentIndex(myCount)
            return True
    return False


def setAggregation(theAggregationLayer):
    """Set the aggregation combo to use the layer with the given name.

    Args:
        theAggregationLayer: str - a string representing the source name of
        the desired aggregation layer.

    Returns:
        bool: True on success, False in the case that the aggregation layer
        is not in the aggregation selector.

    Exception:
        None

    .. note:: Probably wont work for sublayers and anything else other than
        file based layers (e.g. shp).

    """
    if theAggregationLayer is None or theAggregationLayer == '':
        return False

    myDock = getDock()

    for myCount in range(0, myDock.cboAggregation.count()):
        myLayerId = myDock.cboAggregation.itemData(
            myCount, QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)

        if myLayer.source() == theAggregationLayer:
            myDock.cboAggregation.setCurrentIndex(myCount)
            return True
    return False
