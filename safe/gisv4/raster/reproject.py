# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from qgis.core import (
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsRasterFileWriter,
    QgsRasterPipe,
)

from safe.common.utilities import unique_filename, temp_dir


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
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    layer_name = 'reprojected'

    output_raster = unique_filename(suffix='.asc', dir=temp_dir())

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

    output_layer = QgsRasterLayer(output_raster, layer_name)

    # We transfer keywords to the output.
    # We don't need to update keywords as the CRS is dynamic.
    try:
        output_layer.keywords = layer.keywords
    except AttributeError:
        pass

    return output_layer