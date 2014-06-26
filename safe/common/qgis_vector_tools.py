# coding=utf-8
"""**Utilities around QgsVectorLayer**
"""

__author__ = 'Dmitry Kolesov <kolesov.dm@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '14/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import itertools

from safe.common.utilities import unique_filename
from safe.storage.raster import qgis_imported
from safe.common.exceptions import WrongDataTypeException

if qgis_imported:   # Import QgsRasterLayer if qgis is available
    from PyQt4.QtCore import QVariant
    from qgis.core import (
        QgsField,
        QgsVectorLayer,
        QgsFeature,
        QgsPoint,
        QgsGeometry,
        QgsFeatureRequest,
        QgsVectorFileWriter,
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform
    )


def points_to_rectangles(points, dx, dy):
    """Create polygon layer around points. The polygons are dx to dy.
    Attributes of the points are copied.
    A point position is upper-left corner of the created rectangle.

    :param points:  Point layer.
    :type points:   QgsVectorLayer

    :param dx:      Length of the horizontal sides
    :type dx:       float

    :param dy:      Length of the vertical sides
    :type dy:       float

    :returns:       Polygon layer
    :rtype:         QgsVectorLayer
    """

    crs = points.crs().toWkt()
    point_provider = points.dataProvider()
    fields = point_provider.fields()

    # Create layer for store the lines from E and extent
    polygons = QgsVectorLayer(
        'Polygon?crs=' + crs, 'polygons', 'memory')
    polygon_provider = polygons.dataProvider()

    polygon_provider.addAttributes(fields.toList())
    polygons.startEditing()
    for feature in points.getFeatures():
        attrs = feature.attributes()
        point = feature.geometry().asPoint()
        x, y = point.x(), point.y()
        # noinspection PyCallByClass,PyTypeChecker
        g = QgsGeometry.fromPolygon([
            [QgsPoint(x, y),
             QgsPoint(x + dx, y),
             QgsPoint(x + dx, y - dy),
             QgsPoint(x, y - dy)]
        ])
        polygon_feat = QgsFeature()
        polygon_feat.setGeometry(g)
        polygon_feat.setAttributes(attrs)
        _ = polygon_provider.addFeatures([polygon_feat])
    polygons.commitChanges()

    return polygons


def union_geometry(vector, request=QgsFeatureRequest()):
    """Return union of the vector geometries regardless of the attributes.
    (If request is specified, filter the objects before union).
    If all geometries in the vector are invalid, return None.

    The boundaries will be dissolved during the operation.

    :param vector:  Vector layer
    :type vector:   QgsVectorLayer

    :param request: Filter for vector objects
    :type request:  QgsFeatureRequest

    :return:        Union of the geometry
    :rtype:         QgsGeometry or None
    """

    result_geometry = None
    for feature in vector.getFeatures(request):
        if result_geometry is None:
            result_geometry = QgsGeometry(feature.geometry())
        else:
            # But some feature.geometry() may be invalid, skip them
            tmp_geometry = result_geometry.combine(feature.geometry())
            try:
                if tmp_geometry.isGeosValid():
                    result_geometry = tmp_geometry
            except AttributeError:
                pass
    return result_geometry


def create_layer(vector):
    """Create empty layer.

    The CRS and Geometry Type of new layer are the same as of vector layer.
    Attributes of the layer are copied from vector.

    :param vector:  Vector layer
    :type vector:   QgsVectorLayer

    :returns: Empty vector layer (stored in memory)
    :rtype: QgsVectorLayer
    """
    crs = vector.crs().toWkt()
    if vector.geometryType() == 0:
        msg = "Points cant' be split"
        raise WrongDataTypeException(msg)
    elif vector.geometryType() == 1:
        uri = 'LineString?crs=' + crs
    elif vector.geometryType() == 2:
        uri = 'Polygon?crs=' + crs
    else:
        msg = "Received unexpected type of layer geometry: %s" \
              % (vector.geometryType(),)
        raise WrongDataTypeException(msg)

    result_layer = QgsVectorLayer(uri, 'intersected', 'memory')
    result_provider = result_layer.dataProvider()
    result_layer.startEditing()

    # Copy fields from vector
    vector_provider = vector.dataProvider()
    fields = vector_provider.fields()
    result_provider.addAttributes(fields.toList())
    result_layer.commitChanges()

    return result_layer


def clip_by_polygon(
        vector,
        polygon):
    """Clip vector layer using polygon.

    Return part of the objects that lie within the polygon.

    :param vector:  Vector layer
    :type vector:   QgsVectorLayer

    :param polygon: Clipping polygon
    :type polygon:  QgsGeometry

    :returns: Vector layer with split geometry
    :rtype: QgsVectorLayer
    """
    result_layer = create_layer(vector)
    result_layer.startEditing()
    for feature in vector.getFeatures():
        geom = feature.geometry()
        attributes = feature.attributes()
        geometry_type = geom.type()
        if polygon.intersects(geom):
            # Find parts of initial_geom, intersecting
            # with the polygon, then mark them if needed
            intersection = QgsGeometry(
                geom.intersection(polygon)
            ).asGeometryCollection()

            for g in intersection:
                if g.type() == geometry_type:
                    feature = QgsFeature()
                    feature.setGeometry(g)
                    feature.setAttributes(attributes)
                    _ = result_layer.dataProvider().addFeatures([feature])

    result_layer.commitChanges()
    result_layer.updateExtents()
    return result_layer


def split_by_polygon(
        vector,
        polygon,
        request=QgsFeatureRequest(),
        mark_value=None):
    """Split objects from vector layer by polygon.

    If request is specified, filter the objects before splitting.

    If part of vector object lies in the polygon, mark it by mark_value (
    optional).

    :param vector:  Vector layer
    :type vector:   QgsVectorLayer

    :param polygon: Splitting polygon
    :type polygon:  QgsGeometry

    :param request: Filter for vector objects
    :type request:  QgsFeatureRequest

    :param mark_value:  Field value to mark the objects.
    :type mark_value:   (field_name, field_value).or None

    :returns: Vector layer with split geometry
    :rtype: QgsVectorLayer
    """

    def _set_feature(geometry, feature_attributes):
        """
        Helper to create and set up feature
        """
        included_feature = QgsFeature()
        included_feature.setGeometry(geometry)
        included_feature.setAttributes(feature_attributes)
        return included_feature

    def _update_attr_list(attributes, index, value, add_attribute=False):
        """
        Helper for update list of attributes.
        """
        new_attributes = attributes[:]
        if add_attribute:
            new_attributes.append(value)
        else:
            new_attributes[index] = value
        return new_attributes

    # Create layer to store the splitted objects
    result_layer = create_layer(vector)
    result_provider = result_layer.dataProvider()
    fields = result_provider.fields()

    # If target_field does not exist, add it:
    new_field_added = False
    if mark_value is not None:
        target_field = mark_value[0]
        if fields.indexFromName(target_field) == -1:
            result_layer.startEditing()
            result_provider.addAttributes(
                [QgsField(target_field, QVariant.Int)])
            new_field_added = True
            result_layer.commitChanges()
    target_value = None

    if mark_value is not None:
        target_field = mark_value[0]
        target_value = mark_value[1]
        target_field_index = result_provider.fieldNameIndex(target_field)
        if target_field_index == -1:
            raise WrongDataTypeException(
                'Field not found for %s' % target_field)

    # Start split procedure
    result_layer.startEditing()
    for initial_feature in vector.getFeatures(request):
        initial_geom = initial_feature.geometry()
        attributes = initial_feature.attributes()
        geometry_type = initial_geom.type()
        if polygon.intersects(initial_geom):
            # Find parts of initial_geom, intersecting
            # with the polygon, then mark them if needed
            intersection = QgsGeometry(
                initial_geom.intersection(polygon)
            ).asGeometryCollection()

            for g in intersection:
                if g.type() == geometry_type:
                    if mark_value is not None:
                        new_attributes = _update_attr_list(
                            attributes,
                            target_field_index,
                            target_value,
                            add_attribute=new_field_added
                        )
                    else:
                        new_attributes = attributes
                    feature = _set_feature(g, new_attributes)
                    _ = result_layer.dataProvider().addFeatures([feature])

            # Find parts of the initial_geom that do not lie in the polygon
            diff_geom = QgsGeometry(
                initial_geom.symDifference(polygon)
            ).asGeometryCollection()
            for g in diff_geom:
                if g.type() == geometry_type:
                    if mark_value is not None:
                        new_attributes = _update_attr_list(
                            attributes,
                            target_field_index,
                            0,
                            add_attribute=new_field_added
                        )
                    else:
                        new_attributes = attributes
                    feature = _set_feature(g, new_attributes)
                    _ = result_layer.dataProvider().addFeatures([feature])
        else:
            if mark_value is not None:
                new_attributes = _update_attr_list(
                    attributes,
                    target_field_index,
                    0,
                    add_attribute=new_field_added
                )
            else:
                new_attributes = attributes
            feature = _set_feature(initial_geom, new_attributes)
            _ = result_layer.dataProvider().addFeatures([feature])
    result_layer.commitChanges()
    result_layer.updateExtents()

    return result_layer


def split_by_polygon_in_out(
        vector,
        polygon_in,
        polygon_out,
        target_field,
        value,
        request=QgsFeatureRequest()):

    """Split a polygon layer updating the target field with the value.

    All parts of vector layer will have their target_field updated to
    value if they fall within polygon_in.

    :param vector: A polygon vector layer to split.
    :type vector: QgsVectorLayer

    :param polygon_in: Polygon within which vector features will be considered
        to be contained.
    :type polygon_in: QgsGeometry

    :param polygon_out: Polygon within which vector features will be considered
        to be NOT contained.
    :type polygon_out: QgsGeometry

    :param target_field: Field in vector layer to be updated if features
        are within polygon_in.
    :type target_field: QgsField

    :param value: Value to update the target field with if polygons are in.
    :type value: int, float, str

    :param request: Optional feature request used to subset the features
        in vector.
    :type request: QgsFeatureRequest

    :return: QgsVectorLayer of split line for whichever is greater,
        in our out polygons.
    :rtype: QgsVectorLayer
    """
    base_name = unique_filename()
    file_name_in = base_name + '_in.shp'
    file_name_out = base_name + '_out.shp'

    file_name_poly_in = base_name + '_poly_in.shp'
    file_name_poly_out = base_name + '_poly_out.shp'

    # noinspection PyArgumentEqualDefault
    line_layer_in = split_by_polygon2(
        vector,
        polygon_in,
        request,
        use_contains_operation=False,
        mark_value=(target_field, value))
    line_layer_out = split_by_polygon2(
        vector,
        polygon_out,
        request,
        use_contains_operation=True,
        mark_value=(target_field, 0))

    QgsVectorFileWriter.writeAsVectorFormat(
        line_layer_in, file_name_in, "utf-8", None, "ESRI Shapefile")
    QgsVectorFileWriter.writeAsVectorFormat(
        line_layer_out, file_name_out, "utf-8", None, "ESRI Shapefile")
    QgsVectorFileWriter.writeAsVectorFormat(
        polygon_in, file_name_poly_in, "utf-8", None, "ESRI Shapefile")
    QgsVectorFileWriter.writeAsVectorFormat(
        polygon_out, file_name_poly_out, "utf-8", None, "ESRI Shapefile")
    #merge layers
    in_features = line_layer_in.featureCount()
    out_features = line_layer_out.featureCount()
    if in_features > out_features:
        for feature in line_layer_out.getFeatures():
            line_layer_in.dataProvider().addFeatures([feature])
        return line_layer_in
    else:
        for feature in line_layer_in.getFeatures():
            line_layer_out.dataProvider().addFeatures([feature])
        return line_layer_out


def split_by_polygon2(
        vector,
        polygon_layer,
        request=QgsFeatureRequest(),
        use_contains_operation=False,
        mark_value=None):
    """Split objects from vector layer by polygon.

    If request is specified, filter the objects before splitting.

    If part of vector object lies in the polygon, mark it by mark_value (
    optional).

    :param vector:  Vector layer
    :type vector:   QgsVectorLayer

    :param polygon_layer: Splitting polygons layer
    :type polygon_layer:  QgsVectorLayer

    :param request: Filter for vector objects
    :type request:  QgsFeatureRequest

    :param use_contains_operation: Whether to use geometrical containment.
    :type use_contains_operation: bool

    :param mark_value:  Field value to mark the objects.
    :type mark_value:   (field_name, field_value).or None

    :returns: Vector layer with split geometry
    :rtype: QgsVectorLayer
    """

    def _set_feature(geometry, attributes):
        """
        Helper to create and set up feature
        """
        included_feature = QgsFeature()
        included_feature.setGeometry(geometry)
        included_feature.setAttributes(attributes)
        return included_feature

    def _update_attr_list(attributes, index, value, add_attribute=False):
        """
        Helper for update list of attributes.
        """
        new_attributes = attributes[:]
        if add_attribute:
            new_attributes.append(value)
        else:
            new_attributes[index] = value
        return new_attributes

    # Create layer to store the splitted objects
    result_layer = create_layer(vector)
    result_provider = result_layer.dataProvider()
    fields = result_provider.fields()

    # If target_field does not exist, add it:
    new_field_added = False
    if mark_value is not None:
        target_field = mark_value[0]
        if fields.indexFromName(target_field) == -1:
            result_layer.startEditing()
            result_provider.addAttributes(
                [QgsField(target_field, QVariant.Int)])
            new_field_added = True
            result_layer.commitChanges()
    target_value = None

    if mark_value is not None:
        target_field = mark_value[0]
        target_value = mark_value[1]
        target_field_index = result_provider.fieldNameIndex(target_field)
        if target_field_index == -1:
            raise WrongDataTypeException(
                'Field not found for %s' % target_field)

    # Start split procedure

    line_geoms = []
    line_attributes = []

    for initial_feature in vector.getFeatures(request):
        initial_geom = initial_feature.geometry()
        line_geoms.append(QgsGeometry(initial_geom))
        attributes = initial_feature.attributes()
        line_attributes.append(attributes)
        geometry_type = initial_geom.type()

    poly_geoms = []
    for polygon_feature in polygon_layer.getFeatures(request):
        polygon = polygon_feature.geometry()
        poly_geoms.append(QgsGeometry(polygon))

    result_layer.startEditing()

    for polygon in poly_geoms:
        for initial_geom, attributes in \
                itertools.izip(line_geoms, line_attributes):

            if use_contains_operation:
                poly_contains = polygon.contains(initial_geom)
            else:
                poly_contains = False

            poly_intersect = False
            if not poly_contains:
                poly_intersect = polygon.intersects(initial_geom)

            if poly_contains or poly_intersect:
            # Find parts of initial_geom, intersecting
            # with the polygon, then mark them if needed
                if poly_contains:
                    g = initial_geom
                    if mark_value is not None:
                        new_attributes = _update_attr_list(
                            attributes,
                            target_field_index,
                            target_value,
                            add_attribute=new_field_added
                        )
                    else:
                        new_attributes = attributes
                    feature = _set_feature(g, new_attributes)
                    _ = result_layer.dataProvider().addFeatures([feature])

                else:
                    intersection = QgsGeometry(
                        initial_geom.intersection(polygon)
                    ).asGeometryCollection()

                    for g in intersection:
                        if g.type() == geometry_type:
                            if mark_value is not None:
                                new_attributes = _update_attr_list(
                                    attributes,
                                    target_field_index,
                                    target_value,
                                    add_attribute=new_field_added
                                )
                            else:
                                new_attributes = attributes
                            feature = _set_feature(g, new_attributes)
                            _ = result_layer.dataProvider().\
                                addFeatures([feature])

    result_layer.commitChanges()
    result_layer.updateExtents()
    return result_layer


def extent_to_geo_array(extent, source_crs, dest_crs=None):
    """Convert the supplied extent to geographic and return as an array.

    :param extent: Rectangle defining a spatial extent in any CRS.
    :type extent: QgsRectangle

    :param source_crs: Coordinate system used for extent.
    :type source_crs: QgsCoordinateReferenceSystem

    :returns: a list in the form [xmin, ymin, xmax, ymax] where all
            coordinates provided are in Geographic / EPSG:4326.
    :rtype: list

    """

    if dest_crs is None:
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromSrid(4326)
    else:
        geo_crs = dest_crs

    transform = QgsCoordinateTransform(source_crs, geo_crs)

    # Get the clip area in the layer's crs
    transformed_extent = transform.transformBoundingBox(extent)

    geo_extent = [
        transformed_extent.xMinimum(),
        transformed_extent.yMinimum(),
        transformed_extent.xMaximum(),
        transformed_extent.yMaximum()]
    return geo_extent


def reproject_vector_layer(layer, crs):
    """Reproject a vector layer to given CRS

    :param layer: Vector layer
    :type layer: QgsVectorLayer

    :param crs: Coordinate system for reprojection.
    :type crs: QgsCoordinateReferenceSystem

    :returns: a vector layer with the specified projection
    :rtype: QgsVectorLayer

    """

    base_name = unique_filename()
    file_name = base_name + '.shp'
    print "reprojected layer1 %s" % file_name
    QgsVectorFileWriter.writeAsVectorFormat(
        layer, file_name, "utf-8", crs, "ESRI Shapefile")

    return QgsVectorLayer(file_name, base_name, "ogr")
