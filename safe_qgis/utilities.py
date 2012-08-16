"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilitles implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import traceback
import tempfile
import getpass
from datetime import date
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QCoreApplication
from qgis.core import (QGis,
                       QgsRasterLayer,
                       QgsMapLayer,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsGraduatedSymbolRendererV2,
                       QgsSymbolV2,
                       QgsRendererRangeV2,
                       QgsSymbolLayerV2Registry,
                       QgsColorRampShader,
                       QgsRasterTransparency)
from safe_qgis.exceptions import StyleError
#do not remove this even if it is marked as unused by your IDE
#resources are used by htmlfooter and header the comment will mark it unused
#for pylint
import safe_qgis.resources  # pylint: disable=W0611


def setVectorStyle(theQgisVectorLayer, theStyle):
    """Set QGIS vector style based on InaSAFE style dictionary

    Input
        theQgisVectorLayer: Qgis layer
        theStyle: Dictionary of the form as in the example below

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'opacity': 1, 'max': 1.5, 'colour': '#fecc5c',
          'min': 0.5, 'label': 'Low damage', 'size' : 1},
        {'opacity': 1, 'max': 2.5, 'colour': '#fd8d3c',
         'min': 1.5, 'label': 'Medium damage', 'size' : 1},
        {'opacity': 1, 'max': 3.5, 'colour': '#f31a1c',
         'min': 2.5, 'label': 'High damage', 'size' : 1}]}

        .. note:: The transparency and size keys are optional. Size applies
           to points only.
    Output
        Sets and saves style for theQgisVectorLayer

    """
    myTargetField = theStyle['target_field']
    myClasses = theStyle['style_classes']
    myGeometryType = theQgisVectorLayer.geometryType()

    myRangeList = []
    for myClass in myClasses:
        # Transparency 100: transparent
        # Transparency 0: opaque
        mySize = 2  # mm
        if 'size' in myClass:
            mySize = myClass['size']
        myTransparencyPercent = 0
        if 'transparency' in myClass:
            myTransparencyPercent = myClass['transparency']

        if 'min' not in myClass:
            raise StyleError('Style info should provide a "min" entry')
        if 'max' not in myClass:
            raise StyleError('Style info should provide a "max" entry')

        try:
            myMin = float(myClass['min'])
        except TypeError:
            raise StyleError('Class break lower bound should be a number.'
                'I got %s' % myClass['min'])

        try:
            myMax = float(myClass['max'])
        except TypeError:
            raise StyleError('Class break upper bound should be a number.'
                             'I got %s' % myClass['max'])

        myColour = myClass['colour']
        myLabel = myClass['label']
        myColour = QtGui.QColor(myColour)
        mySymbol = QgsSymbolV2.defaultSymbol(myGeometryType)
        myColourString = "%s, %s, %s" % (
                         myColour.red(),
                         myColour.green(),
                         myColour.blue())
        # Work around for the fact that QgsSimpleMarkerSymbolLayerV2
        # python bindings are missing from the QGIS api.
        # .. see:: http://hub.qgis.org/issues/4848
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        myRegistry = QgsSymbolLayerV2Registry.instance()
        if myGeometryType == QGis.Point:
            myMetadata = myRegistry.symbolLayerMetadata('SimpleMarker')
            # note that you can get a list of available layer properties
            # that you can set by doing e.g.
            # QgsSimpleMarkerSymbolLayerV2.properties()
            mySymbolLayer = myMetadata.createSymbolLayer({'color_border':
                                                          myColourString})
            mySymbolLayer.setSize(mySize)
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        elif myGeometryType == QGis.Polygon:
            myMetadata = myRegistry.symbolLayerMetadata('SimpleFill')
            mySymbolLayer = myMetadata.createSymbolLayer({'color_border':
                                                          myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        mySymbol.setColor(myColour)
        # .. todo:: Check that vectors use alpha as % otherwise scale TS
        # Convert transparency % to opacity
        # alpha = 0: transparent
        # alpha = 1: opaque
        alpha = 1 - myTransparencyPercent / 100
        mySymbol.setAlpha(alpha)
        myRange = QgsRendererRangeV2(myMin,
                                     myMax,
                                     mySymbol,
                                     myLabel)
        myRangeList.append(myRange)

    myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
    myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    myRenderer.setClassAttribute(myTargetField)
    theQgisVectorLayer.setRendererV2(myRenderer)
    theQgisVectorLayer.saveDefaultStyle()


def setRasterStyle(theQgsRasterLayer, theStyle):
    """Set QGIS raster style based on InaSAFE style dictionary.

    This function will set both the colour map and the transparency
    for the passed in layer.

    .. note:: There is currently a limitation in QGIS in that
       pixel transparency values can not be specified in ranges and
       consequently the opacity is of limited value and seems to
       only work effectively with integer values.

    .. todo:: Get Tim to implement range based transparency in
       the core QGIS library.

    Input
        theQgsRasterLayer: Qgis layer
        style: Dictionary of the form as in the example below
        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=1),
                         dict(colour='#79C900', quantity=10, transparency=1),
                         dict(colour='#CEED00', quantity=20, transparency=1),
                         dict(colour='#FFCC00', quantity=50, transparency=1),
                         dict(colour='#FF6600', quantity=100, transparency=1),
                         dict(colour='#FF0000', quantity=200, transparency=1),
                         dict(colour='#7A0000', quantity=300, transparency=1)]

    Output
        Sets and saves style for theQgsRasterLayer

    """
    theQgsRasterLayer.setDrawingStyle(QgsRasterLayer.PalettedColor)
    myClasses = theStyle['style_classes']
    myRangeList = []
    myTransparencyList = []
    myLastValue = 0
    for myClass in myClasses:
        myMax = myClass['quantity']
        myColour = QtGui.QColor(myClass['colour'])
        myLabel = QtCore.QString()
        if 'label' in myClass:
            myLabel = QtCore.QString(myClass['label'])
        myShader = QgsColorRampShader.ColorRampItem(myMax, myColour, myLabel)
        myRangeList.append(myShader)
        # Create opacity entries for this range
        myTransparencyPercent = 0
        if 'transparency' in myClass:
            myTransparencyPercent = int(myClass['transparency'])
        if myTransparencyPercent > 0:
            # Check if range extrema are integers so we know if we can
            # use them to calculate a value range
            if ((myLastValue == int(myLastValue)) and (myMax == int(myMax))):
                # Ensure that they are integers
                # (e.g 2.0 must become 2, see issue #126)
                myLastValue = int(myLastValue)
                myMax = int(myMax)

                # Set transparencies
                myRange = range(myLastValue, myMax)
                for myValue in myRange:
                    myPixel = \
                         QgsRasterTransparency.TransparentSingleValuePixel()
                    myPixel.pixelValue = myValue
                    myPixel.percentTransparent = myTransparencyPercent
                    myTransparencyList.append(myPixel)
        #myLabel = myClass['label']

    # Apply the shading algorithm and design their ramp
    theQgsRasterLayer.setColorShadingAlgorithm(QgsRasterLayer.ColorRampShader)
    myFunction = theQgsRasterLayer.rasterShader().rasterShaderFunction()
    # Discrete will shade any cell between maxima of this break
    # and mamima of previous break to the colour of this break
    myFunction.setColorRampType(QgsColorRampShader.DISCRETE)
    myFunction.setColorRampItemList(myRangeList)

    # Now set the raster transparency
    theQgsRasterLayer.rasterTransparency().setTransparentSingleValuePixelList(
                                                myTransparencyList)
    theQgsRasterLayer.saveDefaultStyle()
    return myRangeList, myTransparencyList


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
    myContext = "Utilities"
    return QCoreApplication.translate(myContext, theText)


def getExceptionWithStacktrace(e, html=False, context=None):
    """Convert exception into a string and and stack trace

    Input
        e: Exception object
        html: Optional flat if output is to wrapped as html
        context: Optional context message

    Output
        Exception with stack trace info suitable for display
    """

    myTraceback = ''.join(traceback.format_tb(sys.exc_info()[2]))

    if not html:
        if str(e) is None or str(e) == '':
            myErrorMessage = (e.__class__.__name__ + ' : ' +
                              tr('No details provided'))
        else:
            myErrorMessage = e.__class__.__name__ + ' : ' + str(e)
        return myErrorMessage + "\n" + myTraceback
    else:
        if str(e) is None or str(e) == '':
            myErrorMessage = ('<b>' + e.__class__.__name__ + '</b> : ' +
                              tr('No details provided'))
        else:
            myErrorMessage = '<b>' + e.__class__.__name__ + '</b> : ' + str(e)

        myTraceback = ('<pre id="traceback" class="prettyprint"'
              ' style="display: none;">\n' + myTraceback + '</pre>')

        # Wrap string in html
        s = '<table class="condensed">'
        if context is not None and context != '':
            s += ('<tr><th class="warning button-cell">'
                  + tr('Error:') + '</th></tr>\n'
                  '<tr><td>' + context + '</td></tr>\n')
        # now the string from the error itself
        s += ('<tr><th class="problem button-cell">'
              + tr('Problem:') + '</th></tr>\n'
            '<tr><td>' + myErrorMessage + '</td></tr>\n')
            # now the traceback heading
        s += ('<tr><th class="info button-cell" style="cursor:pointer;"'
              ' onclick="$(\'#traceback\').toggle();">'
              + tr('Click for Diagnostic Information:') + '</th></tr>\n'
              '<tr><td>' + myTraceback + '</td></tr>\n')
        s += '</table>'
        return s


def getTempDir(theSubDirectory=None):
    """Obtain the temporary working directory for the operating system.

    An inasafe subdirectory will automatically be created under this and
    if specified, a user subdirectory under that.

    Args:
        theSubDirectory str - optional argument which will cause an additional
                subirectory to be created e.g. /tmp/inasafe/foo/

    Returns:
        Path to the output clipped layer (placed in the system temp dir).

    Raises:
       Any errors from the underlying system calls.
    """
    myUser = getpass.getuser().replace(' ', '_')
    myCurrentDate = date.today()
    myDateString = myCurrentDate.strftime("%d-%m-%Y")
    # Following 4 lines are a workaround for tempfile.tempdir() unreliabilty
    myHandle, myFilename = tempfile.mkstemp()
    os.close(myHandle)
    myDir = os.path.dirname(myFilename)
    os.remove(myFilename)
    myPath = os.path.join(myDir, 'inasafe', myDateString, myUser, 'work')
    if theSubDirectory is not None:
        myPath = os.path.join(myPath, 'theSubDirectory')
    if not os.path.exists(myPath):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        myOldMask = os.umask(0000)
        os.makedirs(myPath, 0777)
        # Resinstate the old mask for tmp
        os.umask(myOldMask)
    return myPath


def getWGS84resolution(theLayer):
    """Return resolution of raster layer in EPSG:4326

    Input
        theLayer: Raster layer
    Output
        resolution.

    If input layer is already in EPSG:4326, simply return the resolution
    If not, work it out based on EPSG:4326 representations of its extent
    """

    msg = tr('Input layer to getWGS84resolution must be a raster layer. '
           'I got: %s' % str(theLayer.type())[1:-1])
    if not theLayer.type() == QgsMapLayer.RasterLayer:
        raise RuntimeError(msg)

    if theLayer.crs().authid() == 'EPSG:4326':
        # If it is already in EPSG:4326, simply use the native resolution
        myCellSize = theLayer.rasterUnitsPerPixel()
    else:
        # Otherwise, work it out based on EPSG:4326 representations of
        # its extent

        # Reproject extent to EPSG:4326
        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        myXForm = QgsCoordinateTransform(myGeoCrs, theLayer.crs())
        myExtent = theLayer.extent()
        myProjectedExtent = myXForm.transformBoundingBox(myExtent)

        # Estimate cellsize
        myColumns = theLayer.width()
        myGeoWidth = abs(myProjectedExtent.xMaximum() -
                         myProjectedExtent.xMinimum())
        myCellSize = myGeoWidth / myColumns

    return myCellSize


def htmlHeader():
    """Get a standard html header for wrapping content in."""
    myFile = QtCore.QFile(':/plugins/inasafe/header.html')
    if not myFile.open(QtCore.QIODevice.ReadOnly):
        return '----'
    myStream = QtCore.QTextStream(myFile)
    myHeader = myStream.readAll()
    myFile.close()
    return myHeader


def htmlFooter():
    """Get a standard html footer for wrapping content in."""
    myFile = QtCore.QFile(':/plugins/inasafe/footer.html')
    if not myFile.open(QtCore.QIODevice.ReadOnly):
        return '----'
    myStream = QtCore.QTextStream(myFile)
    myFooter = myStream.readAll()
    myFile.close()
    return myFooter


def qgisVersion():
    """Get the version of QGIS
   Args:
       None
    Returns:
        QGIS Version where 10700 represents QGIS 1.7 etc.
    Raises:
       None
    """
    myVersion = None
    try:
        myVersion = unicode(QGis.QGIS_VERSION_INT)  # pylint: disable=E1101
    except AttributeError:
        myVersion = unicode(QGis.qgisVersion)[0]  # pylint: disable=E1101
    myVersion = int(myVersion)
    return myVersion
