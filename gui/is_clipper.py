"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **ISClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.3.0'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import tempfile

from PyQt4.QtCore import QCoreApplication
from qgis.core import (QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsRectangle,
                       QgsMapLayer,
                       QgsFeature,
                       QgsVectorFileWriter)

from storage.utilities import read_keywords, write_keywords, verify

from is_exceptions import (InvalidParameterException,
                            KeywordNotFoundException,
                            NoFeaturesInExtentException)
from is_utilities import getTempDir
from subprocess import call


def tr(theText):
    """We define a tr() alias here since the ISClipper implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences
    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "ISClipper"
    return QCoreApplication.translate(myContext, theText)


def clipLayer(theLayer, theExtent, theCellSize=None, extraKeywords=None):
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
        * extraKeywords - Optional keywords dictionary to be added to
                          output layer

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir). The output layer will be reprojected to EPSG:4326
        if needed.

    Raises:
        None

    """
    if theLayer.type() == QgsMapLayer.VectorLayer:
        return _clipVectorLayer(theLayer, theExtent,
                                extraKeywords=extraKeywords)
    else:
        return _clipRasterLayer(theLayer, theExtent, theCellSize,
                                extraKeywords=extraKeywords)


def _clipVectorLayer(theLayer, theExtent,
                     extraKeywords=None):
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

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """
    if not theLayer or not theExtent:
        msg = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterException(msg)

    if theLayer.type() != QgsMapLayer.VectorLayer:
        msg = tr('Expected a vector layer but received a %s.' %
                str(theLayer.type()))
        raise InvalidParameterException(msg)

    myHandle, myFilename = tempfile.mkstemp('.shp', 'clip_',
                                            getTempDir())

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
        msg = tr('Could not obtain data provider from '
               'layer "%s"' % theLayer.source())
        raise Exception(msg)

    # get the layer field list, select by our extent then write to disk
    # .. todo:: FIXME - for different geometry types we should implement
    #           different clipping behaviour e.g. reject polygons that
    #           intersect the edge of the bbox. Tim
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
        msg = tr('Error when creating shapefile: <br>Filename:'
               '%s<br>Error: %s' %
            (myFilename, myWriter.hasError()))
        raise Exception(msg)

    # Reverse the coordinate xform now so that we can convert
    # geometries from layer crs to geocrs.
    myXForm = QgsCoordinateTransform(theLayer.crs(), myGeoCrs)
    # Retrieve every feature with its geometry and attributes
    myFeature = QgsFeature()
    myCount = 0
    while myProvider.nextFeature(myFeature):
        myGeometry = myFeature.geometry()
        myGeometry.transform(myXForm)
        myFeature.setGeometry(myGeometry)
        myWriter.addFeature(myFeature)
        myCount += 1
    del myWriter  # Flush to disk

    if myCount < 1:
        myMessage = tr('No features fall within the clip extents. '
                       'Try panning / zooming to an area containing data '
                       'and then try to run your analysis again.')
        raise NoFeaturesInExtentException(myMessage)

    copyKeywords(theLayer.source(), myFilename, extraKeywords=extraKeywords)

    return myFilename  # Filename of created file


def _clipRasterLayer(theLayer, theExtent, theCellSize=None,
                     extraKeywords=None):
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
            be resampled to. If not provided for a raster layer,
            the native raster cell size will be used.

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """
    if not theLayer or not theExtent:
        msg = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterException(msg)

    if theLayer.type() != QgsMapLayer.RasterLayer:
        msg = tr('Expected a raster layer but received a %s.' %
               str(theLayer.type()))
        raise InvalidParameterException(msg)

    myWorkingLayer = theLayer.source()

    # Check for existence of keywords file
    myKeywordsPath = str(myWorkingLayer)[:-4] + '.keywords'
    msg = tr('Input file to be clipped "%s" does not have the '
           'expected keywords file %s' % (myWorkingLayer,
                                          myKeywordsPath))
    verify(os.path.isfile(myKeywordsPath), msg)

    # We need to provide gdalwarp with a dataset for the clip
    # because unline gdal_translate, it does not take projwin.
    myClipKml = extentToKml(theExtent)

    # Create a filename for the clipped, resampled and reprojected layer
    myHandle, myFilename = tempfile.mkstemp('.tif', 'clip_',
                                            getTempDir())
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

    # Now run GDAL warp scottie...
    try:
        myResult = call(myCommand, shell=True)
        del myResult
    except Exception, e:
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
    copyKeywords(myWorkingLayer, myFilename, extraKeywords=extraKeywords)
    return myFilename  # Filename of created file


def copyKeywords(sourceFile, destinationFile, extraKeywords=None):
    """Helper to copy the keywords file from a source dataset
    to a destination dataset.

    e.g.::

    copyKeywords('foo.shp', 'bar.shp')

    Will result in the foo.keywords file being copied to bar.keyword.

    Optional argument extraKeywords is a dictionary with additional
    keywords that will be added to the destination file
    e.g::

    copyKeywords('foo.shp', 'bar.shp', {'resolution': 0.01})
    """

    # FIXME (Ole): Need to turn qgis strings into normal strings earlier
    mySourceBase = os.path.splitext(str(sourceFile))[0]
    myDestinationBase = os.path.splitext(destinationFile)[0]
    myNewSource = mySourceBase + '.keywords'
    myNewDestination = myDestinationBase + '.keywords'

    if not os.path.isfile(myNewSource):
        msg = tr('Keywords file associated with dataset could not be found:'
                 ' \n%s' % myNewSource)
        raise KeywordNotFoundException(msg)

    if extraKeywords is None:
        extraKeywords = {}
    msg = tr('Expected extraKeywords to be a dictionary. Got %s'
           % str(type(extraKeywords))[1:-1])
    verify(isinstance(extraKeywords, dict), msg)

    try:
        srcKeywords = read_keywords(myNewSource)
        dstKeywords = srcKeywords
        for key in extraKeywords:
            dstKeywords[key] = extraKeywords[key]
        write_keywords(dstKeywords, myNewDestination)
    except Exception, e:
        msg = tr('Failed to copy keywords file from :\n%s\nto\%s: %s' %
               (myNewSource, myNewDestination, str(e)))
        raise Exception(msg)

    #try:
    #    shutil.copyfile(myNewSource, myNewDestination)
    #except Exception, e:
    #    msg = ('Failed to copy keywords file from :\n%s\nto\%s: %s' %
    #           (myNewSource, myNewDestination, str(e)))
    #    raise Exception(msg)

    return


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
                                      getTempDir())[1]
    myFile = file(myFilename, 'wt')
    myFile.write(myKml)
    myFile.close()
    return myFilename
