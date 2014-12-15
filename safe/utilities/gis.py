# coding=utf-8
"""Helpers for GIS related functionality."""
import uuid
from qgis.core import QgsMapLayer, QgsCoordinateReferenceSystem, \
    QgsCoordinateTransform, QGis, QgsVectorLayer, QgsRasterLayer
from safe.common.exceptions import MemoryLayerCreationError
from safe.storage.core import read_layer as safe_read_layer
from safe.storage.layer import Layer
from safe.utilities.utilities import LOGGER, tr


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


def viewport_geo_array(map_canvas):
    """Obtain the map canvas current extent in EPSG:4326.

    :param map_canvas: A map canvas instance.
    :type map_canvas: QgsMapCanvas

    :returns: A list in the form [xmin, ymin, xmax, ymax] where all
        coordinates provided are in Geographic / EPSG:4326.
    :rtype: list

    .. note:: Delegates to extent_to_array()
    """

    # get the current viewport extent
    rectangle = map_canvas.extent()

    destination_crs = QgsCoordinateReferenceSystem()
    destination_crs.createFromSrid(4326)

    if map_canvas.hasCrsTransformEnabled():
        source_crs = map_canvas.mapRenderer().destinationCrs()
    else:
        source_crs = destination_crs

    return extent_to_array(rectangle, source_crs, destination_crs)


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


def qgis_version():
    """Get the version of QGIS.

    :returns: QGIS Version where 10700 represents QGIS 1.7 etc.
    :rtype: int
    """
    version = unicode(QGis.QGIS_VERSION_INT)
    version = int(version)
    return version


def get_wgs84_resolution(layer):
    """Return resolution of raster layer in EPSG:4326.

    If input layer is already in EPSG:4326, simply return the resolution
    If not, work it out based on EPSG:4326 representations of its extent.

    :param layer: Raster layer
    :type layer: QgsRasterLayer or QgsMapLayer

    :returns: The resolution of the given layer in the form of (res_x, res_y)
    :rtype: tuple
    """

    msg = tr(
        'Input layer to get_wgs84_resolution must be a raster layer. '
        'I got: %s' % str(layer.type())[1:-1])

    if not layer.type() == QgsMapLayer.RasterLayer:
        raise RuntimeError(msg)

    if layer.crs().authid() == 'EPSG:4326':
        cell_size = (
            layer.rasterUnitsPerPixelX(), layer.rasterUnitsPerPixelY())
    else:
        # Otherwise, work it out based on EPSG:4326 representations of
        # its extent

        # Reproject extent to EPSG:4326
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromSrid(4326)
        transform = QgsCoordinateTransform(layer.crs(), geo_crs)
        extent = layer.extent()
        projected_extent = transform.transformBoundingBox(extent)

        # Estimate resolution x
        columns = layer.width()
        width = abs(
            projected_extent.xMaximum() -
            projected_extent.xMinimum())
        cell_size_x = width / columns

        # Estimate resolution y
        rows = layer.height()
        height = abs(
            projected_extent.yMaximum() -
            projected_extent.yMinimum())
        cell_size_y = height / rows

        cell_size = (cell_size_x, cell_size_y)

    return cell_size


def create_memory_layer(layer, new_name=''):
    """Return a memory copy of a layer

    :param layer: QgsVectorLayer that shall be copied to memory.
    :type layer: QgsVectorLayer

    :param new_name: The name of the copied layer.
    :type new_name: str

    :returns: An in-memory copy of a layer.
    :rtype: QgsMapLayer
    """

    if new_name is '':
        new_name = layer.name() + ' TMP'

    if layer.type() == QgsMapLayer.VectorLayer:
        vector_type = layer.geometryType()
        if vector_type == QGis.Point:
            type_string = 'Point'
        elif vector_type == QGis.Line:
            type_string = 'Line'
        elif vector_type == QGis.Polygon:
            type_string = 'Polygon'
        else:
            raise MemoryLayerCreationError('Layer is whether Point nor '
                                           'Line nor Polygon')
    else:
        raise MemoryLayerCreationError('Layer is not a VectorLayer')

    crs = layer.crs().authid().lower()
    uuid_string = str(uuid.uuid4())
    uri = '%s?crs=%s&index=yes&uuid=%s' % (type_string, crs, uuid_string)
    memory_layer = QgsVectorLayer(uri, new_name, 'memory')
    memory_provider = memory_layer.dataProvider()

    provider = layer.dataProvider()
    vector_fields = provider.fields()

    fields = []
    for i in vector_fields:
        fields.append(i)

    memory_provider.addAttributes(fields)

    for ft in provider.getFeatures():
        memory_provider.addFeatures([ft])

    return memory_layer


def layer_attribute_names(layer, allowed_types, current_keyword=None):
    """Iterates over the layer and returns int or string fields.

    :param layer: A vector layer whose attributes shall be returned.
    :type layer: QgsVectorLayer, QgsMapLayer

    :param allowed_types: List of QVariant that are acceptable for the
        attribute. e.g.: [QtCore.QVariant.Int, QtCore.QVariant.String].
    :type allowed_types: list(QVariant)

    :param current_keyword: The currently stored keyword for the attribute.
    :type current_keyword: str

    :returns: A two-tuple containing all the attribute names of attributes
        that have int or string as field type (first element) and the position
        of the current_keyword in the attribute names list, this is None if
        current_keyword is not in the list of attributes (second element).
    :rtype: tuple(list(str), int)
    """

    if layer.type() == QgsMapLayer.VectorLayer:
        provider = layer.dataProvider()
        provider = provider.fields()
        fields = []
        selected_index = None
        i = 0
        for f in provider:
            # show only int or string fields to be chosen as aggregation
            # attribute other possible would be float
            if f.type() in allowed_types:
                current_field_name = f.name()
                fields.append(current_field_name)
                if current_keyword == current_field_name:
                    selected_index = i
                i += 1
        return fields, selected_index
    else:
        return None, None


def read_impact_layer(impact_layer):
    """Helper function to read and validate a safe native spatial layer.

    :param impact_layer: Layer object as provided by InaSAFE engine.
    :type impact_layer: read_layer

    :returns: Valid QGIS layer or None
    :rtype: None, QgsRasterLayer, QgsVectorLayer
    """

    # noinspection PyUnresolvedReferences
    message = tr(
        'Input layer must be a InaSAFE spatial object. '
        'I got %s') % (str(type(impact_layer)))
    if not hasattr(impact_layer, 'is_inasafe_spatial_object'):
        raise Exception(message)
    if not impact_layer.is_inasafe_spatial_object:
        raise Exception(message)

    # Get associated filename and symbolic name
    file_name = impact_layer.get_filename()
    name = impact_layer.get_name()

    qgis_layer = None
    # Read layer
    if impact_layer.is_vector:
        qgis_layer = QgsVectorLayer(file_name, name, 'ogr')
    elif impact_layer.is_raster:
        qgis_layer = QgsRasterLayer(file_name, name)

    # Verify that new qgis layer is valid
    if qgis_layer.isValid():
        return qgis_layer
    else:
        # noinspection PyUnresolvedReferences
        message = tr(
            'Loaded impact layer "%s" is not valid') % file_name
        raise Exception(message)


def convert_to_safe_layer(layer):
    """Thin wrapper around the safe read_layer function.

    :param layer: QgsMapLayer or Safe layer.
    :type layer: QgsMapLayer, read_layer

    :returns: A safe read_safe_layer object is returned.
    :rtype: read_layer
    """
    if isinstance(layer, Layer):
        return layer
    try:
        return safe_read_layer(layer.source())
    except:
        raise
