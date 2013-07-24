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
from osgeo import gdal

from PyQt4.QtCore import QCoreApplication
from qgis.core import QgsRectangle, QgsFeature, QgsGeometry, QgsPoint

from safe_qgis.utilities.utilities import (
    is_raster_layer,
    is_polygon_layer)
from safe_qgis.exceptions import InvalidParameterError, InvalidGeometryError

LOGGER = logging.getLogger('InaSAFE')


def tr(theText):
    """We define a tr() alias here since the utilities implementation.

     The code below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param theText: String to be translated
    :type theText: str

    :returns: Translated version of the given string if available,
        otherwise the original string.
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('zonal_stats', theText)


def calculate_zonal_stats(raster_layer, polygon_layer):
    """Calculate zonal statics given two layers.

    :param raster_layer: A QGIS raster layer.
    :type raster_layer: QgsRasterLayer

    :param polygon_layer: A QGIS vector layer containing polygons.
    :type polygon_layer: QgsVectorLayer

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
    myResults = {}
    myRasterSource = raster_layer.source()
    myFid = gdal.Open(str(myRasterSource), gdal.GA_ReadOnly)
    myGeoTransform = myFid.GetGeoTransform()
    myColumns = myFid.RasterXSize
    myRows = myFid.RasterYSize
    #myBandCount = myFid.RasterCount
    # Get first band.
    myBand = myFid.GetRasterBand(1)
    myNoData = myBand.GetNoDataValue()
    #print 'No data %s' % myNoData
    myCellSizeX = myGeoTransform[1]
    if myCellSizeX < 0:
        myCellSizeX = -myCellSizeX
    myCellSizeY = myGeoTransform[5]
    if myCellSizeY < 0:
        myCellSizeY = -myCellSizeY
    myRasterBox = QgsRectangle(
        myGeoTransform[0],
        myGeoTransform[3] - (myCellSizeY * myRows),
        myGeoTransform[0] + (myCellSizeX * myColumns),
        myGeoTransform[3])

    # Get vector layer
    myProvider = polygon_layer.dataProvider()
    if myProvider is None:
        myMessage = tr(
            'Could not obtain data provider from layer "%1"').arg(
                polygon_layer.source())
        raise Exception(myMessage)

    myFeature = QgsFeature()
    myCount = 0
    myProvider.rewind()
    myProvider.select([])
    while myProvider.nextFeature(myFeature):
        myGeometry = myFeature.geometry()
        if myGeometry is None:
            myMessage = tr(
                'Feature %1 has no geometry or geometry is invalid').arg(
                    myFeature.id())
            raise InvalidGeometryError(myMessage)

        myCount += 1
        myFeatureBox = myGeometry.boundingBox().intersect(myRasterBox)
        print 'NEW AGGR: %s' % myFeature.id()

        #print 'Raster Box: %s' % myRasterBox.asWktCoordinates()
        #print 'Feature Box: %s' % myFeatureBox.asWktCoordinates()

        myOffsetX, myOffsetY, myCellsX, myCellsY = feature_box(
            myRasterBox, myFeatureBox, myCellSizeX, myCellSizeY)

        # If the poly does not intersect the raster just continue
        if None in [myOffsetX, myOffsetY, myCellsX, myCellsY]:
            continue

        # avoid access to cells outside of the raster (may occur because of
        # rounding)
        if (myOffsetX + myCellsX) > myColumns:
            myOffsetX = myColumns - myOffsetX

        if (myOffsetY + myCellsY) > myRows:
            myCellsY = myRows - myOffsetY

        #mySum, myCount = statisticsFromMiddlePointTest(
        #    myBand,
        #    myGeometry,
        #    myOffsetX,
        #    myOffsetY,
        #    myCellsX,
        #    myCellsY,
        #    myCellSizeX,
        #    myCellSizeY,
        #    myRasterBox,
        #    myNoData)
        #print 'Sum: %s count: %s' % (mySum, myCount)

        mySum, myCount = rectangle_stats(
            myBand,
            myFeatureBox,
            myGeoTransform,
            myNoData)

        if myCount <= 1:
            # The cell resolution is probably larger than the polygon area.
            # We switch to precise pixel - polygon intersection in this case
            mySum, myCount = precise_stats(
                myBand,
                myGeometry,
                myOffsetX,
                myOffsetY,
                myCellsX,
                myCellsY,
                myCellSizeX,
                myCellSizeY,
                myRasterBox,
                myNoData)
            #print mySum, myCount

        if myCount == 0:
            myMean = 0
        else:
            myMean = mySum / myCount

        myResults[myFeature.id()] = {
            'sum': mySum,
            'count': myCount,
            'mean': myMean}

    # noinspection PyUnusedLocal
    myFid = None  # Close
    return myResults


def feature_box(
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

    #get intersecting bbox
    myIntersectedBox = feature_box.intersect(raster_box)
    #print 'Intersected Box: %s' % myIntersectedBox.asWktCoordinates()
    if myIntersectedBox.isEmpty():
        return None, None, None, None

    #get offset in pixels in x- and y- direction
    myOffsetX = myIntersectedBox.xMinimum() - raster_box.xMinimum()
    myOffsetX /= cell_size_x
    myOffsetX = int(myOffsetX)
    myOffsetY = raster_box.yMaximum() - myIntersectedBox.yMaximum()
    myOffsetY /= cell_size_y
    myOffsetY = int(myOffsetY)

    ##### Checked to here....offsets calculate correctly ##########

    myMaxColumn = myIntersectedBox.xMaximum() - raster_box.xMinimum()
    myMaxColumn /= cell_size_x
    # Round up to the next cell if the bbox is not on an exact pixel boundary
    if myMaxColumn > int(myMaxColumn):
        myMaxColumn = int(myMaxColumn) + 1
    else:
        myMaxColumn = int(myMaxColumn)

    myMaxRow = raster_box.yMaximum() - myIntersectedBox.yMinimum()
    myMaxRow /= cell_size_y
    # Round up to the next cell if the bbox is not on an exact pixel boundary
    if myMaxRow > int(myMaxRow):
        myMaxRow = int(myMaxRow) + 1
    else:
        myMaxRow = int(myMaxRow)

    myCellsX = myMaxColumn - myOffsetX
    myCellsY = myMaxRow - myOffsetY

    LOGGER.debug(
        'Pixel box: W: %s H: %s Offset Left: %s Offset Bottom: %s' % (
            myCellsX, myCellsY, myOffsetX, myOffsetY
        ))
    return myOffsetX, myOffsetY, myCellsX, myCellsY


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
    myCellCenterX = (
        raster_box.yMaximum() - pixel_offset_y * cell_size_y -
        cell_size_y / 2)
    myCount = 0
    mySum = 0
    myBufferXSize = cells_x
    myBufferYSize = 1  # read in a single row at a time
    myCellsToReadX = cells_x
    myCellsToReadY = 1  # read in a single row at a time

    for i in range(0, cells_y):
        myScanline = band.ReadRaster(
            pixel_offset_x,
            pixel_offset_y + i,
            myCellsToReadX,
            myCellsToReadY,
            myBufferXSize,
            myBufferYSize,
            gdal.GDT_Float32)
        # Note that the returned scanline is of type string, and contains
        # xsize*4 bytes of raw binary floating point data. This can be
        # converted to Python values using the struct module from the standard
        # library:
        myValues = struct.unpack('f' * myCellsToReadX, myScanline)
        #print myValues
        if myValues is None:
            continue

        myCellCenterY = (
            raster_box.xMinimum() +
            pixel_offset_x * cell_size_x +
            cell_size_x / 2)

        for j in range(0, cells_x):
            myPoint = QgsPoint(myCellCenterY, myCellCenterX)
            if geometry.contains(myPoint):
                if myValues[j] != no_data:
                    mySum += myValues[j]
                    myCount += 1

            myCellCenterY += cell_size_x
        # Move down one row
        myCellCenterX -= cell_size_y

    return mySum, myCount


def rectangle_stats(
        band,
        geometry,
        geo_transform,
        no_data):

    """Get stats for rect representing intersection of poly and raster bboxes.

    :param band: A valid band from a raster layer.
    :type band: GDALRasterBand

    :param geometry: A valid rectangle representing intersection between
         geometry bbox and raster bbox.
    :type geometry: QgsRectangle

    :param geo_transform: Georeferencing transform from raster metadata.
    :type geo_transform: list (six doubles)

    :param no_data: No data value for the raster.
    :type no_data: float, int, None

    :returns: Sum, Count - sum of the values of all pixels and the count of
        pixels that intersect with the geometry.
    :rtype: (float, int)
    """
    xMin = geometry.xMinimum()
    xMax = geometry.xMaximum()
    yMin = geometry.yMinimum()
    yMax = geometry.yMaximum()

    startCol, startRow = map_to_pixel(xMin, yMax, geo_transform)
    endCol, endRow = map_to_pixel(xMax, yMin, geo_transform)

    width = endCol - startCol
    height = endRow - startRow

    if width == 0 or height == 0:
        return 0, 0

    myScanline = band.ReadRaster(
        startCol,
        startRow,
        width,
        height,
        width,
        height,
        gdal.GDT_Float32)
    myValues = struct.unpack('f' * height * width, myScanline)
    if myValues is None:
        return 0, 0

    myArray = numpy.array(myValues)
    myMaskedArray = numpy.ma.masked_where(myArray == no_data, myArray)
    mySum = float(numpy.sum(myMaskedArray))
    myCount = myMaskedArray.size

    return mySum, myCount


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

    :param cell_size_y: Size in the y direciton of a single cell.
    :type cell_size_y: float

    :param raster_box: Box defining the extents of the raster.
    :type raster_box: QgsRectangle

    :param no_data: Value for nodata in the raster.
    :type no_data: int, float

    :returns: Sum, Count - sum of the values of all pixels and the count of
        pixels that intersect with the geometry.
    :rtype: (float, int)
    """

    myCurrentY = (
        raster_box.yMaximum() - pixel_offset_y * cell_size_y - cell_size_y / 2)

    myHalfCellSizeX = cell_size_x / 2.0
    myHalfCellsSizeY = cell_size_y / 2.0
    myPixelArea = cell_size_x * cell_size_y
    myCellsToReadX = cells_x
    myCellsToReadY = 1  # read in a single row at a time
    myBufferXSize = 1
    myBufferYSize = 1
    myCount = 0
    mySum = 0.0

    for row in range(0, cells_y):
        myCurrentX = (
            raster_box.xMinimum() + cell_size_x / 2.0 +
            pixel_offset_x * cell_size_x)
        # noinspection PyArgumentList
        for col in range(0, cells_x):
            # Read a single pixel
            myScanline = band.ReadRaster(
                pixel_offset_x + col,
                pixel_offset_y + row,
                myCellsToReadX,
                myCellsToReadY,
                myBufferXSize,
                myBufferYSize,
                gdal.GDT_Float32)
            # Note that the returned scanline is of type string, and contains
            # xsize*4 bytes of raw binary floating point data. This can be
            # converted to Python values using the struct module from the
            # standard library:
            if myScanline != '':
                myValues = struct.unpack('f', myScanline)  # tuple returned
                myValue = myValues[0]
            else:
                continue

            if myValue == no_data:
                continue
            # noinspection PyCallByClass,PyTypeChecker
            myPixelGeometry = QgsGeometry.fromRect(
                QgsRectangle(
                    myCurrentX - myHalfCellSizeX,
                    myCurrentY - myHalfCellsSizeY,
                    myCurrentX + myHalfCellSizeX,
                    myCurrentY + myHalfCellsSizeY))
            if myPixelGeometry:
                myIntersectionGeometry = myPixelGeometry.intersection(
                    geometry)
                if myIntersectionGeometry:
                    myIntersectionArea = myIntersectionGeometry.area()
                    if myIntersectionArea >= 0.0:
                        myWeight = myIntersectionArea / myPixelArea
                        myCount += myWeight
                        mySum += myValue * myWeight
            myCurrentX += cell_size_y
        myCurrentY -= cells_y
    return mySum, myCount


def map_to_pixel(x_coordinate, y_coordinate, geo_transform):
    """Convert map coordinates to pixel coordinates.

    :param x_coordinate: Input map X coordinate.
    :type x_coordinate: float

    :param y_coordinate: Input map Y coordinate.
    :type y_coordinate float

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :returns pX, pY - Output pixel coordinates
    :rtype: (int, int)
    """
    if geo_transform[2] + geo_transform[4] == 0:
        pX = (x_coordinate - geo_transform[0]) / geo_transform[1]
        pY = (y_coordinate - geo_transform[3]) / geo_transform[5]
    else:
        pX, pY = transform(
            x_coordinate, y_coordinate, inverse_transform(geo_transform))
    return int(pX + 0.5), int(pY + 0.5)


def pixel_to_map(pixel_x, pixel_y, geo_transform):
    """Convert pixel coordinates to map coordinates.

    :param pixel_x: Input pixel X coordinate
    :type pixel_x: float

    :param pixel_y: Input pixel Y coordinate
    :type pixel_y: float

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :returns mX, mY - Output map coordinates
    :rtype: (float, float)
    """
    mX, mY = transform(pixel_x, pixel_y, geo_transform)
    return mX, mY


def transform(x, y, geo_transform):
    """Apply a geo transform to coordinates.

    :param x: Input X coordinate.
    :type x: float

    :param y: Input Y coordinate
    :type y: float

    :param geo_transform: Geo-referencing transform from raster metadata.
    :type geo_transform: list (six floats)

    :returns outX, outY - Transformed X and Y coordinates
    :rtype: (float, float)
    """
    outX = geo_transform[0] + x * geo_transform[1] + y * geo_transform[2]
    outY = geo_transform[3] + x * geo_transform[4] + y * geo_transform[5]
    return outX, outY


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

    invDet = 1.0 / det

    # compute adjoint and divide by determinate
    outGeoTransform = [0, 0, 0, 0, 0, 0]
    outGeoTransform[1] = geo_transform[5] * invDet
    outGeoTransform[4] = -geo_transform[4] * invDet

    outGeoTransform[2] = -geo_transform[2] * invDet
    outGeoTransform[5] = geo_transform[1] * invDet

    outGeoTransform[0] = (geo_transform[2] * geo_transform[3] -
                          geo_transform[0] * geo_transform[5]) * invDet
    outGeoTransform[3] = (-geo_transform[1] * geo_transform[3] +
                          geo_transform[0] * geo_transform[4]) * invDet

    return outGeoTransform
