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

from osgeo import gdal

from PyQt4.QtCore import QCoreApplication
from qgis.core import QGis, QgsRectangle, QgsFeature, QgsGeometry, QgsPoint

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe_qgis.utilities import getErrorMessage, isRasterLayer, isPolygonLayer
from safe_qgis.exceptions import InvalidParameterError


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
    print os.path
    if not isPolygonLayer(thePolygonLayer):
        raise InvalidParameterError(tr(
            'Zonal stats needs a polygon layer in order to compute '
            'statistics.'))
    if not isRasterLayer(theRasterLayer):
        raise InvalidParameterError(tr(
            'Zonal stats needs a raster layer in order to compute statistics.'
        ))
    myRasterSource = theRasterLayer.source()
    myFid = gdal.Open(str(myRasterSource), gdal.GA_ReadOnly)
    myGeoTransform = myFid.GetGeoTransform()
    myColumns = myFid.RasterXSize
    myRows = myFid.RasterYSize
    myBandCount = myFid.RasterCount
    # Get first band.
    myBand = myFid.GetRasterBand(1)
    myNoData = myBand.GetNoDataValue()
    print 'No data %s' % myNoData
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
        # Next line is to resolve a wierd issue on OSX where
        # geometry comes back as none all the time when testing
        # Simply accessing the attribute map seems to fix it
        # 9 times out of 10
        print myFeature.attributeMap()
        myGeometry = myFeature.geometry()
        myCount += 1
        myFeatureBox = myGeometry.boundingBox()

        print 'Raster Box: %s' % myRasterBox.asWktCoordinates()
        print 'Feature Box: %s' % myFeatureBox.asWktCoordinates()

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
        print mySum, myCount

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

        if myCount == 0:
            myMean = 0
        else:
            myMean = mySum / myCount

    myFid = None  # Close


def cellInfoForBBox(
        theRasterBox,
        theFeatureBox,
        theCellSizeX,
        theCellSizeY,):
    """Calculate cell offset and distances for the intersecting bbox."""

    #get intersecting bbox
    myIntersectedBox = theFeatureBox.intersect(theRasterBox)
    print 'Intersected Box: %s' % myIntersectedBox.asWktCoordinates()
    if myIntersectedBox.isEmpty():
        return None, None, None, None

    #get offset in pixels in x- and y- direction
    myOffsetX = myIntersectedBox.xMinimum() - theRasterBox.xMinimum()
    myOffsetX = myOffsetX / theCellSizeX
    myOffsetX = int(myOffsetX)
    myOffsetY = theRasterBox.yMaximum() - myIntersectedBox.yMaximum()
    myOffsetY = myOffsetY / theCellSizeY
    myOffsetY = int(myOffsetY)

    myMaxColumn = myIntersectedBox.xMaximum() - theRasterBox.xMinimum()
    myMaxColumn = myMaxColumn / theCellSizeX
    myMaxColumn = int(myMaxColumn) + 1

    myMaxRow = theRasterBox.yMaximum() - myIntersectedBox.yMinimum()
    myMaxRow = myMaxRow / theCellSizeY
    myMaxRow = int(myMaxRow) + 1

    myCellsX = myMaxColumn - myOffsetX
    myCellsY = myMaxRow - myOffsetY

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
        print myValues
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

"""








void QgsZonalStatistics::statisticsFromPreciseIntersection( void* band, QgsGeometry* poly, int pixelOffsetX,
    int pixelOffsetY, int nCellsX, int nCellsY, double cellSizeX, double cellSizeY, const QgsRectangle& rasterBBox, double& sum, double& count )
{
  sum = 0;
  count = 0;
  double currentY = rasterBBox.yMaximum() - pixelOffsetY * cellSizeY - cellSizeY / 2;
  float* pixelData = ( float * ) CPLMalloc( sizeof( float ) );
  QgsGeometry* pixelRectGeometry = 0;

  double hCellSizeX = cellSizeX / 2.0;
  double hCellSizeY = cellSizeY / 2.0;
  double pixelArea = cellSizeX * cellSizeY;
  double weight = 0;

  for ( int row = 0; row < nCellsY; ++row )
  {
    double currentX = rasterBBox.xMinimum() + cellSizeX / 2.0 + pixelOffsetX * cellSizeX;
    for ( int col = 0; col < nCellsX; ++col )
    {
      GDALRasterIO( band, GF_Read, pixelOffsetX + col, pixelOffsetY + row, nCellsX, 1, pixelData, 1, 1, GDT_Float32, 0, 0 );
      pixelRectGeometry = QgsGeometry::fromRect( QgsRectangle( currentX - hCellSizeX, currentY - hCellSizeY, currentX + hCellSizeX, currentY + hCellSizeY ) );
      if ( pixelRectGeometry )
      {
        //intersection
        QgsGeometry *intersectGeometry = pixelRectGeometry->intersection( poly );
        if ( intersectGeometry )
        {
          double intersectionArea = intersectGeometry->area();
          if ( intersectionArea >= 0.0 )
          {
            weight = intersectionArea / pixelArea;
            count += weight;
            sum += *pixelData * weight;
          }
          delete intersectGeometry;
        }
      }
      currentX += cellSizeX;
    }
    currentY -= cellSizeY;
  }
  CPLFree( pixelData );
}
"""
