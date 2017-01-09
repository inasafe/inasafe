# coding=utf-8
"""**Utilities around QgsVectorLayer**
"""

__author__ = 'Dmitry Kolesov <kolesov.dm@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '14/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsPoint,
    QgsGeometry,
    QgsFeatureRequest,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform)
from PyQt4.QtCore import QVariant

from safe.common.utilities import unique_filename
from safe.common.exceptions import WrongDataTypeException


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
        # We can create layer from Point. Do not need to split it.
        uri = 'Point?crs=' + crs
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
