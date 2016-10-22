# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Debug helper class.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from tempfile import mkdtemp
from PyQt4.QtCore import QVariant
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsFeature, QgsField

from safe.datastore.folder import Folder

__author__ = 'etienne@kartoza.com'
__date__ = '20/04/2016'
__copyright__ = (
    'Copyright 2016, Australia Indonesia Facility for Disaster Reduction')

"""
BE CAREFUL :
These functions shouldn't be use in production.
You can call them only to debug your code.
"""


def show_qgis_geometry(geometry):
    """Show a QGIS geometry.

    :param geometry: The geometry to display.
    :type geometry: QgsGeometry
    """
    feature = QgsFeature()
    feature.setGeometry(geometry)
    show_qgis_feature(feature)


def show_qgis_feature(feature):
    """Show a QGIS feature.

    :param feature: The feature to display.
    :type feature: QgsFeature
    """

    geometries = ['Point', 'Line', 'Polygon']
    geometry = geometries[feature.geometry().type()]

    layer = QgsVectorLayer(geometry, 'Debug', 'memory')
    data_provider = layer.dataProvider()

    for i, attr in enumerate(feature.attributes()):
        data_provider.addAttributes(
            [QgsField('attribute %s' % i, QVariant.String)])

    layer.updateFields()

    data_provider.addFeatures([feature])
    layer.updateExtents()
    show_qgis_layer(layer)


def show_qgis_layer(layer):
    """Show a QGIS layer in the map canvas.

    :param layer: The layer to show.
    :type layer: QgsMapLayer
    """
    QgsMapLayerRegistry.instance().addMapLayer(layer)


def save_layer_to_file(layer):
    """Save a QGIS layer to disk.

    :param layer: The layer to save.
    :type layer: QgsMapLayer

    :return: The path to the file.
    :rtype: str
    """
    path = mkdtemp()
    data_store = Folder(path)
    result = data_store.add_layer(layer, 'debug_layer')
    return data_store.layer_uri(result[1])
