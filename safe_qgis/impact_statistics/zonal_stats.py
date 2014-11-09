# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **Zonal Stats.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '17/10/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import struct
import logging

import numpy
from osgeo import gdal, ogr, osr

from PyQt4.QtCore import QCoreApplication
from qgis.core import (
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPoint)

from safe_qgis.utilities.utilities import (
    is_raster_layer,
    is_polygon_layer)
from safe_qgis.exceptions import InvalidParameterError, InvalidGeometryError

LOGGER = logging.getLogger('InaSAFE')


def tr(text):
    """We define a tr() alias here since the utilities implementation.

     The code below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str

    :returns: Translated version of the given string if available,
        otherwise the original string.
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('zonal_stats', text)


def calculate_zonal_stats(raster_layer, polygon_layer):
    """Calculate zonal statics given two layers.

    :param raster_layer: A QGIS raster layer.
    :type raster_layer: QgsRasterLayer, QgsMapLayer

    :param polygon_layer: A QGIS vector layer containing polygons.
    :type polygon_layer: QgsVectorLayer, QgsMapLayer

    :returns: A data structure containing sum, mean, min, max,
        count of raster values for each polygonal area.
    :rtype: dict

    :raises: InvalidParameterError, InvalidGeometryError

    Note:
        * InvalidParameterError if incorrect inputs are received.
        * InvalidGeometryError if none geometry is found during calculations.
        * Any other exceptions are propagated.

    Example of output data structure:

        { 1: {'sum': 10, 'count': 20, 'min': 1, 'max': 4, 'mean': 2},
          2: {'sum': 10, 'count': 20, 'min': 1, 'max': 4, 'mean': 2},
          3 {'sum': 10, 'count': 20, 'min': 1, 'max': 4, 'mean': 2}}

    The key in the outer dict is the feature id

    .. note:: This is a python port of the zonal stats implementation in QGIS
        . See https://github.com/qgis/Quantum-GIS/blob/master/src/analysis/
        vector/qgszonalstatistics.cpp

    .. note:: Currently not projection checks are made to ensure that both
        layers are in the same CRS - we assume they are.

    """
    if not is_polygon_layer(polygon_layer):
        raise InvalidParameterError(tr(
            'Zonal stats needs a polygon layer in order to compute '
            'statistics.'))
    if not is_raster_layer(raster_layer):
        raise InvalidParameterError(tr(
            'Zonal stats needs a raster layer in order to compute statistics.'
        ))
    LOGGER.debug('Calculating zonal stats for:')
    LOGGER.debug('Raster: %s' % raster_layer.source())
    LOGGER.debug('Vector: %s' % polygon_layer.source())
    results = {}
    raster_source = raster_layer.source()
    feature_id = gdal.Open(str(raster_source), gdal.GA_ReadOnly)
    geo_transform = feature_id.GetGeoTransform()
    columns = feature_id.RasterXSize
    rows = feature_id.RasterYSize
    # Get first band.
    band = feature_id.GetRasterBand(1)
    no_data = band.GetNoDataValue()
    # print 'No data %s' % no_data
    cell_size_x = geo_transform[1]
    if cell_size_x < 0:
        cell_size_x = -cell_size_x
    cell_size_y = geo_transform[5]
    if cell_size_y < 0:
        cell_size_y = -cell_size_y
    raster_box = QgsRectangle(
        geo_transform[0],
        geo_transform[3] - (cell_size_y * rows),
        geo_transform[0] + (cell_size_x * columns),
        geo_transform[3])

    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    raster_geometry = QgsGeometry.fromRect(raster_box)

    # Get vector layer
    provider = polygon_layer.dataProvider()
    if provider is None:
        message = tr(
            'Could not obtain data provider from layer "%s"') % (
                polygon_layer.source())
        raise Exception(message)

    request = QgsFeatureRequest()
    crs = osr.SpatialReference()
    crs.ImportFromProj4(str(polygon_layer.crs().toProj4()))

    count = 0
    for myFeature in provider.getFeatures(request):
        geometry = myFeature.geometry()
        if geometry is None:
            message = tr(
                'Feature %d has no geometry or geometry is invalid') % (
                    myFeature.id())
            raise InvalidGeometryError(message)

        count += 1
        feature_box = geometry.boundingBox().intersect(raster_box)
        print 'NEW AGGR: %s' % myFeature.id()

        # print 'Raster Box: %s' % raster_box.asWktCoordinates()
        # print 'Feature Box: %s' % feature_box.asWktCoordinates()

        offset_x, offset_y, cells_x, cells_y = intersection_box(
            raster_box, feature_box, cell_size_x, cell_size_y)

        # If the poly does not intersect the raster just continue
        if None in [offset_x, offset_y, cells_x, cells_y]:
            continue

        # avoid access to cells outside of the raster (may occur because of
        # rounding)
        if (offset_x + cells_x) > columns:
            offset_x = columns - offset_x

        if (offset_y + cells_y) > rows:
            cells_y = rows - offset_y

        intersected_geometry = raster_geometry.intersection(geometry)
        geometry_sum, count = numpy_stats(
            band,
            intersected_geometry,
            geo_transform,
            no_data,
            crs)

        if count <= 1:
            # The cell resolution is probably larger than the polygon area.
            # We switch to precise pixel - polygon intersection in this case
            geometry_sum, count = precise_stats(
                band,
                geometry,
                offset_x,
                offset_y,
                cells_x,
                cells_y,
                cell_size_x,
                cell_size_y,
                raster_box,
                no_data)
            # print geometry_sum, count

        if count == 0:
            mean = 0
        else:
            mean = geometry_sum / count

        results[myFeature.id()] = {
            'sum': geometry_sum,
            'count': count,
            'mean': mean}

    # noinspection PyUnusedLocal
    feature_id = None  # Close
    return results


def intersection_box(
        raster_box,
        feature_box,
        cell_size_x,
        cell_size_y):
    """Calculate cell offset and distances for the intersecting bbox.

    :param raster_box: Box defining the extents of the raster.
    :type raster_box: QgsRectangle

    :param feature_box: Bounding box for the feature.
    :type feature_box: QgsRectangle

    :param cell_size_x: Size in the x direction of a single cell.
    :type cell_size_x: float

    :param cell_size_y: Size in the y direction of a single cell.
    :type cell_size_y: float

    :returns: Offsets in the x and y directions, and number of cells in the x
        and y directions.
    :rtype: (int, int, int, int)
    """

    # get intersecting bbox
    intersected_box = feature_box.intersect(raster_box)
    # print 'Intersected Box: %s' % intersected_box.asWktCoordinates()
    if intersected_box.isEmpty():
        return None, None, None, None

    # get offset in pixels in x- and y- direction
    offset_x = intersected_box.xMinimum() - raster_box.xMinimum()
    offset_x /= cell_size_x
    offset_x = int(offset_x)
    offset_y = raster_box.yMaximum() - intersected_box.yMaximum()
    offset_y /= cell_size_y
    offset_y = int(offset_y)

    max_column = intersected_box.xMaximum() - raster_box.xMinimum()
    max_column /= cell_size_x
    # Round up to the next cell if the bbox is not on an exact pixel boundary
    if max_column > int(max_column):
        max_column = int(max_column) + 1
    else:
        max_column = int(max_column)

    max_row = raster_box.yMaximum() - intersected_box.yMinimum()
    max_row /= cell_size_y
    # Round up to the next cell if the bbox is not on an exact pixel boundary
    if max_row > int(max_row):
        max_row = int(max_row) + 1
    else:
        max_row = int(max_row)

    cells_x = max_column - offset_x
    cells_y = max_row - offset_y

    LOGGER.debug(
        'Pixel box: W: %s H: %s Offset Left: %s Offset Bottom: %s' % (
            cells_x, cells_y, offset_x, offset_y
        ))
    return offset_x, offset_y, cells_x, cells_y


def centroid_intersection_stats(
        band,
        geometry,
        pixel_offset_x,
        pixel_offset_y,
        cells_x,
        cells_y,
        cell_size_x,
        cell_size_y,
        raster_box,
        no_data):
    """Stats where centroid of each cell must intersect the polygon.

    :param band: A valid band from a raster layer.
    :type band: GDALRasterBand

    :param geometry: A valid polygon geometry.
    :type geometry: QgsGeometry

    :param pixel_offset_x: Left offset for raster window.
    :type pixel_offset_x: int

    :param pixel_offset_y: Offset from bottom for raster window.
    :type pixel_offset_y: int

    :param cells_x: Width of the raster window.
    :type cells_x: int

    :param cells_y: Height of the raster window.
    :type cells_y: int

    :param cell_size_x: Size in the x direction of a single cell.
    :type cell_size_x: float

    :param cell_size_y: Size in the y direction of a single cell.
    :type cell_size_y: float

    :param raster_box: Box defining the extents of the raster.
    :type raster_box: QgsRectangle

    :param no_data: Value for no data in the raster.
    :type no_data: int, float

    :returns: Sum, Count - sum of the values of all pixels and the count of
        pixels that intersect with the geometry.
    :rtype: (float, int)
    """
    cell_center_x = (
        raster_box.yMaximum() - pixel_offset_y * cell_size_y -
        cell_size_y / 2)
    count = 0
    geometry_sum = 0
    buffer_x_size = cells_x
    buffer_y_size = 1  # read in a single row at a time
    cells_to_read_x = cells_x
    cells_to_read_y = 1  # read in a single row at a time

    for i in range(0, cells_y):
        scanline = band.ReadRaster(
            pixel_offset_x,
            pixel_offset_y + i,
            cells_to_read_x,
            cells_to_read_y,
            buffer_x_size,
            buffer_y_size,
            gdal.GDT_Float32)
        # Note that the returned scanline is of type string, and contains
        # xsize*4 bytes of raw binary floating point data. This can be
        # converted to Python values using the struct module from the standard
        # library:
        values = struct.unpack('f' * cells_to_read_x, scanline)
        # print values
        if values is None:
            continue

        cell_center_y = (
            raster_box.xMinimum() +
            pixel_offset_x * cell_size_x +
            cell_size_x / 2)

        for j in range(0, cells_x):
            point = QgsPoint(cell_center_y, cell_center_x)
            if geometry.contains(point):
                if values[j] != no_data:
                    geometry_sum += values[j]
                    count += 1

            cell_center_y += cell_size_x
        # Move down one row
        cell_center_x -= cell_size_y

    return geometry_sum, count


# noinspection PyArgumentList
def precise_stats(
        band,
        geometry,
        pixel_offset_x,
        pixel_offset_y,
        cells_x,
        cells_y,
        cell_size_x,
        cell_size_y,
        raster_box,
        no_data):
    """Weighted pixel sum for polygon based on only intersecting parts.

    :param band: A valid band from a raster layer.
    :type band: GDALRasterBand

    :param geometry: A valid polygon geometry.
    :type geometry: QgsGeometry

    :param pixel_offset_x: Left offset for raster window.
    :type pixel_offset_x: int

    :param pixel_offset_y: Offset from bottom for raster window.
    :type pixel_offset_y: int

    :param cells_x: Width of the raster window.
    :type cells_x: int

    :param cells_y: Height of the raster window.
    :type cells_y: int

    :param cell_size_x: Size in the x direction of a single cell.
    :type cell_size_x: float

    :param cell_size_y: Size in the y direction of a single cell.
    :type cell_size_y: float

    :param raster_box: Box defining the extents of the raster.
    :type raster_box: QgsRectangle

    :param no_data: Value for no data in the raster.
    :type no_data: int, float

    :returns: Sum, Count - sum of the values of all pixels and the count of
        pixels that intersect with the geometry.
    :rtype: (float, int)
    """

    current_y = (
        raster_box.yMaximum() - pixel_offset_y * cell_size_y - cell_size_y / 2)

    half_cell_size_x = cell_size_x / 2.0
    half_cell_size_y = cell_size_y / 2.0
    pixel_area = cell_size_x * cell_size_y
    cells_to_read_x = cells_x
    cells_to_read_y = 1  # read in a single row at a time
    buffer_size_x = 1
    buffer_size_y = 1
    count = 0
    geometry_sum = 0.0

    for row in range(0, cells_y):
        current_x = (
            raster_box.xMinimum() + cell_size_x / 2.0 +
            pixel_offset_x * cell_size_x)
        # noinspection PyArgumentList
        for col in range(0, cells_x):
            # Read a single pixel
            scanline = band.ReadRaster(
                pixel_offset_x + col,
                pixel_offset_y + row,
                cells_to_read_x,
                cells_to_read_y,
                buffer_size_x,
                buffer_size_y,
                gdal.GDT_Float32)
            # Note that the returned scanline is of type string, and contains
            # xsize*4 bytes of raw binary floating point data. This can be
            # converted to Python values using the struct module from the
            # standard library:
            if scanline != '':
                values = struct.unpack('f', scanline)  # tuple returned
                value = values[0]
            else:
                continue

            if value == no_data:
                continue
            # noinspection PyCallByClass,PyTypeChecker
            pixel_geometry = QgsGeometry.fromRect(
                QgsRectangle(
                    current_x - half_cell_size_x,
                    current_y - half_cell_size_y,
                    current_x + half_cell_size_x,
                    current_y + half_cell_size_y))
            if pixel_geometry:
                intersection_geometry = pixel_geometry.intersection(
                    geometry)
                if intersection_geometry:
                    intersection_area = intersection_geometry.area()
                    if intersection_area >= 0.0:
                        weight = intersection_area / pixel_area
                        count += weight
                        geometry_sum += value * weight
            current_x += cell_size_y
        current_y -= cells_y
    return geometry_sum, count


def map_to_pixel(x_coordinate, y_coordinate, geo_transform):
    """Convert map coordinates to pixel coordinates.

    :param x_coordinate: Input map X coordinate.
    :type x_coordinate: float

    :param y_coordinate: Input map Y coordinate.
    :type y_coordinate: float

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :returns pixel_x, pixel_y - Output pixel coordinates
    :rtype: (int, int)
    """
    if geo_transform[2] + geo_transform[4] == 0:
        pixel_x = (x_coordinate - geo_transform[0]) / geo_transform[1]
        pixel_y = (y_coordinate - geo_transform[3]) / geo_transform[5]
    else:
        pixel_x, pixel_y = transform(
            x_coordinate, y_coordinate, inverse_transform(geo_transform))
    return int(pixel_x + 0.5), int(pixel_y + 0.5)


def pixel_to_map(pixel_x, pixel_y, geo_transform):
    """Convert pixel coordinates to map coordinates.

    :param pixel_x: Input pixel X coordinate
    :type pixel_x: float

    :param pixel_y: Input pixel Y coordinate
    :type pixel_y: float

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :returns map_x, map_y - Output map coordinates
    :rtype: (float, float)
    """
    map_x, map_y = transform(pixel_x, pixel_y, geo_transform)
    return map_x, map_y


def transform(x, y, geo_transform):
    """Apply a geo transform to coordinates.

    :param x: Input X coordinate.
    :type x: float

    :param y: Input Y coordinate
    :type y: float

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :returns output_x, output_y - Transformed X and Y coordinates
    :rtype: (float, float)
    """
    output_x = geo_transform[0] + x * geo_transform[1] + y * geo_transform[2]
    output_y = geo_transform[3] + x * geo_transform[4] + y * geo_transform[5]
    return output_x, output_y


def inverse_transform(geo_transform):
    """Invert standard 3x2 set of geo-transform coefficients.

    :param geo_transform: Geo-referencing transform from raster metadata (
        which is unaltered).
    :type geo_transform: list (six floats)

    :param geo_transform: Invert geo-referencing transform (updated) on
        success, empty list on failure.
    :type geo_transform: list (six floats or empty)
    """
    # we assume a 3rd row that is [1 0 0]
    # compute determinate
    det = (geo_transform[1] * geo_transform[5] -
           geo_transform[2] * geo_transform[4])

    if abs(det) < 0.000000000000001:
        return []

    inverse_det = 1.0 / det

    # compute adjoint and divide by determinate
    output_geo_transform = [0, 0, 0, 0, 0, 0]
    output_geo_transform[1] = geo_transform[5] * inverse_det
    output_geo_transform[4] = -geo_transform[4] * inverse_det

    output_geo_transform[2] = -geo_transform[2] * inverse_det
    output_geo_transform[5] = geo_transform[1] * inverse_det

    output_geo_transform[0] = (
        geo_transform[2] * geo_transform[3] -
        geo_transform[0] * geo_transform[5]) * inverse_det
    output_geo_transform[3] = (
        -geo_transform[1] * geo_transform[3] +
        geo_transform[0] * geo_transform[4]) * inverse_det

    return output_geo_transform


def numpy_stats(band, geometry, geo_transform, no_data, crs):
    """
    :param band: A valid band from a raster layer.
    :type band: GDALRasterBand

    :param geometry: A polygon geometry used to calculate statistics.
    :type geometry: QgsGeometry

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :param no_data: Value for no data in the raster.
    :type no_data: int, float

    :param crs: Coordinate reference system of the vector layer.
    :type crs: OGRSpatialReference

    :returns: Sum, Count - sum of the values of all pixels and the count of
        pixels that intersect with the geometry.
    :rtype: (float, int)
    """
    mem_drv = ogr.GetDriverByName('Memory')
    driver = gdal.GetDriverByName('MEM')

    geom = ogr.CreateGeometryFromWkt(str(geometry.exportToWkt()))

    bbox = geometry.boundingBox()

    x_min = bbox.xMinimum()
    x_max = bbox.xMaximum()
    y_min = bbox.yMinimum()
    y_max = bbox.yMaximum()

    start_column, start_row = map_to_pixel(x_min, y_max, geo_transform)
    end_column, end_row = map_to_pixel(x_max, y_min, geo_transform)

    width = end_column - start_column
    height = end_row - start_row

    if width == 0 or height == 0:
        return 0, 0

    src_offset = (start_column, start_row, width, height)

    src_array = band.ReadAsArray(*src_offset)

    new_geo_transform = (
        (geo_transform[0] + (src_offset[0] * geo_transform[1])),
        geo_transform[1],
        0.0,
        (geo_transform[3] + (src_offset[1] * geo_transform[5])),
        0.0,
        geo_transform[5]
    )

    # Create a temporary vector layer in memory
    mem_ds = mem_drv.CreateDataSource('out')
    mem_layer = mem_ds.CreateLayer('poly', crs, ogr.wkbPolygon)

    feat = ogr.Feature(mem_layer.GetLayerDefn())
    feat.SetGeometry(geom)
    mem_layer.CreateFeature(feat)
    feat.Destroy()

    # Rasterize it
    rasterized_ds = driver.Create('', src_offset[2], src_offset[3], 1,
                                  gdal.GDT_Byte)
    rasterized_ds.SetGeoTransform(new_geo_transform)
    gdal.RasterizeLayer(rasterized_ds, [1], mem_layer, burn_values=[1])
    rv_array = rasterized_ds.ReadAsArray()

    # Mask the source data array with our current feature
    # we take the logical_not to flip 0<->1 to get the correct mask effect
    # we also mask out no data values explicitly
    src_array = numpy.nan_to_num(src_array)
    masked = numpy.ma.MaskedArray(
        src_array,
        mask=numpy.logical_or(
            src_array == no_data,
            numpy.logical_not(rv_array)
        )
    )

    my_sum = float(masked.sum())
    my_count = int(masked.count())

    return my_sum, my_count
