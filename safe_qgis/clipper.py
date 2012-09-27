"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **ISClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
from safe.common.utilities import temp_dir

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import tempfile
import logging
from subprocess import (call, CalledProcessError)

from PyQt4.QtCore import QCoreApplication
from qgis.core import (QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsRectangle,
                       QgsMapLayer,
                       QgsFeature,
                       QgsVectorFileWriter,
                       QgsGeometry)

from safe_qgis.safe_interface import (verify,
                                      readKeywordsFromFile)

from safe_qgis.keyword_io import KeywordIO
from safe_qgis.exceptions import (InvalidParameterException,
                           NoFeaturesInExtentException,
                           InvalidProjectionException)

LOGGER = logging.getLogger(name='InaSAFE')


def tr(theText):
    """We define a tr() alias here since the ClipperTest implementation below
    is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    Args:
       theText - string to be translated

    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "ClipperTest"
    return QCoreApplication.translate(myContext, theText)


def clipLayer(theLayer, theExtent, theCellSize=None, theExtraKeywords=None,
              explodeMultipart=True):
    """Clip a Hazard or Exposure layer to the extents provided.

    .. note:: Will delegate to clipVectorLayer or clipRasterLayer as needed.

    Args:

        * theLayer - a valid QGIS vector or raster layer
        * theExtent - an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * theCellSize - cell size which the layer should be resampled to.
            This argument will be ignored for vector layers and if not provided
            for a raster layer, the native raster cell size will be used.
        * theExtraKeywords - Optional keywords dictionary to be added to
                          output layer
        * explodeMultipart - a bool describing if to convert multipart
        features into singleparts

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir). The output layer will be reprojected to EPSG:4326
        if needed.

    Raises:
        None

    """
    if theLayer.type() == QgsMapLayer.VectorLayer:
        return _clipVectorLayer(theLayer, theExtent,
            theExtraKeywords=theExtraKeywords,
            explodeMultipart=explodeMultipart)
    else:
        return _clipRasterLayer(theLayer, theExtent, theCellSize,
            theExtraKeywords=theExtraKeywords)


def _clipVectorLayer(theLayer, theExtent,
                     theExtraKeywords=None, explodeMultipart=True):
    """Clip a Hazard or Exposure layer to the
    extents of the current view frame. The layer must be a
    vector layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS vector layer in EPSG:4326
        * theExtent -  an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * theExtraKeywords - any additional keywords over and above the
          original keywords that should be associated with the cliplayer.
        * explodeMultipart - a bool describing if to convert multipart
        features into singleparts

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """
    if not theLayer or not theExtent:
        myMessage = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterException(myMessage)

    if theLayer.type() != QgsMapLayer.VectorLayer:
        myMessage = tr('Expected a vector layer but received a %s.' %
                       str(theLayer.type()))
        raise InvalidParameterException(myMessage)

    myHandle, myFilename = tempfile.mkstemp('.shp', 'clip_',
        temp_dir())

    # Ensure the file is deleted before we try to write to it
    # fixes windows specific issue where you get a message like this
    # ERROR 1: c:\temp\inasafe\clip_jpxjnt.shp is not a directory.
    # This is because mkstemp creates the file handle and leaves
    # the file open.
    os.close(myHandle)
    os.remove(myFilename)

    # Get the clip extents in the layer's native CRS
    myGeoCrs = QgsCoordinateReferenceSystem()
    myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    myXForm = QgsCoordinateTransform(myGeoCrs, theLayer.crs())
    myRect = QgsRectangle(theExtent[0], theExtent[1],
        theExtent[2], theExtent[3])
    myProjectedExtent = myXForm.transformBoundingBox(myRect)

    # Get vector layer
    myProvider = theLayer.dataProvider()
    if myProvider is None:
        myMessage = tr('Could not obtain data provider from '
                       'layer "%s"' % theLayer.source())
        raise Exception(myMessage)

    # get the layer field list, select by our extent then write to disk
    # .. todo:: FIXME - for different geometry types we should implement
    #    different clipping behaviour e.g. reject polygons that
    #    intersect the edge of the bbox. Tim
    myAttributes = myProvider.attributeIndexes()
    myFetchGeometryFlag = True
    myUseIntersectFlag = True
    myProvider.select(myAttributes,
        myProjectedExtent,
        myFetchGeometryFlag,
        myUseIntersectFlag)

    myFieldList = myProvider.fields()

    myWriter = QgsVectorFileWriter(myFilename,
        'UTF-8',
        myFieldList,
        theLayer.wkbType(),
        myGeoCrs,
        'ESRI Shapefile')
    if myWriter.hasError() != QgsVectorFileWriter.NoError:
        myMessage = tr('Error when creating shapefile: <br>Filename:'
                       '%s<br>Error: %s' %
                       (myFilename, myWriter.hasError()))
        raise Exception(myMessage)

    # Reverse the coordinate xform now so that we can convert
    # geometries from layer crs to geocrs.
    myXForm = QgsCoordinateTransform(theLayer.crs(), myGeoCrs)
    # Retrieve every feature with its geometry and attributes
    myFeature = QgsFeature()
    myCount = 0
    while myProvider.nextFeature(myFeature):
        myGeometry = myFeature.geometry()
        # Loop through the parts adding them to the output file
        # we write out single part features unless explodeMultipart is False
        if explodeMultipart:
            myGeometryList = explodeMultiPartGeometry(myGeometry)
        else:
            myGeometryList = [myGeometry]

        for myPart in myGeometryList:
            myPart.transform(myXForm)
            myFeature.setGeometry(myPart)
            myWriter.addFeature(myFeature)
        myCount += 1
    del myWriter  # Flush to disk

    if myCount < 1:
        myMessage = tr('No features fall within the clip extents. '
                       'Try panning / zooming to an area containing data '
                       'and then try to run your analysis again.')
        raise NoFeaturesInExtentException(myMessage)

    myKeywordIO = KeywordIO()
    myKeywordIO.copyKeywords(theLayer, myFilename,
        theExtraKeywords=theExtraKeywords)

    return myFilename  # Filename of created file


def explodeMultiPartGeometry(theGeom):
    """Convert a multipart geometry to a list of single parts. This method was
    adapted from Carson Farmer's fTools doGeometry implementation in QGIS.

    Args:
       theGeom - A geometry - if it is multipart it will be exploded.

    Returns:
        A list of single part geometries

    Raises:
       None

    """
    myMultiGeometry = QgsGeometry()
    myParts = []
    if theGeom.type() == 0:
        if theGeom.isMultipart():
            myMultiGeometry = theGeom.asMultiPoint()
            for i in myMultiGeometry:
                myParts.append(QgsGeometry().fromPoint(i))
        else:
            myParts.append(theGeom)
    elif theGeom.type() == 1:
        if theGeom.isMultipart():
            myMultiGeometry = theGeom.asMultiPolyline()
            for i in myMultiGeometry:
                myParts.append(QgsGeometry().fromPolyline(i))
        else:
            myParts.append(theGeom)
    elif theGeom.type() == 2:
        if theGeom.isMultipart():
            myMultiGeometry = theGeom.asMultiPolygon()
            for i in myMultiGeometry:
                myParts.append(QgsGeometry().fromPolygon(i))
        else:
            myParts.append(theGeom)
    return myParts


def _clipRasterLayer(theLayer, theExtent, theCellSize=None,
                     theExtraKeywords=None):
    """Clip a Hazard or Exposure raster layer to the extents provided. The
    layer must be a raster layer or an exception will be thrown.

    .. note:: The extent *must* be in EPSG:4326.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS raster layer in EPSG:4326
        * theExtent -  an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * theCellSize - cell size (in GeoCRS) which the layer should
            be resampled to. If not provided for a raster layer (i.e.
            theCellSize=None), the native raster cell size will be used.

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       Exception if input layer is a density layer in projected coordinates -
       see issue #123

    """
    if not theLayer or not theExtent:
        myMessage = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterException(myMessage)

    if theLayer.type() != QgsMapLayer.RasterLayer:
        myMessage = tr('Expected a raster layer but received a %s.' %
               str(theLayer.type()))
        raise InvalidParameterException(myMessage)

    myWorkingLayer = str(theLayer.source())

    # Check for existence of keywords file
    myKeywordsPath = myWorkingLayer[:-4] + '.keywords'
    myMessage = tr('Input file to be clipped "%s" does not have the '
           'expected keywords file %s' % (myWorkingLayer,
                                          myKeywordsPath))
    verify(os.path.isfile(myKeywordsPath), myMessage)

    # Raise exception if layer is projected and refers to density (issue #123)
    # FIXME (Ole): Need to deal with it - e.g. by automatically reprojecting
    # the layer at this point and setting the native resolution accordingly
    # in its keywords.
    myKeywords = readKeywordsFromFile(myKeywordsPath)
    if 'datatype' in myKeywords and myKeywords['datatype'] == 'density':
        if theLayer.srs().epsg() != 4326:

            # This layer is not WGS84 geographic
            myMessage = ('Layer %s represents density but has spatial '
                         'reference "%s". Density layers must be given in '
                         'WGS84 geographic coordinates, so please reproject '
                         'and try again. For more information, see issue '
                         'https://github.com/AIFDR/inasafe/issues/123'
                         % (myWorkingLayer, theLayer.srs().toProj4()))
            raise InvalidProjectionException(myMessage)

    # We need to provide gdalwarp with a dataset for the clip
    # because unline gdal_translate, it does not take projwin.
    myClipKml = extentToKml(theExtent)

    # Create a filename for the clipped, resampled and reprojected layer
    myHandle, myFilename = tempfile.mkstemp('.tif', 'clip_',
                                            temp_dir())
    os.close(myHandle)
    os.remove(myFilename)

    # If no cell size is specified, we need to run gdalwarp without
    # specifying the output pixel size to ensure the raster dims
    # remain consistent.
    if theCellSize is None:
        myCommand = ('gdalwarp -q -t_srs EPSG:4326 -r near '
                     '-cutline %s -crop_to_cutline -of GTiff '
                     '"%s" "%s"' % (myClipKml,
                                    myWorkingLayer,
                                    myFilename))
    else:
        myCommand = ('gdalwarp -q -t_srs EPSG:4326 -r near -tr %f %f '
                     '-cutline %s -crop_to_cutline -of GTiff '
                     '"%s" "%s"' % (theCellSize,
                                    theCellSize,
                                    myClipKml,
                                    myWorkingLayer,
                                    myFilename))
    myExecutablePrefix = ''
    if sys.platform == 'darwin':  # Mac OS X
        # .. todo:: FIXME - softcode gdal version in this path
        myExecutablePrefix = ('/Library/Frameworks/GDAL.framework/'
                              'Versions/1.9/Programs/')
    myCommand = myExecutablePrefix + myCommand

    # For debugging only
    # myCommand = myExecutablePrefix + myCommand
    # myFile = file('C:/temp/command.txt', 'wt')
    # myFile.write(myCommand)
    # myFile.close()
    # Now run GDAL warp scottie...
    LOGGER.debug(myCommand)
    try:
        myResult = call(myCommand, shell=True)
        del myResult
    except CalledProcessError, e:
        myMessage = tr('<p>Error while executing the following shell command:'
                     '</p><pre>%s</pre><p>Error message: %s'
                     % (myCommand, str(e)))
        # shameless hack - see https://github.com/AIFDR/inasafe/issues/141
        if sys.platform == 'darwin':  # Mac OS X
            if 'Errno 4' in str(e):
                # continue as the error seems to be non critical
                pass
            else:
                raise Exception(myMessage)
        else:
            raise Exception(myMessage)

    # .. todo:: Check the result of the shell call is ok
    myKeywordIO = KeywordIO()
    myKeywordIO.copyKeywords(theLayer, myFilename,
                             theExtraKeywords=theExtraKeywords)
    return myFilename  # Filename of created file


def extentToKml(theExtent):
    """A helper to get a little kml doc for an extent so that
    we can use it with gdal warp for clipping."""

    myBottomLeftCorner = '%f,%f' % (theExtent[0], theExtent[1])
    myTopLeftCorner = '%f,%f' % (theExtent[0], theExtent[3])
    myTopRightCorner = '%f,%f' % (theExtent[2], theExtent[3])
    myBottomRightCorner = '%f,%f' % (theExtent[2], theExtent[1])
    myKml = ("""<?xml version="1.0" encoding="utf-8" ?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Folder>
      <Placemark>
        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>
                %s %s %s %s %s
              </coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>""" %
    (myBottomLeftCorner,
     myTopLeftCorner,
     myTopRightCorner,
     myBottomRightCorner,
     myBottomLeftCorner))

    myFilename = tempfile.mkstemp('.kml', 'extent_',
                                      temp_dir())[1]
    myFile = file(myFilename, 'wt')
    myFile.write(myKml)
    myFile.close()
    return myFilename
