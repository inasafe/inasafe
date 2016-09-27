# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from uuid import uuid4
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QGis

from safe.common.exceptions import MemoryLayerCreationError


def create_memory_layer(layer_name, geometry, coordinate_reference_system):
    """Create a vector memory layer.

    :param layer_name: The name of the layer.
    :type layer_name: str

    :param geometry: The geometry of the layer.
    :rtype geometry: QGis.WkbType

    :param coordinate_reference_system: The CRS of the memory layer.
    :type coordinate_reference_system: QgsCoordinateReferenceSystem

    :return: The memory layer.
    :rtype: QgsVectorLayer
    """

    if geometry == QGis.Point:
        type_string = 'Point'
    elif geometry == QGis.Line:
        type_string = 'Line'
    elif geometry == QGis.Polygon:
        type_string = 'Polygon'
    else:
        raise MemoryLayerCreationError(
            'Layer is whether Point nor Line nor Polygon')

    crs = coordinate_reference_system.authid().lower()
    uri = '%s?crs=%s&index=yes&uuid=%s' % (type_string, crs, str(uuid4()))
    memory_layer = QgsVectorLayer(uri, layer_name, 'memory')
    memory_layer.keywords = {}
    return memory_layer
