"""
Disaster risk assessment tool developed by AusAid -
  **RiabClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import shutil
from qgis.core import (QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                       QgsRectangle, QgsMapLayer, QgsFeature,
                       QgsVectorFileWriter)
from PyQt4 import QtCore
from riabexceptions import InvalidParameterException, KeywordNotFoundException
import tempfile
from subprocess import call


def getBestResolution(theHazardLayer, theExposureLayer):
    """Given two raster layers, assess them to
    see which has the better spatial resolution and
    return the better one.

    Args:

        * theHazardLayer - a valid QGIS raster layer
        * theExposureLayer - a valid QGIS raster layer

    Returns:
        QGIS raster layer which is one of the two input layers.

    Raises:
       InvalidParameterException if both of the inputs are not
       valid QGIS raster layers.

    .. note:: This function is not yet sensitive to rasters
        where the x and y dimensions of a pixel differ.

    """
    if (theHazardLayer.type() != QgsMapLayer.RasterLayer or
        not theHazardLayer.isValid()):
        msg = ('getBestResolution: Hazard layer is not a valid raster layer.')
        raise InvalidParameterException(msg)
    if (theExposureLayer.type() != QgsMapLayer.RasterLayer or
        not theExposureLayer.isValid()):
        msg = ('getBestResolution: Exposure layer is not a valid '
               'raster layer.')
        raise InvalidParameterException(msg)

    myHazardUPP = theHazardLayer.rasterUnitsPerPixel()
    myExposureUPP = theExposureLayer.rasterUnitsPerPixel()
    print "Exposure Units Per Pixel: %s" % myExposureUPP
    print "Hazard Units Per Pixel: %s" % myHazardUPP
    if myHazardUPP < myExposureUPP:
        return theHazardLayer
    else:
        return theExposureLayer


def clipLayer(theLayer, theExtent, theCellSize=None):
    """Clip a Hazard or Exposure layer to the
    extents of the current view frame.

    .. note:: Will delegate to clipVectorLayer or clipRasterLayer as needed.

    Args:

        * theLayer - a valid QGIS vector or raster layer
        * theExtent - valid QgsRectangle defining the clip extent in EPSG:4326
        * theCellSize - cell size which the layer should be resampled to.
            This argument will be ignored for vector layers and if not provided
            for a raster layer, the native raster cell size will be used.

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """
    if theLayer.type() == QgsMapLayer.VectorLayer:
        return _clipVectorLayer(theLayer, theExtent)
    else:
        return _clipRasterLayer(theLayer, theExtent, theCellSize)


def reprojectLayer(theLayer):
    """Reproject a Hazard or Exposure layer to EPSG:4326 and
       return the resulting dataset's filename. If the input
       is already in EPSG:4326, its original filename will
       simply be returned.

    .. note:: Will delegate to _reprojectVectorLayer or
              _reprojectRasterLayer as needed.

    Args:

        theLayer - a valid QGIS vector or raster layer

    Returns:
        Path to the output reprojected layer. If it is a
        generated dataset it will be placed in the
        system temp dir. If the original file is already in
        EPSG:4326, it will simply return the original
        file name.

    Raises:
       None

    """
    if theLayer.type() == QgsMapLayer.VectorLayer:
        return _reprojectVectorLayer(theLayer)
    else:
        return _reprojectRasterLayer(theLayer)


def _clipVectorLayer(layer, extent):
    """Clip a Hazard or Exposure layer to the
    extents of the current view frame. The layer must be a
    vector layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS vector layer in EPSG:4326
        * theExtent - a valid QgsRectangle defining the
                      clip extent in EPSG:4326

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """
    if not layer or not extent:
        msg = 'Layer or Extent passed to clip is None.'
        raise InvalidParameterException(msg)

    if layer.type() != QgsMapLayer.VectorLayer:
        msg = ('Expected a vector layer but received a %s.' %
                str(layer.type()))
        raise InvalidParameterException(msg)

    myFilename = tempfile.mkstemp('.shp', 'clip_',
                                  tempfile.gettempdir())[1]

    if not layer or not extent:
        msg = 'Layer or Extent passed to clip is None.'
        raise InvalidParameterException(msg)

    if layer.type() != QgsMapLayer.VectorLayer:
        msg = ('Expected a vector layer but received a %s.' %
               str(layer.type()))
        raise InvalidParameterException(msg)

    myDestinationCrs = QgsCoordinateReferenceSystem()
    myDestinationCrs.createFromEpsg(4326)
    myXForm = QgsCoordinateTransform(layer.crs(),
                                     myDestinationCrs)

    # Get the clip area in the layer's crs
    myProjectedExtent = myXForm.transformBoundingBox(extent)

    # Get vector layer
    myProvider = layer.dataProvider()
    if myProvider is None:
        msg = ('Could not obtain data provider from '
               'layer "%s"' % layer.source())
        raise Exception(msg)

    # get the layer field list, select by our extent then write to disk
    myAttributes = myProvider.attributeIndexes()
    myProvider.select(myAttributes,
                      myProjectedExtent, True, True)
    myFieldList = myProvider.fields()

    myWriter = QgsVectorFileWriter(myFilename,
                                   'UTF-8',
                                   myFieldList,
                                   layer.wkbType(),
                                   myDestinationCrs,
                                   'ESRI Shapefile')
    if myWriter.hasError() != QgsVectorFileWriter.NoError:
        msg = ('Error when creating shapefile: <br>%s<br>%s' % 
            (myFilename, myWriter.hasError()))
        raise Exception(msg)

    # Retrieve every feature with its geometry and attributes
    myFeature = QgsFeature()
    while myProvider.nextFeature(myFeature):
        myWriter.addFeature(myFeature)
    del myWriter  # Flush to disk

    copyKeywords(str(layer.source()), myFilename)

    return myFilename  # Filename of created file


def _reprojectVectorLayer(theLayer):
    """Reproject a Hazard or Exposure layer to EPSG:4326
    The layer must be a *vector* layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS vector layer

    Returns:
        Path to the output reprojected layer. The output
        will be placed in the system temp dir. If the
        original layer is already in WGS84, the original
        layer's file name is simply returned without doing
        anything.

    Raises:
       InvalidParameterException if an invalid input is
       received.

    """
    if not theLayer:
        msg = 'Layer passed for reprojection is None.'
        raise InvalidParameterException(msg)

    if theLayer.type() != QgsMapLayer.VectorLayer:
        msg = ('Expected a vector layer but received a %s.' %
               str(theLayer.type()))
        raise InvalidParameterException(msg)

    mySource = theLayer.source()
    # Get the crs of the layer so we can check if it is not yet in EPSG:4326
    # .. note:: Later we could support postgres by always writing to disk at
    #           this point.
    myCrs = theLayer.crs()
    if myCrs.epsg() is not 4326:
            # Reproject the layer to wgs84
        myFilename = tempfile.mkstemp('.shp', 'prj_',
                                tempfile.gettempdir())[1]
        myError = QgsVectorFileWriter.writeAsVectorFormat(
                                theLayer,
                                myFilename,
                                "UTF-8",
                                None,
                                "ESRI Shapefile")

    return mySource


def _clipRasterLayer(layer, extent, theCellSize=None):
    """Clip a Hazard or Exposure layer to the extents provided. The
    layer must be a raster layer or an exception will be thrown.

    .. note:: The extent *must* be in EPSG:4326.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS raster layer in EPSG:4326
        * theExtent - a valid QgsRectangle defining the clip extent
            in EPSG:4326
        * theCellSize - cell size which the layer should be resampled to.
            If not provided for a raster layer, the native raster cell
            size will be used.

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """
    if not layer or not extent:
        msg = 'Layer or Extent passed to clip is None.'
        raise InvalidParameterException(msg)

    if layer.type() != QgsMapLayer.RasterLayer:
        msg = ('Expected a raster layer but received a %s.' %
               str(layer.type()))
        raise InvalidParameterException(msg)

    # Get the crs of the layer so we can check that it is in EPSG:4326
    myCrs = layer.crs()
    if myCrs.epsg() != 4326:
        msg = ('Expected a raster layer in EPSG:4326 but received one'
               ' in EPSG:%s.' % myCrs.epsg())
        raise InvalidParameterException(msg)

    myWorkingLayer = layer.source()
    # resample the file first if needed to the required pixel size
    myCellSize = layer.rasterUnitsPerPixel()
    if myCellSize != theCellSize and theCellSize is not None:
        # ok we have to resample
        myFilename = tempfile.mkstemp('.tif', 'rsmpl_',
                                    tempfile.gettempdir())[1]
        myCommand = ('gdalwarp -tr %f %f -of GTiff '
                 '%s %s' % (theCellSize,
                            theCellSize,
                            myWorkingLayer,
                            myFilename))
        #print 'Command: ', myCommand
        myResult = call(myCommand, shell=True)
        myWorkingLayer = myFilename
    # ok myWorking layer now has the original or resampled file
    # which we can go on to clip....
    myFilename = tempfile.mkstemp('.tif', 'clip_',
                                    tempfile.gettempdir())[1]
    myCommand = ('gdal_translate -projwin %f %f %f %f -of GTiff '
                 '%s %s' % (extent.xMinimum(),
                            extent.yMaximum(),
                            extent.xMaximum(),
                            extent.yMinimum(),
                            myWorkingLayer,
                            myFilename))
    #print 'Command: ', myCommand
    myResult = call(myCommand, shell=True)
    # .. todo:: Check the result of the shell call is ok
    copyKeywords(str(layer.source()), myFilename)
    return myFilename  # Filename of created file


def _reprojectRasterLayer(theLayer):
    """Reproject a Hazard or Exposure layer to EPSG:4326
    The layer must be a raster layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS raster layer

    Returns:
        Path to the output reprojected layer. The output
        will be placed in the system temp dir. If the
        original layer is already in WGS84, the original
        layer's file name is simply returned without doing
        anything.

    Raises:
       InvalidParameterException if an invalid input is
       received.

    """
    if not theLayer:
        msg = 'Layer passed for reprojection is None.'
        raise InvalidParameterException(msg)

    if theLayer.type() != QgsMapLayer.RasterLayer:
        msg = ('Expected a raster layer but received a %s.' %
               str(theLayer.type()))
        raise InvalidParameterException(msg)

    mySource = theLayer.source()
    # Get the crs of the layer so we can check if it is not yet in EPSG:4326
    myCrs = theLayer.crs()
    if myCrs.epsg() != 4326:
            # Reproject the layer to wgs84
        myFilename = tempfile.mkstemp('.tif', 'prj_',
                                tempfile.gettempdir())[1]
        myCommand = 'gdalwarp -t_srs EPSG:4326 -r near -of GTiff %s %s' % (
            mySource, myFilename)
        myResult = call(myCommand, shell=True)
        # .. todo:: Check the result of the shell call is ok
        # Set the source to the filename so code after this if
        # block continues to work as expected
        mySource = myFilename

    return mySource


def copyKeywords(sourceFile, destinationFile):
    """Helper to copy the keywords file from a source dataset
    to a destination dataset.

    e.g.::

    copyKeywords('foo.shp','bar.shp')

    Will result in the foo.keywords file being copied to bar.keyword."""

    mySourceBase = os.path.splitext(sourceFile)[0]
    myDestinationBase = os.path.splitext(destinationFile)[0]
    myNewSource = mySourceBase + '.keywords'
    myNewDestination = myDestinationBase + '.keywords'
    if not os.path.exists(myNewSource):
        msg = ('Keywords file associated with dataset could not be found: \n%s'
               % myNewSource)
        raise KeywordNotFoundException(msg)
    try:
        shutil.copyfile(myNewSource, myNewDestination)
    except:
        msg = ('Failed to copy keywords file from :\n%s\nto\%s' %
               (myNewSource, myNewDestination))
    return
