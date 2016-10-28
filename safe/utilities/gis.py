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
    QgsVectorLayer,
    QgsRasterLayer)
from PyQt4.QtCore import QVariant
from safe.common.exceptions import (
    MemoryLayerCreationError,
    BoundingBoxError,
    NoKeywordsFoundError,
    InsufficientOverlapError,
    RadiiException)
from safe.storage.core import read_layer as safe_read_layer
from safe.storage.layer import Layer
from safe.storage.utilities import bbox_intersection
from safe.utilities.i18n import tr
from safe.utilities.utilities import LOGGER
from safe.common.utilities import get_utm_epsg, unique_filename
from safe.utilities.keyword_io import KeywordIO


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


def array_to_geo_array(extent, source_crs):
    """Transform the extent in EPSG:4326.
    :param extent: A list in the form [xmin, ymin, xmax, ymax].
    :type extent: list
    :param source_crs: Coordinate system used for input extent.
    :type source_crs: QgsCoordinateReferenceSystem
    :return: A list in the form [xmin, ymin, xmax, ymax] where all
            coordinates provided are in Geographic / EPSG:4326.
    :rtype: list
    .. note:: Delegates to extent_to_array()
    """

    min_longitude = extent[0]
    min_latitude = extent[1]
    max_longitude = extent[2]
    max_latitude = extent[3]

    rectangle = QgsRectangle(
        min_longitude, min_latitude, max_longitude, max_latitude)
    return extent_to_array(rectangle, source_crs)


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


def vector_geometry_string(layer):
    """Get string representation of geometry types of a QgsVectorLayer.

    :param layer: A vector layer.
    :type layer: QgsVectorLayer

     :returns: A string 'point', 'line', or 'polygon'.
     :rtype: str
     """

    types = {
        QGis.Point: 'point',
        QGis.Line: 'line',
        QGis.Polygon: 'polygon'
    }

    if not layer.type() == QgsMapLayer.VectorLayer:
        return None

    return types.get(layer.geometryType())


def get_optimal_extent(
        hazard_geo_extent, exposure_geo_extent, viewport_geo_extent=None):
    """A helper function to determine what the optimal extent is.

    Optimal extent should be considered as the intersection between
    the three inputs. The inasafe library will perform various checks
    to ensure that the extent is tenable, includes data from both
    etc.

    This is a thin wrapper around safe.storage.utilities.bbox_intersection

    Typically the result of this function will be used to clip
    input layers to a common extent before processing.

    :param hazard_geo_extent: An array representing the hazard layer
        extents in the form [xmin, ymin, xmax, ymax]. It is assumed that
        the coordinates are in EPSG:4326 although currently no checks are
        made to enforce this.
    :type hazard_geo_extent: list

    :param exposure_geo_extent: An array representing the exposure layer
        extents in the form [xmin, ymin, xmax, ymax]. It is assumed that
        the coordinates are in EPSG:4326 although currently no checks are
        made to enforce this.
    :type exposure_geo_extent: list

    :param viewport_geo_extent: (optional) An array representing the
        viewport extents in the form [xmin, ymin, xmax, ymax]. It is
        assumed that the coordinates are in EPSG:4326 although currently
        no checks are made to enforce this.

        ..note:: We do minimal checking as the inasafe library takes care
        of it for us.

    :returns: An array containing an extent in the form
        [xmin, ymin, xmax, ymax]
        e.g.::
        [100.03, -1.14, 100.81, -0.73]
    :rtype: list

    :raises: Any exceptions raised by the InaSAFE library will be
        propagated.
    """

    message = tr(
        'theHazardGeoExtent or theExposureGeoExtent cannot be None.Found: '
        '/ntheHazardGeoExtent: %s /ntheExposureGeoExtent: %s' %
        (hazard_geo_extent, exposure_geo_extent))

    if (hazard_geo_extent is None) or (exposure_geo_extent is None):
        raise BoundingBoxError(message)

    # .. note:: The bbox_intersection function below assumes that
    # all inputs are in EPSG:4326
    optimal_extent = bbox_intersection(
        hazard_geo_extent, exposure_geo_extent, viewport_geo_extent)

    if optimal_extent is None:
        # Bounding boxes did not overlap
        message = tr(
            'Bounding boxes of hazard data, exposure data and viewport '
            'did not overlap, so no computation was done. Please make '
            'sure you pan to where the data is and that hazard and '
            'exposure data overlaps.')
        raise InsufficientOverlapError(message)

    return optimal_extent


def add_output_feature(
        features,
        geometry,
        affected_class,
        fields,
        original_attributes,
        target_field):
    """ Utility function to construct road features from geometry.

    Newly created features get the attributes from the original feature.

    :param features: A collection of features that the new feature will
        be added to.
    :type features: list

    :param geometry: The geometry for the new feature. If the geometry is
        multi-part, it will be exploded into several single-part features.
    :type geometry: QgsGeometry

    :param affected_class: Affected class, 0 is not affected by a range.
    :type affected_class: int

    :param fields: Fields that should be assigned to the new feature.
    :type fields: list

    :param original_attributes: Attributes for the feature before the new
        target field (see below) is added.
    :type original_attributes: list

    :param target_field: Output field used to indicate if the road segment
        is flooded.
    :type target_field: QgsField

    :returns: None
    """
    geometries = geometry.asGeometryCollection() if geometry.isMultipart() \
        else [geometry]
    for g in geometries:
        f = QgsFeature(fields)
        f.setGeometry(g)
        for attr_no, attr_val in enumerate(original_attributes):
            f.setAttribute(attr_no, attr_val)
        f.setAttribute(target_field, affected_class)
        features.append(f)


def union_geometries(geometries):
    """ Return a geometry which is union of the passed list of geometries.

    :param geometries: Geometries for the union operation.
    :type geometries: list

    :returns: union of geometries
    :rtype: QgsGeometry
    """
    if QGis.QGIS_VERSION_INT >= 20400:
        # woohoo we can use fast union (needs GEOS >= 3.3)
        return QgsGeometry.unaryUnion(geometries)
    else:
        # uhh we need to use slow iterative union
        if len(geometries) == 0:
            return QgsGeometry()
        result_geometry = QgsGeometry(geometries[0])
        for g in geometries[1:]:
            result_geometry = result_geometry.combine(g)
        return result_geometry


def buffer_points(point_layer, radii, hazard_zone_attribute, output_crs):
    """Buffer points for each point with defined radii.

    This function is used for making buffer of volcano point hazard.

    :param point_layer: A point layer to buffer.
    :type point_layer: QgsVectorLayer

    :param radii: Desired approximate radii in kilometres (must be
        monotonically ascending). Can be either one number or list of numbers
    :type radii: int, list

    :param hazard_zone_attribute: The name of the attributes representing
        hazard zone.
    :type hazard_zone_attribute: str

    :param output_crs: The output CRS.
    :type output_crs: QgsCoordinateReferenceSystem

    :return: Vector polygon layer representing circle in point layer CRS.
    :rtype: QgsVectorLayer
    """
    if not isinstance(radii, list):
        radii = [radii]

    if not is_point_layer(point_layer):
        message = (
            'Input hazard must be a vector point layer. I got %s '
            'with layer type %s' % (point_layer.name(), point_layer.type()))
        raise Exception(message)

    # Check that radii are monotonically increasing
    monotonically_increasing_flag = all(
        x < y for x, y in zip(radii, radii[1:]))
    if not monotonically_increasing_flag:
        raise RadiiException(RadiiException.suggestion)

    hazard_file_path = unique_filename(suffix='-polygon-volcano.shp')
    fields = point_layer.pendingFields()
    fields.append(QgsField(hazard_zone_attribute, QVariant.Double))
    writer = QgsVectorFileWriter(
        hazard_file_path,
        'utf-8',
        fields,
        QGis.WKBPolygon,
        output_crs,
        'ESRI Shapefile')
    input_crs = point_layer.crs()

    center = point_layer.extent().center()
    utm = None
    if output_crs.authid() == 'EPSG:4326':
        utm = QgsCoordinateReferenceSystem(
            get_utm_epsg(center.x(), center.y(), input_crs))
        transform = QgsCoordinateTransform(point_layer.crs(), utm)

    else:
        transform = QgsCoordinateTransform(point_layer.crs(), output_crs)

    for point in point_layer.getFeatures():
        geom = point.geometry()
        geom.transform(transform)

        inner_rings = None
        for radius in radii:
            attributes = point.attributes()
            # Generate circle polygon

            circle = geom.buffer(radius * 1000.0, 30)

            if inner_rings:
                circle.addRing(inner_rings)
            inner_rings = circle.asPolygon()[0]

            new_buffer = QgsFeature()

            if output_crs.authid() == 'EPSG:4326':
                circle.transform(QgsCoordinateTransform(utm, output_crs))

            new_buffer.setGeometry(circle)
            attributes.append(radius)
            new_buffer.setAttributes(attributes)

            writer.addFeature(new_buffer)

    del writer
    vector_layer = QgsVectorLayer(hazard_file_path, 'Polygons', 'ogr')

    keyword_io = KeywordIO()
    try:
        keywords = keyword_io.read_keywords(point_layer)
        keyword_io.write_keywords(vector_layer, keywords)
    except NoKeywordsFoundError:
        pass
    return vector_layer
