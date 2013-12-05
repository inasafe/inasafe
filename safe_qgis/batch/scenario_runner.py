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

from safe_qgis.exceptions import FileNotFoundError

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
    filename = os.path.split(thePath)[-1]  # In case path was absolute
    myBaseName, _ = os.path.splitext(filename)
    theLongPath = os.path.join(theScenarioFilePath, thePath)
    path = os.path.normpath(theLongPath)
    return path, myBaseName


def addLayers(scenario_dir, paths):
    """Add the layers described in a scenario file to QGIS.

    :param scenario_dir: Base directory to find path.
    :type scenario_dir: str

    :param paths: Path of scenario file (or a list of paths).
    :type paths: str, list

    :raises: Exception, TypeError, FileNotFoundError

    Note:
        * Exception - occurs when paths have illegal extension
        * TypeError - occurs when paths is not string or list
        * FileNotFoundError - occurs when file not found
    """

    paths = []
    if isinstance(paths, str):
        paths.append(extractPath(scenario_dir, paths))
    elif isinstance(paths, list):
        paths = [extractPath(scenario_dir, path) for path in paths]
    else:
        message = "Paths must be string or list not %s" % type(paths)
        raise TypeError(message)

    for path, myBaseName in paths:
        myExt = os.path.splitext(path)[-1]

        if not os.path.exists(path):
            raise FileNotFoundError('File not found: %s' % path)

        if myExt in ['.asc', '.tif']:
            LOGGER.debug("add raster layer %s" % path)
            layer = QgsRasterLayer(path, myBaseName)
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        elif myExt in ['.shp']:
            LOGGER.debug("add vector layer %s" % path)
            layer = QgsVectorLayer(path, myBaseName, 'ogr')
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        else:
            raise Exception('File %s had illegal extension' % path)


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
        myFunctionId = theDock.get_function_id(myCount)
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
        layerId = theDock.cboAggregation.itemData(
            myCount, QtCore.Qt.UserRole)
        # noinspection PyArgumentList
        layer = QgsMapLayerRegistry.instance().mapLayer(layerId)

        if layer is None:
            continue

        if layer.source() == theAggregationLayer:
            theDock.cboAggregation.setCurrentIndex(myCount)
            return True
    return False
