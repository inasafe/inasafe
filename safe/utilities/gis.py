# coding=utf-8
"""Helpers for GIS related functionality."""
import uuid

from qgis.core import (
    QgsMapLayer,
    QgsField,
    QgsFeature,
    QgsPoint,
    QgsGeometry,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QGis,
    QgsRectangle,
    QgsPoint,
    QgsVectorLayer,
    QgsRasterLayer)
from safe.common.exceptions import (
    MemoryLayerCreationError,
    BoundingBoxError,
    InsufficientOverlapError,
)
from safe.storage.core import read_layer as safe_read_layer
from safe.storage.layer import Layer
from safe.storage.utilities import bbox_intersection
from safe.utilities.i18n import tr
from safe.utilities.utilities import LOGGER


def is_raster_layer(layer):
    """Check if a QGIS layer is raster.

    :param layer: A layer.
    :type layer: QgsRaster, QgsMapLayer, QgsVectorLayer

    :returns: True if the layer contains polygons, otherwise False.
    :rtype: bool
    """
    try:
        return layer.type() == QgsMapLayer.RasterLayer
    except AttributeError:
        return False


def extent_string_to_array(extent_text):
    """Convert an extent string to an array.

    .. versionadded: 2.2.0

    :param extent_text: String representing an extent e.g.
        109.829170982, -8.13333290561, 111.005344795, -7.49226294379
    :type extent_text: str

    :returns: A list of floats, or None
    :rtype: list, None
    """
    coordinates = extent_text.replace(' ', '').split(',')
    count = len(coordinates)
    if count != 4:
        message = (
            'Extent need exactly 4 value but got %s instead' % count)
        LOGGER.error(message)
        return None

    # parse the value to float type
    try:
        coordinates = [float(i) for i in coordinates]
    except ValueError as e:
        message = e.message
        LOGGER.error(message)
        return None
    return coordinates


def extent_to_array(extent, source_crs, dest_crs=None):
    """Convert the supplied extent to geographic and return as an array.

    :param extent: Rectangle defining a spatial extent in any CRS.
    :type extent: QgsRectangle

    :param source_crs: Coordinate system used for input extent.
    :type source_crs: QgsCoordinateReferenceSystem

    :param dest_crs: Coordinate system used for output extent. Defaults to
        EPSG:4326 if not specified.
    :type dest_crs: QgsCoordinateReferenceSystem

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


def rectangle_geo_array(rectangle, map_canvas):
    """Obtain the rectangle in EPSG:4326.

    :param rectangle: A rectangle instance.
    :type rectangle: QgsRectangle

    :param map_canvas: A map canvas instance.
    :type map_canvas: QgsMapCanvas

    :returns: A list in the form [xmin, ymin, xmax, ymax] where all
        coordinates provided are in Geographic / EPSG:4326.
    :rtype: list

    .. note:: Delegates to extent_to_array()
    """

    destination_crs = QgsCoordinateReferenceSystem()
    destination_crs.createFromSrid(4326)

    source_crs = map_canvas.mapSettings().destinationCrs()

    return extent_to_array(rectangle, source_crs, destination_crs)


def viewport_geo_array(map_canvas):
    """Obtain the map canvas current extent in EPSG:4326.

    :param map_canvas: A map canvas instance.
    :type map_canvas: QgsMapCanvas

    :returns: A list in the form [xmin, ymin, xmax, ymax] where all
        coordinates provided are in Geographic / EPSG:4326.
    :rtype: list

    .. note:: Delegates to rectangle_geo_array()
    """

    # get the current viewport extent
    rectangle = map_canvas.extent()

    return rectangle_geo_array(rectangle, map_canvas)


def validate_geo_array(extent):
    """Validate a geographic extent.

    .. versionadded:: 3.2

    :param extent: A list in the form [xmin, ymin, xmax, ymax] where all
        coordinates provided are in Geographic / EPSG:4326.
    :type extent: list

    :return: True if the extent is valid, otherwise False
    :rtype: bool
    """
    min_longitude = extent[0]
    min_latitude = extent[1]
    max_longitude = extent[2]
    max_latitude = extent[3]

    # min_latitude < max_latitude
    if min_latitude >= max_latitude:
        return False

    # min_longitude < max_longitude
    if min_longitude >= max_longitude:
        return False

    # -90 <= latitude <= 90
    if min_latitude < -90 or min_latitude > 90:
        return False
    if max_latitude < -90 or max_latitude > 90:
        return False

    # -180 <= longitude <= 180
    if min_longitude < -180 or min_longitude > 180:
        return False
    if max_longitude < -180 or max_longitude > 180:
        return False

    return True


def is_point_layer(layer):
    """Check if a QGIS layer is vector and its geometries are points.

    :param layer: A vector layer.
    :type layer: QgsVectorLayer, QgsMapLayer

    :returns: True if the layer contains points, otherwise False.
    :rtype: bool
    """
    try:
        return (layer.type() == QgsMapLayer.VectorLayer) and (
            layer.geometryType() == QGis.Point)
    except AttributeError:
        return False


def is_polygon_layer(layer):
    """Check if a QGIS layer is vector and its geometries are polygons.

    :param layer: A vector layer.
    :type layer: QgsVectorLayer, QgsMapLayer

    :returns: True if the layer contains polygons, otherwise False.
    :rtype: bool

    """
    try:
        return (layer.type() == QgsMapLayer.VectorLayer) and (
            layer.geometryType() == QGis.Polygon)
    except AttributeError:
        return False


def wkt_to_rectangle(extent):
    """Compute the rectangle from a WKT string.

    It returns None if the extent is not valid WKT rectangle.

    :param extent: The extent.
    :type extent: basestring

    :return: The rectangle or None if it is not a valid WKT rectangle.
    :rtype: QgsRectangle
    """
    geometry = QgsGeometry.fromWkt(extent)
    if not geometry.isGeosValid():
        return None

    polygon = geometry.asPolygon()[0]

    if len(polygon) != 5:
        return None

    if polygon[0] != polygon[4]:
        return None

    rectangle = QgsRectangle(
        QgsPoint(polygon[0].x(), polygon[0].y()),
        QgsPoint(polygon[2].x(), polygon[2].y()))

    return rectangle


def qgis_version():
    """Get the version of QGIS.

    :returns: QGIS Version where 10700 represents QGIS 1.7 etc.
    :rtype: int
    """
    version = unicode(QGis.QGIS_VERSION_INT)
    version = int(version)
    return version
