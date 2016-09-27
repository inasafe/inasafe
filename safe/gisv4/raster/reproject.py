# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import logging

from PyQt4.QtCore import QProcess

from qgis.core import (
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsRasterFileWriter,
    QgsRasterPipe,
)

from safe.common.utilities import which
from safe.common.exceptions import KeywordNotFoundError, CallGDALError
from safe.common.utilities import unique_filename, temp_dir
from safe.utilities.i18n import tr

LOGGER = logging.getLogger(name='InaSAFE')


def reproject(layer, output_crs, callback=None):
    """
    Reproject a raster layer to a specific CRS.

    The callback for raster is not used.

    Issue https://github.com/inasafe/inasafe/issues/3183

    :param layer: The layer to reproject.
    :type layer: QgsRasterLayer

    :param output_crs: The destination CRS.
    :type output_crs: QgsCoordinateReferenceSystem

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """

    # ET 26/09/16
    # I have a problem reprojecting with PyQGIS. I'm using GDAL command line.

    # Fixme : Manage callback in these functions.
    return _reproject_gdal(layer, output_crs, callback)


def _reproject_gdal(layer, output_crs, callback=None):
    """Reproject a raster layer using GDAL command line.

    You mustn't call this function. Use "reproject" instead.

    :param layer: The layer to reproject.
    :type layer: QgsRasterLayer

    :param output_crs: The destination CRS.
    :type output_crs: QgsCoordinateReferenceSystem

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    output_layer_name = 'reprojected'
    processing_step = tr('Reprojecting')

    output_raster = unique_filename(suffix='.tiff', dir=temp_dir())

    binary_list = which('gdalwarp')
    LOGGER.debug('Path for gdalwarp: %s' % binary_list)
    if len(binary_list) < 1:
        raise CallGDALError(
            tr('gdalwarp could not be found on your computer'))
    # Use the first matching gdalwarp found
    binary = binary_list[0]
    command = (
        '"%s" '
        '-s_srs %s '
        '-t_srs %s '
        '-of GTiff '
        '"%s" '
        '"%s"' % (
            binary,
            layer.crs().authid(),
            output_crs.authid(),
            layer.source(),
            output_raster))

    LOGGER.debug(command)
    result = QProcess().execute(command)

    # For QProcess exit codes see
    # http://qt-project.org/doc/qt-4.8/qprocess.html#execute
    if result == -2:  # cannot be started
        message_detail = tr('Process could not be started.')
        message = tr(
            '<p>Error while executing the following shell command:'
            '</p><pre>%s</pre><p>Error message: %s'
            % (command, message_detail))
        raise CallGDALError(message)
    elif result == -1:  # process crashed
        message_detail = tr('Process crashed.')
        message = tr(
            '<p>Error while executing the following shell command:</p>'
            '<pre>%s</pre><p>Error message: %s' % (command, message_detail))
        raise CallGDALError(message)

    reprojected = QgsRasterLayer(output_raster, output_layer_name)

    # We transfer keywords to the output.
    # We don't need to update keywords as the CRS is dynamic.
    try:
        reprojected.keywords = layer.keywords
    except AttributeError:
        raise KeywordNotFoundError

    return reprojected


def _reproject_pyqgis(layer, output_crs, callback=None):
    """Reproject a raster layer using PyQGIS.
    Not working properly for now. Need more tests.

    You mustn't call this function. Use "reproject" instead.

    :param layer: The layer to reproject.
    :type layer: QgsRasterLayer

    :param output_crs: The destination CRS.
    :type output_crs: QgsCoordinateReferenceSystem

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    output_layer_name = 'reprojected'
    processing_step = tr('Reprojecting')

    output_raster = unique_filename(suffix='.tiff', dir=temp_dir())

    transform = QgsCoordinateTransform(layer.crs(), output_crs)
    transformed_extent = transform.transformBoundingBox(layer.extent())

    renderer = layer.renderer()
    provider = layer.dataProvider()

    pipe = QgsRasterPipe()
    pipe.set(provider.clone())
    pipe.set(renderer.clone())

    file_writer = QgsRasterFileWriter(output_raster)
    file_writer.Mode(1)
    file_writer.writeRaster(
        pipe,
        provider.xSize(),
        provider.ySize(),
        transformed_extent,
        output_crs)

    output_layer = QgsRasterLayer(output_raster, output_layer_name)

    # We transfer keywords to the output.
    # We don't need to update keywords as the CRS is dynamic.
    try:
        output_layer.keywords = layer.keywords
    except AttributeError:
        raise KeywordNotFoundError

    return output_layer
