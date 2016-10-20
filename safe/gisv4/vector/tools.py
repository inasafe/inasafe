# coding=utf-8

"""
Tools for vector layers.
"""

from uuid import uuid4
from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QGis,
    QgsFeature,
    QgsField,
    QgsWKBTypes
)

from safe.common.exceptions import MemoryLayerCreationError
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


wkb_type_groups = {
    'Point': (
        QgsWKBTypes.Point,
        QgsWKBTypes.MultiPoint,
        QgsWKBTypes.Point25D,
        QgsWKBTypes.MultiPoint25D,),
    'LineString': (
        QgsWKBTypes.LineString,
        QgsWKBTypes.MultiLineString,
        QgsWKBTypes.LineString25D,
        QgsWKBTypes.MultiLineString25D,),
    'Polygon': (
        QgsWKBTypes.Polygon,
        QgsWKBTypes.MultiPolygon,
        QgsWKBTypes.Polygon25D,
        QgsWKBTypes.MultiPolygon25D,),
}
for key, value in list(wkb_type_groups.items()):
    for const in value:
        wkb_type_groups[const] = key


@profile
def create_memory_layer(
        layer_name, geometry, coordinate_reference_system, fields=None):
    """Create a vector memory layer.

    :param layer_name: The name of the layer.
    :type layer_name: str

    :param geometry: The geometry of the layer.
    :rtype geometry: QGis.WkbType

    :param coordinate_reference_system: The CRS of the memory layer.
    :type coordinate_reference_system: QgsCoordinateReferenceSystem

    :param fields: Fields of the vector layer. Default to None.
    :type fields: QgsFields

    :return: The memory layer.
    :rtype: QgsVectorLayer
    """

    if geometry == QGis.Point:
        type_string = 'MultiPoint'
    elif geometry == QGis.Line:
        type_string = 'MultiLineString'
    elif geometry == QGis.Polygon:
        type_string = 'MultiPolygon'
    else:
        raise MemoryLayerCreationError(
            'Layer is whether Point nor Line nor Polygon, I got %s' % geometry)

    crs = coordinate_reference_system.authid().lower()
    uri = '%s?crs=%s&index=yes&uuid=%s' % (type_string, crs, str(uuid4()))
    memory_layer = QgsVectorLayer(uri, layer_name, 'memory')
    memory_layer.keywords = {}

    if fields:
        data_provider = memory_layer.dataProvider()
        data_provider.addAttributes(fields)
        memory_layer.updateFields()

    return memory_layer


@profile
def copy_layer(source, target):
    """Copy a vector layer to another one.

    :param source: The vector layer to copy.
    :type source: QgsVectorLayer

    :param target: The destination.
    :type source: QgsVectorLayer
    """
    out_feature = QgsFeature()
    target.startEditing()

    for i, feature in enumerate(source.getFeatures()):
        geom = feature.geometry()
        out_feature.setGeometry(geom)
        out_feature.setAttributes(feature.attributes())
        target.addFeature(out_feature)

    target.commitChanges()


@profile
def copy_fields(layer, fields_to_copy):
    """Copy fields inside an attribute table.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param fields_to_copy: Dictionary of fields to copy.
    :type fields_to_copy: dict
    """
    for field in fields_to_copy:

        index = layer.fieldNameIndex(field)
        if index != -1:

            layer.startEditing()

            source_field = layer.fields().at(index)
            new_field = QgsField(source_field)
            new_field.setName(fields_to_copy[field])

            layer.addAttribute(new_field)

            new_index = layer.fieldNameIndex(fields_to_copy[field])

            for feature in layer.getFeatures():
                attributes = feature.attributes()
                source_value = attributes[index]
                layer.changeAttributeValue(
                    feature.id(), new_index, source_value)

            layer.commitChanges()
            layer.updateFields()


@profile
def remove_fields(layer, fields_to_remove):
    """Remove fields from a vector layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param fields_to_remove: List of fields to remove.
    :type fields_to_remove: list
    """
    index_to_remove = []
    data_provider = layer.dataProvider()

    for field in fields_to_remove:
        index = layer.fieldNameIndex(field)
        if index != -1:
            index_to_remove.append(index)

    data_provider.deleteAttributes(index_to_remove)
    layer.updateFields()
