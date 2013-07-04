"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **ISClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import tempfile
import logging

from PyQt4.QtCore import QCoreApplication, QProcess, QVariant
from qgis.core import (
    QGis,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsMapLayer,
    QgsFeature,
    QgsVectorFileWriter,
    QgsGeometry,
    QgsVectorLayer,
    QgsRasterLayer)

from safe_qgis.safe_interface import (verify,
                                      readKeywordsFromFile,
                                      temp_dir)

from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.exceptions import (
    InvalidParameterError,
    NoFeaturesInExtentError,
    CallGDALError,
    InvalidProjectionError,
    InvalidClipGeometryError)
from safe_qgis.utilities.utilities import which

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
    myContext = "@default"
    # noinspection PyCallByClass
    return QCoreApplication.translate(myContext, theText)


def clipLayer(theLayer,
              theExtent,
              theCellSize=None,
              theExtraKeywords=None,
              theExplodeFlag=True,
              theHardClipFlag=False,
              theExplodeAttribute=None):
    """Clip a Hazard or Exposure layer to the extents provided.

    .. note:: Will delegate to clipVectorLayer or clipRasterLayer as needed.

    :param theLayer: A valid QGIS vector or raster layer
    :type theLayer:

    :param theExtent: Either an array representing the exposure layer extents
        in the form [xmin, ymin, xmax, ymax]. It is assumed that the coordinates
        are in EPSG:4326 although currently no checks are made to enforce this.
        or: A QgsGeometry of type polygon. **Polygon clipping is currently
        only supported for vector datasets.**
    :type theExtent:

    :param theCellSize: cell size which the layer should be resampled to.
        This argument will be ignored for vector layers and if not provided
        for a raster layer, the native raster cell size will be used.
    :type theCellSize:

    :param theExtraKeywords: Optional keywords dictionary to be added to
        output layer.
    :type theExtraKeywords:

    :param theExplodeFlag: A bool specifying whether multipart features
        should be 'exploded' into singleparts. **This parameter is ignored
        for raster layer clipping.**
    :type theExplodeFlag: bool

    :param theHardClipFlag: A bool specifying whether line and polygon
        features that extend beyond the extents should be clipped such that they
        are reduced in size to the part of the geometry that intersects the
        extent only. Default is False. **This parameter is ignored for raster
        layer clipping.**
    :type theHardClipFlag: bool

    :param theExplodeAttribute: A str specifying to which attribute #1,
        #2 and so on will be added in case of theExplodeFlag being true. The
        attribute is modified only if there are at least 2 parts **This
        parameter is ignored for raster layer clipping.**
    :type theExplodeAttribute: str

    :returns: Clipped layer (placed in the system temp dir). The output layer
        will be reprojected to EPSG:4326 if needed.
    """

    if theLayer.type() == QgsMapLayer.VectorLayer:
        return _clipVectorLayer(theLayer,
                                theExtent,
                                theExtraKeywords=theExtraKeywords,
                                theExplodeFlag=theExplodeFlag,
                                theHardClipFlag=theHardClipFlag,
                                theExplodeAttribute=theExplodeAttribute)
    else:
        try:
            return _clipRasterLayer(
                theLayer, theExtent, theCellSize,
                theExtraKeywords=theExtraKeywords)
        except CallGDALError, e:
            raise e
        except IOError, e:
            raise e


def _clipVectorLayer(theLayer,
                     theExtent,
                     theExtraKeywords=None,
                     theExplodeFlag=True,
                     theHardClipFlag=False,
                     theExplodeAttribute=None):
    """Clip a Hazard or Exposure layer to the
    extents of the current view frame. The layer must be a
    vector layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS vector layer in EPSG:4326
        * theExtent either: an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
                    or: A QgsGeometry of type polygon. **Polygon clipping is
           currently only supported for vector datasets.**
        * theExtraKeywords - any additional keywords over and above the
          original keywords that should be associated with the cliplayer.
        * theExplodeFlag - a bool specifying whether multipart features
            should be 'exploded' into singleparts.
        * theHardClipFlag - a bool specifying whether line and polygon features
            that extend beyond the extents should be clipped such that they
            are reduced in size to the part of the geometry that intersects
            the extent only. Default is False.
        * theExplodeAttribute - a str specifying to which attribute #1, #2 and
            so on will be added in case of theExplodeFlag being true.
            The attribute is modified only if there are at least 2 parts


    Returns:
        QgsVectorLayer - output clipped layer (placed in the system temp dir).

    Raises:
       None

    """
    if not theLayer or not theExtent:
        myMessage = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterError(myMessage)

    if theLayer.type() != QgsMapLayer.VectorLayer:
        myMessage = tr('Expected a vector layer but received a %s.' %
                       str(theLayer.type()))
        raise InvalidParameterError(myMessage)

    #myHandle, myFilename = tempfile.mkstemp('.sqlite', 'clip_',
    #    temp_dir())
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
    myAllowedClipTypes = [QGis.WKBPolygon, QGis.WKBPolygon25D]
    if type(theExtent) is list:
        myRect = QgsRectangle(
            theExtent[0], theExtent[1],
            theExtent[2], theExtent[3])
        # noinspection PyCallByClass
        myClipPolygon = QgsGeometry.fromRect(myRect)
    elif (type(theExtent) is QgsGeometry and
          theExtent.wkbType in myAllowedClipTypes):
        myRect = theExtent.boundingBox().toRectF()
        myClipPolygon = theExtent
    else:
        raise InvalidClipGeometryError(
            tr(
                'Clip geometry must be an extent or a single part'
                'polygon based geometry.'))

    myProjectedExtent = myXForm.transformBoundingBox(myRect)

    # Get vector layer
    myProvider = theLayer.dataProvider()
    if myProvider is None:
        myMessage = tr('Could not obtain data provider from '
                       'layer "%s"' % theLayer.source())
        raise Exception(myMessage)

    # Get the layer field list, select by our extent then write to disk
    # .. todo:: FIXME - for different geometry types we should implement
    #    different clipping behaviour e.g. reject polygons that
    #    intersect the edge of the bbox. Tim
    myAttributes = myProvider.attributeIndexes()
    myFetchGeometryFlag = True
    myUseIntersectFlag = True
    myProvider.select(
        myAttributes,
        myProjectedExtent,
        myFetchGeometryFlag,
        myUseIntersectFlag)

    myFieldList = myProvider.fields()

    myWriter = QgsVectorFileWriter(
        myFilename,
        'UTF-8',
        myFieldList,
        theLayer.wkbType(),
        myGeoCrs,
        #'SQLite')  # FIXME (Ole): This works but is far too slow
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
    myHasMultipart = False

    if theExplodeAttribute is not None:
        theExplodeAttributeIndex = myProvider.fieldNameIndex(
            theExplodeAttribute)

    while myProvider.nextFeature(myFeature):
        myGeometry = myFeature.geometry()
        if theExplodeAttribute is not None:
            myAttrs = myFeature.attributeMap()
        # Loop through the parts adding them to the output file
        # we write out single part features unless theExplodeFlag is False
        if theExplodeFlag:
            myGeometryList = explodeMultiPartGeometry(myGeometry)
        else:
            myGeometryList = [myGeometry]

        for myPartIndex, myPart in enumerate(myGeometryList):
            myPart.transform(myXForm)
            if theHardClipFlag:
                # Remove any dangling bits so only intersecting area is
                # kept.
                myPart = clipGeometry(myClipPolygon, myPart)
            if myPart is None:
                continue

            myFeature.setGeometry(myPart)
            # There are multiple parts and we want to show it in the
            # theExplodeAttribute
            if myPartIndex > 0 and theExplodeAttribute is not None:
                myHasMultipart = True
                myPartAttr = QVariant(
                    '%s #%s' % (myAttrs[theExplodeAttributeIndex].toString(),
                                myPartIndex))
                myFeature.changeAttribute(theExplodeAttributeIndex, myPartAttr)

            myWriter.addFeature(myFeature)
        myCount += 1
    del myWriter  # Flush to disk

    if myCount < 1:
        myMessage = tr(
            'No features fall within the clip extents. Try panning / zooming '
            'to an area containing data and then try to run your analysis '
            'again. If hazard and exposure data doesn\'t overlap at all, it '
            'is not possible to do an analysis. Another possibility is that '
            'the layers do overlap but because they may have different '
            'spatial references, they appear to be disjointed. If this is the '
            'case, try to turn on reproject on-the-fly in QGIS.')
        raise NoFeaturesInExtentError(myMessage)

    myKeywordIO = KeywordIO()
    if theExtraKeywords is None:
        theExtraKeywords = {}
    theExtraKeywords['HAD_MULTIPART_POLY'] = myHasMultipart
    myKeywordIO.copyKeywords(
        theLayer, myFilename, theExtraKeywords=theExtraKeywords)
    myBaseName = '%s clipped' % theLayer.name()
    myLayer = QgsVectorLayer(myFilename, myBaseName, 'ogr')

    return myLayer


def clipGeometry(theClipPolygon, theGeometry):
    """Clip a geometry (linestring or polygon) using a clip polygon.

    To do this we combine the clip polygon with the input geometry which
    will add nodes to the input geometry where it intersects the clip polygon.
    Next we get the symmetrical difference between the input geometry and the
    combined geometry.

    Args:
        * theClipPolygon - QgsGeometry a Polygon or Polygon25D geometry to clip
            with. Multipart polygons are not supported so the client needs to
            take care of that.
        * theGeometry - QgsGeometry - linestring or polygon that should be
            clipped.

    Returns:
        QgsGeometry - clipped to the region of the clip polygon.

    Raises:
        None
    """
    # Add nodes to input geometry where it intersects with clip
    myLineTypes = [QGis.WKBLineString, QGis.WKBLineString25D]
    myPointTypes = [QGis.WKBPoint, QGis.WKBPoint25D]
    myPolygonTypes = [QGis.WKBPolygon, QGis.WKBPolygon25D]
    myType = theGeometry.wkbType()
    if myType in myLineTypes:
        myCombinedGeometry = theGeometry.combine(theClipPolygon)
        # Gives you the lines inside the clip
        mySymmetricalGeometry = theGeometry.symDifference(myCombinedGeometry)
        return mySymmetricalGeometry
    elif myType in myPolygonTypes:
        myIntersectionGeometry = theGeometry.intersection(theClipPolygon)
        return myIntersectionGeometry
    elif myType in myPointTypes:
        if theClipPolygon.contains(theGeometry):
            return theGeometry
        else:
            return None
    else:
        return None


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
    myParts = []
    if theGeom.type() == QGis.Point:
        if theGeom.isMultipart():
            myMultiGeometry = theGeom.asMultiPoint()
            for i in myMultiGeometry:
                myParts.append(QgsGeometry().fromPoint(i))
        else:
            myParts.append(theGeom)
    elif theGeom.type() == QGis.Line:
        if theGeom.isMultipart():
            myMultiGeometry = theGeom.asMultiPolyline()
            for i in myMultiGeometry:
                myParts.append(QgsGeometry().fromPolyline(i))
        else:
            myParts.append(theGeom)
    elif theGeom.type() == QGis.Polygon:
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
        * theExtent either: an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
                    or: A QgsGeometry of type polygon. **Polygon clipping is
           currently only supported for vector datasets.**
        * theCellSize - cell size (in GeoCRS) which the layer should
            be resampled to. If not provided for a raster layer (i.e.
            theCellSize=None), the native raster cell size will be used.

    Returns:
        QgsRasterLayer - the output clipped layer (placed in the
        system temp dir).

    Raises:
       Exception if input layer is a density layer in projected coordinates -
       see issue #123

    """
    if not theLayer or not theExtent:
        myMessage = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterError(myMessage)

    if theLayer.type() != QgsMapLayer.RasterLayer:
        myMessage = tr(
            'Expected a raster layer but received a %s.' %
            str(theLayer.type()))
        raise InvalidParameterError(myMessage)

    myWorkingLayer = str(theLayer.source())

    # Check for existence of keywords file
    myKeywordsPath = myWorkingLayer[:-4] + '.keywords'
    myMessage = tr(
        'Input file to be clipped "%s" does not have the '
        'expected keywords file %s' % (
            myWorkingLayer, myKeywordsPath))
    verify(os.path.isfile(myKeywordsPath), myMessage)

    # Raise exception if layer is projected and refers to density (issue #123)
    # FIXME (Ole): Need to deal with it - e.g. by automatically reprojecting
    # the layer at this point and setting the native resolution accordingly
    # in its keywords.
    myKeywords = readKeywordsFromFile(myKeywordsPath)
    if 'datatype' in myKeywords and myKeywords['datatype'] == 'density':
        if str(theLayer.crs().authid()) != 'EPSG:4326':

            # This layer is not WGS84 geographic
            myMessage = ('Layer %s represents density but has spatial '
                         'reference "%s". Density layers must be given in '
                         'WGS84 geographic coordinates, so please reproject '
                         'and try again. For more information, see issue '
                         'https://github.com/AIFDR/inasafe/issues/123'
                         % (myWorkingLayer, theLayer.crs().toProj4()))
            raise InvalidProjectionError(myMessage)

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
    myBinaryList = which('gdalwarp')
    LOGGER.debug('Path for gdalwarp: %s' % myBinaryList)
    if len(myBinaryList) < 1:
        raise CallGDALError(
            tr('gdalwarp could not be found on your computer'))
    # Use the first matching gdalwarp found
    myBinary = myBinaryList[0]
    if theCellSize is None:
        myCommand = ('%s -q -t_srs EPSG:4326 -r near '
                     '-cutline %s -crop_to_cutline -of GTiff '
                     '"%s" "%s"' % (myBinary,
                                    myClipKml,
                                    myWorkingLayer,
                                    myFilename))
    else:
        myCommand = ('%s -q -t_srs EPSG:4326 -r near -tr %f %f '
                     '-cutline %s -crop_to_cutline -of GTiff '
                     '"%s" "%s"' % (myBinary,
                                    theCellSize,
                                    theCellSize,
                                    myClipKml,
                                    myWorkingLayer,
                                    myFilename))

    LOGGER.debug(myCommand)
    myResult = QProcess().execute(myCommand)

    # For QProcess exit codes see
    # http://qt-project.org/doc/qt-4.8/qprocess.html#execute
    if myResult == -2:  # cannot be started
        myMessageDetail = tr('Process could not be started.')
        myMessage = tr(
            '<p>Error while executing the following shell command:'
            '</p><pre>%s</pre><p>Error message: %s'
            % (myCommand, myMessageDetail))
        raise CallGDALError(myMessage)
    elif myResult == -1:  # process crashed
        myMessageDetail = tr('Process could not be started.')
        myMessage = tr('<p>Error while executing the following shell command:'
                       '</p><pre>%s</pre><p>Error message: %s'
                       % (myCommand, myMessageDetail))
        raise CallGDALError(myMessage)

    # .. todo:: Check the result of the shell call is ok
    myKeywordIO = KeywordIO()
    myKeywordIO.copyKeywords(theLayer, myFilename,
                             theExtraKeywords=theExtraKeywords)
    myBaseName = '%s clipped' % theLayer.name()
    myLayer = QgsRasterLayer(myFilename, myBaseName)

    return myLayer


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
</kml>""" % (
        myBottomLeftCorner,
        myTopLeftCorner,
        myTopRightCorner,
        myBottomRightCorner,
        myBottomLeftCorner))

    myFilename = tempfile.mkstemp('.kml', 'extent_', temp_dir())[1]
    myFile = file(myFilename, 'wt')
    myFile.write(myKml)
    myFile.close()
    return myFilename


def extentToGeoArray(theExtent, theSourceCrs):
    """Convert the supplied extent to geographic and return as as array.

    :param theExtent: QgsRectangle to be transformed to geocrs.
    :type theExtent:

    :param theSourceCrs: QgsCoordinateReferenceSystem representing the
        original extent's CRS.
    :type theSourceCrs:

    :returns: Transformed extents in EPSG:4326 in the form
        [xmin, ymin, xmax, ymax]
    """

    myGeoCrs = QgsCoordinateReferenceSystem()
    myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    myXForm = QgsCoordinateTransform(
        theSourceCrs,
        myGeoCrs)

    # Get the clip area in the layer's crs
    myTransformedExtent = myXForm.transformBoundingBox(theExtent)

    myGeoExtent = [myTransformedExtent.xMinimum(),
                   myTransformedExtent.yMinimum(),
                   myTransformedExtent.xMaximum(),
                   myTransformedExtent.yMaximum()]
    return myGeoExtent
