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
global_status_flag = False


def get_map_canvas():
    """Return map canvas object
    """
    return iface.mapCanvas()


def run_scenario(dock=None):
    """Run the current scenario.

    :param dock: Dock instance
    """
    # pylint: disable=W0603
    global global_status_flag
    global_status_flag = False

    def completed(flag):
        """Listen for completion and set myFlag according to exit value.
        :param flag:
        """
        global global_status_flag
        global_status_flag = flag
        LOGGER.debug("scenario done")
        dock.analysisDone.disconnect(completed)

    dock.analysisDone.connect(completed)
    # Start the analysis
    dock.accept()
    return global_status_flag
    # pylint: enable=W0603


def extract_path(scenario_file_path, path):
    """Get a path and basename given a scenarioFilePath and path.

    :param scenario_file_path: Path to a scenario file.
    :type scenario_file_path: str

    :param path:
    :type path: str

    :returns: Tuple containing path and base name
    :rtype: (str, str)
    """
    filename = os.path.split(path)[-1]  # In case path was absolute
    base_name, _ = os.path.splitext(filename)
    full_path = os.path.join(scenario_file_path, path)
    path = os.path.normpath(full_path)
    return path, base_name


def add_layers(scenario_dir, paths):
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

    path_list = []
    if isinstance(paths, str):
        path_list.append(extract_path(scenario_dir, paths))
    elif isinstance(paths, list):
        path_list = [extract_path(scenario_dir, path) for path in paths]
    else:
        message = "Paths must be string or list not %s" % type(paths)
        raise TypeError(message)

    for path, base_name in path_list:
        extension = os.path.splitext(path)[-1]

        if not os.path.exists(path):
            raise FileNotFoundError('File not found: %s' % path)

        if extension in ['.asc', '.tif']:
            LOGGER.debug("add raster layer %s" % path)
            layer = QgsRasterLayer(path, base_name)
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayers([layer])
        elif extension in ['.shp']:
            LOGGER.debug("add vector layer %s" % path)
            layer = QgsVectorLayer(path, base_name, 'ogr')
            # noinspection PyArgumentList
            QgsMapLayerRegistry.instance().addMapLayers([layer])
        else:
            raise Exception('File %s had illegal extension' % path)


def set_function_id(function_id, dock=None):
    """Set the function combo to use the function with the given id.

    :param function_id: str - a string representing the unique identifier for
            the desired function.
    :param dock: a dock instance

    :returns bool: True on success, False in the case that the function is not
            present in the function selector (based on the context of loaded
            hazard and exposure layers.
    """
    if function_id is None or function_id == '':
        return False

    for count in range(0, dock.cboFunction.count()):
        current_id = dock.get_function_id(count)
        if current_id == function_id:
            dock.cboFunction.setCurrentIndex(count)
            return True
    return False


def set_aggregation_layer(aggregation_layer, dock=None):
    """Set the aggregation combo to use the layer with the given name.

    :param aggregation_layer: str - a string representing the source name of
        the desired aggregation layer.
    :param dock: a dock instance

    :returns bool: True on success, False in the case that the aggregation
        layer is not in the aggregation selector.

    .. note:: Probably won't work for sublayers and anything else other than
        file based layers (e.g. shp).

    """
    if aggregation_layer is None or aggregation_layer == '':
        return False

    for count in range(0, dock.cboAggregation.count()):
        layer_id = dock.cboAggregation.itemData(
            count, QtCore.Qt.UserRole)
        # noinspection PyArgumentList
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)

        if layer is None:
            continue

        if layer.source() == aggregation_layer:
            dock.cboAggregation.setCurrentIndex(count)
            return True
    return False
