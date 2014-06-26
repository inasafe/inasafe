# coding=utf-8
"""**Convert QgsRasterLayer to QgsVectorLayer**
"""
__author__ = 'Dmitry Kolesov <kolesov.dm@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '14/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.common.utilities import unique_filename
from safe.storage.raster import qgis_imported
from safe.common.gdal_ogr_tools import polygonize_thresholds
from safe.common.exceptions import GetDataError

if qgis_imported:   # Import QgsRasterLayer if qgis is available
    # noinspection PyPackageRequirements
    from PyQt4.QtCore import QVariant
    from qgis.core import (
        QgsRasterLayer,
        QgsField,
        QgsVectorLayer,
        QgsFeature,
        QgsPoint,
        QgsGeometry,
        QgsRasterFileWriter,
        QgsRasterPipe
    )

from qgis_vector_tools import (
    union_geometry,
    points_to_rectangles
)


def _get_pixel_coordinates(extent, width, height, row, col):
    """Pixel to coordinates transformation

    :param extent: Geotransformation parameter: extent
    :type extent: QgsRectangle

    :param width: Geotransformation parameter: horizontal raster size
    :type width: Int

    :param height: Geotransformation parameter: vertical raster size
    :type height: Int

    :param col: Input x pixel coordinate
    :type col: Int

    :param row: Input y pixel coordinate
    :type row: Int

    :returns: output_x,output_y Output coordinates
    :rtype: (double, double)
    """
    # pylint: disable=
    x_minimum = extent.xMinimum()
    y_maximum = extent.yMaximum()
    x_resolution = (extent.xMaximum() - extent.xMinimum()) / width
    y_resolution = (extent.yMaximum() - extent.yMinimum()) / height

    output_x = x_minimum + col * x_resolution
    output_y = y_maximum - row * y_resolution
    return output_x, output_y


def pixels_to_points(
        raster,
        threshold_min=0.0,
        threshold_max=float('inf'),
        field_name='value'):
    """
    Convert raster to points.

    Areas (pixels) with threshold_min < pixel_values < threshold_max will be
    converted to point layer.

    :param raster: Raster layer
    :type raster: QgsRasterLayer

    :param threshold_min: Value that splits raster to flooded or not flooded.
    :type threshold_min: float

    :param threshold_max: Value that splits raster to flooded or not flooded.
    :type threshold_max: float

    :param field_name: Field name to store pixel value.
    :type field_name:  string

    :returns: Point layer of pixels
    :rtype: QgsVectorLayer
    """
    if raster.bandCount() != 1:
        msg = "Current version allows using of one-band raster only"
        raise NotImplementedError(msg)

    extent = raster.extent()
    width, height = raster.width(), raster.height()
    provider = raster.dataProvider()
    block = provider.block(1, extent, width, height)

    # Create points
    crs = raster.crs().toWkt()
    point_layer = QgsVectorLayer('Point?crs=' + crs, 'pixels', 'memory')

    point_provider = point_layer.dataProvider()
    point_provider.addAttributes([QgsField(field_name, QVariant.Double)])
    field_index = point_provider.fieldNameIndex(field_name)
    attribute_count = 1

    point_layer.startEditing()
    for row in range(height):
        for col in range(width):
            value = block.value(row, col)
            x, y = _get_pixel_coordinates(extent, width, height, row, col)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            geom = QgsGeometry.fromPoint(QgsPoint(x, y))
            if threshold_min < value < threshold_max:
                feature = QgsFeature()
                feature.initAttributes(attribute_count)
                feature.setAttribute(field_index, value)
                feature.setGeometry(geom)
                _ = point_layer.dataProvider().addFeatures([feature])
    point_layer.commitChanges()
    return point_layer


def polygonize(raster, threshold_min=0.0, threshold_max=float('inf')):
    """Raster polygonizer.

    Function to polygonize raster. Areas (pixels) with threshold_min <
    pixel_values < threshold_max will be converted to polygons.

    :param raster: Raster layer
    :type raster: QgsRasterLayer

    :param threshold_min: Value that splits raster to flooded or not flooded.
    :type threshold_min: float

    :param threshold_max: Value that splits raster to flooded or not flooded.
    :type threshold_max: float

    :returns: Polygonal geometry
    :rtype: QgsGeometry
    """
    points = pixels_to_points(raster, threshold_min, threshold_max)
    polygons = points_to_rectangles(
        points,
        raster.rasterUnitsPerPixelX(),
        raster.rasterUnitsPerPixelY())
    polygons = union_geometry(polygons)
    return polygons


def clip_raster(raster, column_count, row_count, output_extent):
    """Clip raster to specified extent, width and height.

    Note there is similar utility in safe_qgis.utilities.clipper, but it uses
    gdal whereas this one uses native QGIS.

    :param raster: Raster
    :type raster: QgsRasterLayer

    :param column_count: Desired width in pixels of new raster
    :type column_count: Int

    :param row_count: Desired height in pixels of new raster
    :type row_count: Int

    :param output_extent: Extent of the clipped region
    :type output_extent: QgsRectangle

    :returns: Clipped region of the raster
    :rtype: QgsRasterLayer
    """
    provider = raster.dataProvider()
    pipe = QgsRasterPipe()
    pipe.set(provider.clone())

    base_name = unique_filename()
    file_name = base_name + '.tif'
    file_writer = QgsRasterFileWriter(file_name)
    file_writer.writeRaster(
        pipe,
        column_count,
        row_count,
        output_extent,
        raster.crs())

    return QgsRasterLayer(file_name, 'clipped_raster')


def polygonize_gdal(
        raster,
        threshold_min=0.0,
        threshold_max=float('inf')):
    """
    Function to polygonize raster. Areas (pixels) with threshold_min <
    pixel_values < threshold_max will be converted to polygons.

    :param raster:  Raster layer
    :type raster: QgsRasterLayer

    :param threshold_min: Value that splits raster to flooded or not flooded.
    :type threshold_min: float

    :param threshold_max: Value that splits raster to flooded or not flooded.
    :type threshold_max: float

    :returns: Polygonal geometry
    :rtype: QgsGeometry
    """

    #save qgis raster to disk
    base_name = unique_filename()
    file_name = base_name + '.tif'
    file_writer = QgsRasterFileWriter(file_name)
    pipe = QgsRasterPipe()
    provider = raster.dataProvider()
    if not pipe.set(provider.clone()):
        msg = "Cannot set pipe provider"
        raise GetDataError(msg)
    file_writer.writeRaster(
        pipe,
        provider.xSize(),
        provider.ySize(),
        provider.extent(),
        provider.crs())

    (inside_file_name, inside_layer_name, outside_file_name,
        outside_layer_name) = \
        polygonize_thresholds(file_name, threshold_min, threshold_max)
    inside_layer = \
        QgsVectorLayer(inside_file_name, inside_layer_name, 'ogr')
    outside_layer = \
        QgsVectorLayer(outside_file_name, outside_layer_name, 'ogr')
    if inside_layer.featureCount() == 0:
        return None, None
    else:
        return inside_layer, outside_layer
