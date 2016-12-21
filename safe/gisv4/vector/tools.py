# coding=utf-8

"""
Tools for vector layers.
"""

from uuid import uuid4
from PyQt4.QtCore import QPyNullVariant
from qgis.core import (
    QgsGeometry,
    QgsVectorLayer,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsCoordinateReferenceSystem,
    QGis,
    QgsFeature,
    QgsField,
    QgsDistanceArea,
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
        layer_name, geometry, coordinate_reference_system=None, fields=None):
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
    elif geometry == QGis.NoGeometry:
        type_string = 'none'
    else:
        raise MemoryLayerCreationError(
            'Layer is whether Point nor Line nor Polygon, I got %s' % geometry)

    uri = '%s?index=yes&uuid=%s' % (type_string, str(uuid4()))
    if coordinate_reference_system:
        crs = coordinate_reference_system.authid().lower()
        uri += '&crs=%s' % crs
    memory_layer = QgsVectorLayer(uri, layer_name, 'memory')
    memory_layer.keywords = {
        'inasafe_fields': {}
    }

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

    request = QgsFeatureRequest()

    if source.keywords.get('layer_purpose') == 'aggregation':
        try:
            use_selected_only = source.use_selected_features_only
        except AttributeError:
            use_selected_only = False

        # We need to check if the user wants selected feature only and if there
        # is one minimum selected.
        if use_selected_only and source.selectedFeatureCount() > 0:
            request.setFilterFids(source.selectedFeaturesIds())

    for i, feature in enumerate(source.getFeatures(request)):
        geom = feature.geometry()
        out_feature.setGeometry(QgsGeometry(geom))
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


@profile
def create_spatial_index(layer):
    """Helper function to create the spatial index on a vector layer.

    This function is mainly used to see the processing time with the decorator.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The index.
    :rtype: QgsSpatialIndex
    """
    spatial_index = QgsSpatialIndex(layer.getFeatures())
    return spatial_index


def create_field_from_definition(field_definition, name=None):
    """Helper to create a field from definition.

    :param field_definition: The definition of the field.
    :type field_definition: safe.definitionsv4.fields

    :param name: The name is required if the field name is dynamic and need a
        string formatting.
    :type name: basestring

    :return: The new field.
    :rtype: QgsField
    """
    field = QgsField()

    if isinstance(name, QPyNullVariant):
        name = 'NULL'

    if name:
        field.setName(field_definition['field_name'] % name)
    else:
        field.setName(field_definition['field_name'])

    if isinstance(field_definition['type'], list):
        # Use the first element in the list of type
        field.setType(field_definition['type'][0])
    else:
        field.setType(field_definition['type'])
    field.setLength(field_definition['length'])
    field.setPrecision(field_definition['precision'])
    return field


def read_dynamic_inasafe_field(inasafe_fields, dynamic_field):
    """Helper to read inasafe_fields using a dynamic field.

    :param inasafe_fields: inasafe_fields keywords to use.
    :type inasafe_fields: dict

    :param dynamic_field: The dynamic field to use.
    :type dynamic_field: safe.definitions.fields

    :return: A list of unique value used in this dynamic field.
    :return: list
    """
    pattern = dynamic_field['key']
    pattern = pattern.replace('%s', '')
    unique_exposure = []
    for key, name_field in inasafe_fields.iteritems():
        if key.endswith(pattern):
            unique_exposure.append(key.replace(pattern, ''))

    return unique_exposure


@profile
def size_calculator(crs):
    """Helper function to create a size calculator according to a CRS.

    :param crs: The coordinate reference system to use.
    :type crs: QgsCoordinateReferenceSystem

    :return: The QgsDistanceArea object.
    :rtype: QgsDistanceArea
    """
    calculator = QgsDistanceArea()
    calculator.setSourceCrs(crs)
    calculator.setEllipsoid('WGS84')
    calculator.setEllipsoidalMode(True)
    return calculator
