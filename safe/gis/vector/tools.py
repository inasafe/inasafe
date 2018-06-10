# coding=utf-8

"""Tools for vector layers."""


import logging
from math import isnan
from uuid import uuid4

import ogr
from qgis.core import (
    QgsGeometry,
    QgsVectorLayer,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsFeature,
    QgsField,
    QgsProject,
    QgsDistanceArea,
    QgsWkbTypes
)

from qgis.PyQt.QtCore import QVariant

from safe.common.exceptions import (
    MemoryLayerCreationError,
    # SpatialIndexCreationError,
)
from safe.definitions.units import unit_metres, unit_square_metres
from safe.definitions.utilities import definition
from safe.gis.vector.clean_geometry import geometry_checker, clean_layer
from safe.utilities.profiling import profile
from safe.utilities.rounding import convert_unit

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')

wkb_type_groups = {
    'Point': (
        QgsWkbTypes.Point,
        QgsWkbTypes.MultiPoint,
        QgsWkbTypes.Point25D,
        QgsWkbTypes.MultiPoint25D,),
    'LineString': (
        QgsWkbTypes.LineString,
        QgsWkbTypes.MultiLineString,
        QgsWkbTypes.LineString25D,
        QgsWkbTypes.MultiLineString25D,),
    'Polygon': (
        QgsWkbTypes.Polygon,
        QgsWkbTypes.MultiPolygon,
        QgsWkbTypes.Polygon25D,
        QgsWkbTypes.MultiPolygon25D,),
}
for key, value in list(wkb_type_groups.items()):
    for const in value:
        wkb_type_groups[const] = key

# This table come from https://qgis.org/api/qgsunittypes_8h_source.html#l00043
distance_unit = {
    0: 'Meters',
    1: 'Kilometres',
    2: 'Feets',
    3: 'Nautical Miles',
    4: 'Yards',
    5: 'Miles',
    6: 'Degrees',
    7: 'Unknown Unit'
}

# This table come from https://qgis.org/api/qgsunittypes_8h_source.html#l00065
area_unit = {
    0: 'Square Meters',
    1: 'Square Kilometres',
    2: 'Square Feet',
    3: 'Square Yards',
    4: 'Square Miles',
    5: 'Hectares',
    6: 'Acres',
    7: 'Square Nautical Miles',
    8: 'Square Degrees',
    9: 'unknown Unit'
}

# Field type converter from QGIS to OGR
# Source http://www.gdal.org/ogr__core_8h.html#a787194be
field_type_converter = {
    QVariant.String: ogr.OFTString,
    QVariant.Int: ogr.OFTInteger,
    QVariant.Double: ogr.OFTReal,
}


@profile
def create_memory_layer(
        layer_name, geometry, coordinate_reference_system=None, fields=None):
    """Create a vector memory layer.

    :param layer_name: The name of the layer.
    :type layer_name: str

    :param geometry: The geometry of the layer.
    :rtype geometry: QgsWkbTypes (note: from C++ QgsWkbTypes::GeometryType enum)

    :param coordinate_reference_system: The CRS of the memory layer.
    :type coordinate_reference_system: QgsCoordinateReferenceSystem

    :param fields: Fields of the vector layer. Default to None.
    :type fields: QgsFields

    :return: The memory layer.
    :rtype: QgsVectorLayer
    """

    if geometry == QgsWkbTypes.PointGeometry:
        type_string = 'MultiPoint'
    elif geometry == QgsWkbTypes.LineGeometry:
        type_string = 'MultiLineString'
    elif geometry == QgsWkbTypes.PolygonGeometry:
        type_string = 'MultiPolygon'
    elif geometry == QgsWkbTypes.NullGeometry:
        type_string = 'none'
    else:
        raise MemoryLayerCreationError(
            'Layer geometry must be one of: Point, Line, Polygon or Null, I got %s' % geometry)

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

    aggregation_layer = False
    if source.keywords.get('layer_purpose') == 'aggregation':
        try:
            use_selected_only = source.use_selected_features_only
        except AttributeError:
            use_selected_only = False

        # We need to check if the user wants selected feature only and if there
        # is one minimum selected.
        if use_selected_only and source.selectedFeatureCount() > 0:
            request.setFilterFids(source.selectedFeatureIds())

        aggregation_layer = True

    for i, feature in enumerate(source.getFeatures(request)):
        geom = feature.geometry()
        if aggregation_layer:
            # See issue https://github.com/inasafe/inasafe/issues/3713
            # and issue https://github.com/inasafe/inasafe/issues/3927
            # Also handle if feature has no geometry.
            geom = geometry_checker(geom)
            if not geom or not geom.isGeosValid():
                LOGGER.info(
                    'One geometry in the aggregation layer is still invalid '
                    'after cleaning.')
        out_feature.setGeometry(QgsGeometry(geom))
        out_feature.setAttributes(feature.attributes())
        target.addFeature(out_feature)

    target.commitChanges()


@profile
def rename_fields(layer, fields_to_copy):
    """Rename fields inside an attribute table.

    Only since QGIS 2.16.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param fields_to_copy: Dictionary of fields to copy.
    :type fields_to_copy: dict
    """
    for field in fields_to_copy:
        index = layer.fields().lookupField(field)
        if index != -1:
            layer.startEditing()
            layer.renameAttribute(index, fields_to_copy[field])
            layer.commitChanges()
            LOGGER.info(
                'Renaming field %s to %s' % (field, fields_to_copy[field]))
        else:
            LOGGER.info(
                'Field %s not present in the layer while trying to renaming '
                'it to %s' % (field, fields_to_copy[field]))


@profile
def copy_fields(layer, fields_to_copy):
    """Copy fields inside an attribute table.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param fields_to_copy: Dictionary of fields to copy.
    :type fields_to_copy: dict
    """
    for field in fields_to_copy:

        index = layer.fields().lookupField(field)
        if index != -1:

            layer.startEditing()

            source_field = layer.fields().at(index)
            new_field = QgsField(source_field)
            new_field.setName(fields_to_copy[field])

            layer.addAttribute(new_field)

            new_index = layer.fields().lookupField(fields_to_copy[field])

            for feature in layer.getFeatures():
                attributes = feature.attributes()
                source_value = attributes[index]
                layer.changeAttributeValue(
                    feature.id(), new_index, source_value)

            layer.commitChanges()
            layer.updateFields()  # Avoid crash #4729


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
        index = layer.fields().lookupField(field)
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
    request = QgsFeatureRequest().setSubsetOfAttributes([])
    try:
        spatial_index = QgsSpatialIndex(layer.getFeatures(request))
    except BaseException:
        # Spatial index is creating an unknown exception.
        # https://github.com/inasafe/inasafe/issues/4304
        # or https://gitter.im/inasafe/inasafe?at=5a2903d487680e6230e0359a
        LOGGER.warning(
            'An Exception has been raised from the spatial index creation. '
            'We will clean your layer and try again.')
        new_layer = clean_layer(layer)
        try:
            spatial_index = QgsSpatialIndex(new_layer.getFeatures())
        except BaseException:
            # We got another exception.
            # We try now to insert feature by feature.
            # It's slower than the using the feature iterator.
            spatial_index = QgsSpatialIndex()
            for feature in new_layer.getFeatures(request):
                try:
                    spatial_index.insertFeature(feature)
                except BaseException:
                    LOGGER.critical(
                        'A feature has been removed from the spatial index.')

            # # We tried one time to clean the layer, we can't do more.
            # LOGGER.critical(
            #     'An Exception has been raised from the spatial index '
            #     'creation. Unfortunately, we already try to clean your '
            #     'layer. We will stop here the process.')
            # raise SpatialIndexCreationError
    return spatial_index


def create_field_from_definition(field_definition, name=None, sub_name=None):
    """Helper to create a field from definition.

    :param field_definition: The definition of the field (see:
        safe.definitions.fields).
    :type field_definition: dict

    :param name: The name is required if the field name is dynamic and need a
        string formatting.
    :type name: basestring

    :param sub_name: The name is required if the field name is dynamic and need
        a string formatting.
    :type sub_name: basestring

    :return: The new field.
    :rtype: QgsField
    """
    field = QgsField()

    if name and not sub_name:
        field.setName(field_definition['field_name'] % name)
    elif name and sub_name:
        field.setName(field_definition['field_name'] % (name, sub_name))
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


def create_ogr_field_from_definition(field_definition):
    """Helper to create a field from definition.

    :param field_definition: The definition of the field (see:
        safe.definitions.fields).
    :type field_definition: dict

    :return: The new ogr field definition.
    :rtype: ogr.FieldDefn
    """
    if isinstance(field_definition['type'], list):
        # Use the first element in the list of type
        field_type = field_definition['type'][0]
    else:
        field_type = field_definition['type']

    # Conversion to OGR field
    field_type = field_type_converter.get(field_type, ogr.OFTString)

    return ogr.FieldDefn(field_definition['field_name'], field_type)


def field_index_from_definition(layer, field_definition):

    return layer.fields().lookupField(field_definition['field_name'])


def read_dynamic_inasafe_field(inasafe_fields, dynamic_field, black_list=None):
    """Helper to read inasafe_fields using a dynamic field.

    :param inasafe_fields: inasafe_fields keywords to use.
    :type inasafe_fields: dict

    :param dynamic_field: The dynamic field to use.
    :type dynamic_field: safe.definitions.fields

    :param black_list: A list of fields which are conflicting with the dynamic
        field. Same field name pattern.

    :return: A list of unique value used in this dynamic field.
    :return: list
    """
    pattern = dynamic_field['key']
    pattern = pattern.replace('%s', '')

    if black_list is None:
        black_list = []

    black_list = [field['key'] for field in black_list]

    unique_exposure = []
    for field_key, name_field in list(inasafe_fields.items()):
        if field_key.endswith(pattern) and field_key not in black_list:
            unique_exposure.append(field_key.replace(pattern, ''))

    return unique_exposure


class SizeCalculator():

    """Special object to handle size calculation with an output unit."""

    def __init__(
            self, coordinate_reference_system, geometry_type, exposure_key):
        """Constructor for the size calculator.

        :param coordinate_reference_system: The Coordinate Reference System of
            the layer.
        :type coordinate_reference_system: QgsCoordinateReferenceSystem

        :param exposure_key: The geometry type of the layer.
        :type exposure_key: qgis.core.QgsWkbTypes.GeometryType
        """
        self.calculator = QgsDistanceArea()
        self.calculator.setSourceCrs(coordinate_reference_system, QgsProject.instance().transformContext())
        self.calculator.setEllipsoid('WGS84')

        if geometry_type == QgsWkbTypes.LineGeometry:
            self.default_unit = unit_metres
            LOGGER.info('The size calculator is set to use {unit}'.format(
                unit=distance_unit[self.calculator.lengthUnits()]))
        else:
            self.default_unit = unit_square_metres
            LOGGER.info('The size calculator is set to use {unit}'.format(
                unit=distance_unit[self.calculator.areaUnits()]))
        self.geometry_type = geometry_type
        self.output_unit = None
        if exposure_key:
            exposure_definition = definition(exposure_key)
            self.output_unit = exposure_definition['size_unit']

    def measure_distance(self, point_a, point_b):
        """Measure the distance between two points.

        This is added here since QgsDistanceArea object is already called here.

        :param point_a: First Point.
        :type point_a: QgsPoint

        :param point_b: Second Point.
        :type point_b: QgsPoint

        :return: The distance between input points.
        :rtype: float
        """
        return self.calculator.measureLine(point_a, point_b)

    def measure(self, geometry):
        """Measure the length or the area of a geometry.

        :param geometry: The geometry.
        :type geometry: QgsGeometry

        :return: The geometric size in the expected exposure unit.
        :rtype: float
        """
        message = 'Size with NaN value : geometry valid={valid}, WKT={wkt}'
        feature_size = 0
        if geometry.isMultipart():
            # Be careful, the size calculator is not working well on a
            # multipart.
            # So we compute the size part per part. See ticket #3812
            for single in geometry.asGeometryCollection():
                if self.geometry_type == QgsWkbTypes.LineGeometry:
                    geometry_size = self.calculator.measureLength(single)
                else:
                    geometry_size = self.calculator.measureArea(single)
                if not isnan(geometry_size):
                    feature_size += geometry_size
                else:
                    LOGGER.debug(message.format(
                        valid=single.isGeosValid(),
                        wkt=single.asWkt()))
        else:
            if self.geometry_type == QgsWkbTypes.LineGeometry:
                geometry_size = self.calculator.measureLength(geometry)
            else:
                geometry_size = self.calculator.measureArea(geometry)
            if not isnan(geometry_size):
                feature_size = geometry_size
            else:
                LOGGER.debug(message.format(
                    valid=geometry.isGeosValid(),
                    wkt=geometry.asWkt()))

        feature_size = round(feature_size)

        if self.output_unit:
            if self.output_unit != self.default_unit:
                feature_size = convert_unit(
                    feature_size, self.default_unit, self.output_unit)

        return feature_size
