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
import unittest
import sys
import os
import struct
import logging

from osgeo import gdal

from PyQt4.QtCore import QCoreApplication
from qgis.core import QGis, QgsRectangle, QgsFeature, QgsGeometry, QgsPoint

from safe_qgis.utilities.utilities import (
    getErrorMessage,
    isRasterLayer,
    isPolygonLayer)
from safe_qgis.exceptions import InvalidParameterError

LOGGER = logging.getLogger('InaSAFE')


def tr(theText):
    """We define a tr() alias here since the utilities implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences
    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('zonalstats', theText)


def calculateZonalStats(theRasterLayer, thePolygonLayer):
    """Calculate zonal statics given two layers.

    Args:
        * theRasterLayer: A QGIS raster layer.
        * theVectorLayer: A QGIS vector layer containing polygons.

    Returns:
        dict: A data structure containing sum, mean, min, max,
        count of raster values for each polygonal area.

    Raises:
        * InvalidParameterError if incorrect inputs are received.
        * Any other exceptions are propogated.

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
    if not isPolygonLayer(thePolygonLayer):
        raise InvalidParameterError(tr(
            'Zonal stats needs a polygon layer in order to compute '
            'statistics.'))
    if not isRasterLayer(theRasterLayer):
        raise InvalidParameterError(tr(
            'Zonal stats needs a raster layer in order to compute statistics.'
        ))
    LOGGER.debug('Calculating zonal stats for:')
    LOGGER.debug('Raster: %s' % theRasterLayer.source())
    LOGGER.debug('Vector: %s' % thePolygonLayer.source())
    myResults = {}
    myRasterSource = theRasterLayer.source()
    myFid = gdal.Open(str(myRasterSource), gdal.GA_ReadOnly)
    myGeoTransform = myFid.GetGeoTransform()
    myColumns = myFid.RasterXSize
    myRows = myFid.RasterYSize
    myBandCount = myFid.RasterCount
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
    myProvider = thePolygonLayer.dataProvider()
    if myProvider is None:
        myMessage = tr(
            'Could not obtain data provider from layer "%1"').arg(
                thePolygonLayer.source())
        raise Exception(myMessage)

    myFeature = QgsFeature()
    myCount = 0
    while myProvider.nextFeature(myFeature):
        myGeometry = myFeature.geometry()
        myCount += 1
        myFeatureBox = myGeometry.boundingBox()
        print 'NEW AGGR: %s' % myFeature.id()

        #print 'Raster Box: %s' % myRasterBox.asWktCoordinates()
        #print 'Feature Box: %s' % myFeatureBox.asWktCoordinates()

        myOffsetX, myOffsetY, myCellsX, myCellsY = cellInfoForBBox(
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

        mySum, myCount = statisticsFromMiddlePointTest(
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
        #print 'Sum: %s count: %s' % (mySum, myCount)

        if myCount <= 1:
            # The cell resolution is probably larger than the polygon area.
            # We switch to precise pixel - polygon intersection in this case
            mySum, myCount = statisticsFromPreciseIntersection(
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

    myFid = None  # Close
    return myResults


def cellInfoForBBox(
        theRasterBox,
        theFeatureBox,
        theCellSizeX,
        theCellSizeY,):
    """Calculate cell offset and distances for the intersecting bbox."""

    #get intersecting bbox
    myIntersectedBox = theFeatureBox.intersect(theRasterBox)
    #print 'Intersected Box: %s' % myIntersectedBox.asWktCoordinates()
    if myIntersectedBox.isEmpty():
        return None, None, None, None

    #get offset in pixels in x- and y- direction
    myOffsetX = myIntersectedBox.xMinimum() - theRasterBox.xMinimum()
    myOffsetX = myOffsetX / theCellSizeX
    myOffsetX = int(myOffsetX)
    myOffsetY = theRasterBox.yMaximum() - myIntersectedBox.yMaximum()
    myOffsetY = myOffsetY / theCellSizeY
    myOffsetY = int(myOffsetY)

    ##### Checked to here....offsets calculate correctly ##########

    myMaxColumn = myIntersectedBox.xMaximum() - theRasterBox.xMinimum()
    myMaxColumn = myMaxColumn / theCellSizeX
    # Round up to the next cell if the bbox is not on an exact pixel boundary
    if myMaxColumn > int(myMaxColumn):
        myMaxColumn = int(myMaxColumn) + 1
    else:
        myMaxColumn = int(myMaxColumn)

    myMaxRow = theRasterBox.yMaximum() - myIntersectedBox.yMinimum()
    myMaxRow = myMaxRow / theCellSizeY
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


def statisticsFromMiddlePointTest(
        theBand,
        theGeometry,
        thePixelOffsetX,
        thePixelOffsetY,
        theCellsX,
        theCellsY,
        theCellSizeX,
        theCellSizeY,
        theRasterBox,
        theNoData):
    """Stats where centroid of each cell must intersect the polygon.

    Args:
        * theBand GDALRasterBand - a valid band from a raster layer.
        * theGeometry QgsGeometry - a valid polygon geometry.
        * thePixelOffsetX int - left offset for raster window.
        * thePixelOffsetY int - offset from bottom for raster window.
        * theCellsX int - width of the raster window.
        * theCellsY int - height of the raster window.
        * theCellSizeX -
        * theCellSizeY,
        * theRasterBox,
        * theNoData

    """
    myCellCenterX = (
        theRasterBox.yMaximum() - thePixelOffsetY * theCellSizeY -
        theCellSizeY / 2)
    myCount = 0
    mySum = 0
    myBufferXSize = theCellsX
    myBufferYSize = 1  # read in a single row at a time
    myCellsToReadX = theCellsX
    myCellsToReadY = 1  # read in a single row at a time

    for i in range(0, theCellsY):
        myScanline = theBand.ReadRaster(
            thePixelOffsetX,
            thePixelOffsetY + i,
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
            theRasterBox.xMinimum() +
            thePixelOffsetX * theCellSizeX +
            theCellSizeX / 2)

        for j in range(0, theCellsX):
            myPoint = QgsPoint(myCellCenterY, myCellCenterX)
            if theGeometry.contains(myPoint):
                if myValues[j] != theNoData:
                    mySum += myValues[j]
                    myCount += 1

            myCellCenterY += theCellSizeX
        # Move down one row
        myCellCenterX -= theCellSizeY

    return mySum, myCount


def statisticsFromPreciseIntersection(
        theBand,
        theGeometry,
        thePixelOffsetX,
        thePixelOffsetY,
        theCellsX,
        theCellsY,
        theCellSizeX,
        theCellSizeY,
        theRasterBox,
        theNoData):
    myCurrentY = (
        theRasterBox.yMaximum() - thePixelOffsetY *
        theCellSizeY - theCellSizeY / 2)

    myHalfCellSizeX = theCellSizeX / 2.0
    myHalfCellsSizeY = theCellSizeY / 2.0
    myPixelArea = theCellSizeX * theCellSizeY
    myCellsToReadX = theCellsX
    myCellsToReadY = 1  # read in a single row at a time
    myBufferXSize = 1
    myBufferYSize = 1
    myCount = 0
    mySum = 0.0

    for row in range(0, theCellsY):
        myCurrentX = (
            theRasterBox.xMinimum() + theCellSizeX / 2.0 +
            thePixelOffsetX * theCellSizeX)
        for col in range(0, theCellsX):
            # Read a single pixel
            myScanline = theBand.ReadRaster(
                thePixelOffsetX + col,
                thePixelOffsetY + row,
                myCellsToReadX,
                myCellsToReadY,
                myBufferXSize,
                myBufferYSize,
                gdal.GDT_Float32)
            # Note that the returned scanline is of type string, and contains
            # xsize*4 bytes of raw binary floating point data. This can be
            # converted to Python values using the struct module from the
            # standard library:
            #print myScanline
            if myScanline != '':
                myValues = struct.unpack('f', myScanline)  # tuple returned
                myValue = myValues[0]
            else:
                continue

            if myValue == theNoData:
                #print 'myValue is nodata (%s)' % theNoData
                continue
            #print 'Value of cell in precise intersection: %s' % myValue
            # noinspection PyCallByClass,PyTypeChecker
            myPixelGeometry = QgsGeometry.fromRect(
                QgsRectangle(
                    myCurrentX - myHalfCellSizeX,
                    myCurrentY - myHalfCellsSizeY,
                    myCurrentX + myHalfCellSizeX,
                    myCurrentY + myHalfCellsSizeY))
            if myPixelGeometry:
                myIntersectionGeometry = myPixelGeometry.intersection(
                    theGeometry)
                if myIntersectionGeometry:
                    myIntersectionArea = myIntersectionGeometry.area()
                    #print 'Intersection Area: %s' % myIntersectionArea
                    if myIntersectionArea >= 0.0:
                        myWeight = myIntersectionArea / myPixelArea
                        #print 'Weight: %s' % myWeight
                        myCount += myWeight
                        #print 'myCount: %s' % myCount
                        mySum += myValue * myWeight
                        #print 'myValue: %s' % myValue
            myCurrentX += theCellSizeY
        myCurrentY -= theCellsY
    return mySum, myCount
