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
from qgis.core import (
    QgsMapLayerRegistry,
    QGis,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsFeatureRequest,
)

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
    data_store.default_vector_format = 'geojson'
    result = data_store.add_layer(layer, 'debug_layer')
    return data_store.layer_uri(result[1])


def pretty_table(iterable, header):
    """Copy/paste from http://stackoverflow.com/a/40426743/2395485"""
    max_len = [len(x) for x in header]
    for row in iterable:
        row = [row] if type(row) not in (list, tuple) else row
        for index, col in enumerate(row):
            if max_len[index] < len(str(col)):
                max_len[index] = len(str(col))
    output = '-' * (sum(max_len) + 1) + '\n'
    output += '|' + ''.join(
        [h + ' ' * (l - len(h)) + '|' for h, l in zip(header, max_len)]) + '\n'
    output += '-' * (sum(max_len) + 1) + '\n'
    for row in iterable:
        row = [row] if type(row) not in (list, tuple) else row
        output += '|' + ''.join(
            [
                str(c) + ' ' * (
                    l - len(str(c))) + '|' for c, l in zip(
                row, max_len)]) + '\n'
    output += '-' * (sum(max_len) + 1) + '\n'
    return output


def print_attribute_table(layer, limit=-1):
    """Print the attribute table in the console.

    :param layer: The layer to print.
    :type layer: QgsVectorLayer

    :param limit: The limit in the query.
    :type limit: integer
    """
    if layer.wkbType() == QGis.WKBNoGeometry:
        geometry = False
    else:
        geometry = True

    headers = []
    if geometry:
        headers.append('geom')
    headers.extend(
        [f.name() + ' : ' + str(f.type()) for f in layer.fields().toList()])

    request = QgsFeatureRequest()
    request.setLimit(limit)
    data = []
    for feature in layer.getFeatures(request):
        attributes = []
        if geometry:
            attributes.append(feature.geometry().type())
        attributes.extend(feature.attributes())
        data.append(attributes)

    print pretty_table(data, headers)
