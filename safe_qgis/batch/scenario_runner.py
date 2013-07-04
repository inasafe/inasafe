# coding=utf-8
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

from qgis.core import QgsMapLayerRegistry, QgsRasterLayer, QgsVectorLayer
from qgis.utils import iface

from safe_qgis.exceptions import QgisPathError
from safe_qgis.utilities.utilities import getAbsolutePath

LOGGER = logging.getLogger('InaSAFE')
STATUS_FLAG = False


def getMapCanvas():
    """Return map canvas object
    """
    return iface.mapCanvas()


def runScenario(theDock=None):
    """Simulate pressing run button in InaSAFE dock widget.

    :param theDock: Dock instance
    """
    # pylint: disable=W0603
    global STATUS_FLAG
    STATUS_FLAG = False

    def completed(theFlag):
        """Listen for completion and set myFlag according to exit value.
        :param theFlag:
        """
        global STATUS_FLAG
        STATUS_FLAG = theFlag
        LOGGER.debug("scenario done")
        theDock.analysisDone.disconnect(completed)

    theDock.analysisDone.connect(completed)
    # Start the analysis
    theDock.accept()
    return STATUS_FLAG
    # pylint: enable=W0603


def extractPath(theScenarioFilePath, thePath):
    """Get a path and basename given a scenarioFilePath and path.
    :param theScenarioFilePath:
    :param thePath:
    """
    myFilename = os.path.split(thePath)[-1]  # In case path was absolute
    myBaseName, _ = os.path.splitext(myFilename)
    myPath = getAbsolutePath(theScenarioFilePath, thePath)
    return myPath, myBaseName


def addLayers(theScenarioFilePath, thePaths):
    """ Add vector or raster layer to current project
    :param theScenarioFilePath: str - (Required) base directory to find path.
    :param thePaths: str or list - (Required) path of layer file.

    Raises:
        * Exception - occurs when thePaths have illegal extension
        * TypeError - occurs when thePaths is not string or list
        * QgisPathError - occurs when file not found
    """

    myPaths = []
    if isinstance(thePaths, str):
        myPaths.append(extractPath(theScenarioFilePath, thePaths))
    elif isinstance(thePaths, list):
        myPaths = [extractPath(theScenarioFilePath, path) for path in thePaths]
    else:
        myMessage = "thePaths must be string or list not %s" % type(thePaths)
        raise TypeError(myMessage)

    for myPath, myBaseName in myPaths:
        myExt = os.path.splitext(myPath)[-1]

        if not os.path.exists(myPath):
            raise QgisPathError('File not found: %s' % myPath)

        if myExt in ['.asc', '.tif']:
            LOGGER.debug("add raster layer %s" % myPath)
            myLayer = QgsRasterLayer(myPath, myBaseName)
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayer(myLayer)
        elif myExt in ['.shp']:
            LOGGER.debug("add vector layer %s" % myPath)
            myLayer = QgsVectorLayer(myPath, myBaseName, 'ogr')
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayer(myLayer)
        else:
            raise Exception('File %s had illegal extension' % myPath)


def setFunctionId(theFunctionId, theDock=None):
    """Set the function combo to use the function with the given id.

    :param theFunctionId: str - a string representing the unique identifier for
            the desired function.
    :param theDock: a dock instance

    :returns bool: True on success, False in the case that the function is not
            present in the function selector (based on the context of loaded
            hazard and exposure layers.
    """
    if theFunctionId is None or theFunctionId == '':
        return False

    for myCount in range(0, theDock.cboFunction.count()):
        myFunctionId = theDock.getFunctionID(myCount)
        if myFunctionId == theFunctionId:
            theDock.cboFunction.setCurrentIndex(myCount)
            return True
    return False


def setAggregationLayer(theAggregationLayer, theDock=None):
    """Set the aggregation combo to use the layer with the given name.

    :param theAggregationLayer: str - a string representing the source name of
        the desired aggregation layer.
    :param theDock: a dock instance

    :returns bool: True on success, False in the case that the aggregation
        layer is not in the aggregation selector.

    .. note:: Probably won't work for sublayers and anything else other than
        file based layers (e.g. shp).

    """
    if theAggregationLayer is None or theAggregationLayer == '':
        return False

    for myCount in range(0, theDock.cboAggregation.count()):
        myLayerId = theDock.cboAggregation.itemData(
            myCount, QtCore.Qt.UserRole).toString()
        # noinspection PyArgumentList
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)

        if myLayer is None:
            continue

        if myLayer.source() == theAggregationLayer:
            theDock.cboAggregation.setCurrentIndex(myCount)
            return True
    return False
