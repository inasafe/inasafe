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

from qgis.PyQt.QtCore import QVariant, Qt
from qgis.core import (
    QgsProject,
    QgsWkbTypes,
    QgsFeature,
    QgsField,
    QgsFeatureRequest,
    QgsCoordinateReferenceSystem,
)

from safe.datastore.folder import Folder
from safe.gis.vector.tools import create_memory_layer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

"""
BE CAREFUL :
These functions shouldn't be use in production.
You can call them only to debug your code.
"""


def show_qgis_geometry(geometry, crs=None):
    """Show a QGIS geometry.

    :param geometry: The geometry to display.
    :type geometry: QgsGeometry

    :param crs: The CRS of the geometry. 4326 by default.
    :type crs: QgsCoordinateReferenceSystem
    """
    feature = QgsFeature()
    feature.setGeometry(geometry)
    if crs is None:
        crs = QgsCoordinateReferenceSystem(4326)
    show_qgis_feature(feature, crs)


def show_qgis_feature(feature, crs=None):
    """Show a QGIS feature.

    :param feature: The feature to display.
    :type feature: QgsFeature

    :param crs: The CRS of the geometry. 4326 by default.
    :type crs: QgsCoordinateReferenceSystem
    """
    if crs is None:
        crs = QgsCoordinateReferenceSystem(4326)
    layer = create_memory_layer('Debug', feature.geometry().type(), crs)
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
    QgsProject.instance().addMapLayer(layer)


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
    if layer.wkbType() in [QgsWkbTypes.NullGeometry, QgsWkbTypes.UnknownGeometry]:
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

    # fix_print_with_import
    print((pretty_table(data, headers)))


def print_combobox(combo, role=Qt.UserRole):
    """Helper to print a combobox with the current item.

    :param combo: The combobox.
    :type combo: QCombobox

    :param role: A Role to display. Default to Qt.UserRole.
        You can give a list of role.
    :type role: int, list
    """
    headers = ['Text', 'Selected']
    if isinstance(role, list):
        headers.extend(['Role %s' % i for i in role])
    else:
        headers.append('Role %s' % role)
        role = [role]
    data = []
    for i in range(0, combo.count()):
        selected = 'YES' if i == combo.currentIndex() else ''
        attributes = [combo.itemText(i), selected]
        attributes.extend([str(combo.itemData(i, j)) for j in role])
        data.append(attributes)
    # fix_print_with_import
    print((pretty_table(data, headers)))
