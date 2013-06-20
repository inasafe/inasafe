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
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import traceback
import logging
import uuid

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QCoreApplication

from qgis.core import (
    QGis,
    QgsRasterLayer,
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsVectorLayer,
    QgsFeature)

from safe_interface import ErrorMessage

from safe_qgis.exceptions import (
    MemoryLayerCreationError)

from safe_qgis.safe_interface import (
    DEFAULTS,
    safeTr,
    get_version,
    messaging as m)

from safe_interface import styles
INFO_STYLE = styles.INFO_STYLE

#do not remove this even if it is marked as unused by your IDE
#resources are used by htmlfooter and header the comment will mark it unused
#for pylint
# noinspection PyUnresolvedReferences
import safe_qgis.resources_rc  # pylint: disable=W0611

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
    return QCoreApplication.translate('@default', theText)


def getErrorMessage(theException, theContext=None, theSuggestion=None):
    """Convert exception into an ErrorMessage containing a stack trace.

    .. seealso:: https://github.com/AIFDR/inasafe/issues/577

    Args:
        * theException: Exception object.
        * theContext: Optional theContext message.

    Returns:
        ErrorMessage: with stack trace info suitable for display.
    """

    myTraceback = ''.join(traceback.format_tb(sys.exc_info()[2]))

    myProblem = m.Message(m.Text(theException.__class__.__name__))

    if str(theException) is None or str(theException) == '':
        myProblem.append = m.Text(tr('No details provided'))
    else:
        myProblem.append = m.Text(str(theException))

    mySuggestion = theSuggestion
    if mySuggestion is None and hasattr(theException, 'suggestion'):
        mySuggestion = theException.message

    myErrorMessage = ErrorMessage(
        myProblem,
        detail=theContext,
        suggestion=mySuggestion,
        traceback=myTraceback
    )

    myArgs = theException.args
    for myArg in myArgs:
        myErrorMessage.details.append(myArg)

    return myErrorMessage


def getWGS84resolution(theLayer):
    """Return resolution of raster layer in EPSG:4326

    Input
        theLayer: Raster layer
    Output
        resolution.

    If input layer is already in EPSG:4326, simply return the resolution
    If not, work it out based on EPSG:4326 representations of its extent
    """

    msg = tr(
        'Input layer to getWGS84resolution must be a raster layer. '
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
        myXForm = QgsCoordinateTransform(theLayer.crs(), myGeoCrs)
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
    """Get the version of QGIS.
   Args:
       None
    Returns:
        QGIS Version where 10700 represents QGIS 1.7 etc.
    Raises:
       None
    """
    try:
        myVersion = unicode(QGis.QGIS_VERSION_INT)
    except AttributeError:
        myVersion = unicode(QGis.qgisVersion)[0]
    myVersion = int(myVersion)
    return myVersion


def getLayerAttributeNames(theLayer, theAllowedTypes, theCurrentKeyword=None):
    """iterates over self.layer and returns all the attribute names of
       attributes that have int or string as field type and the position
       of the theCurrentKeyword in the attribute names list

    Args:
       * theAllowedTypes: list(Qvariant) - a list of QVariants types that are
            acceptable for the attribute.
            e.g.: [QtCore.QVariant.Int, QtCore.QVariant.String]
       * theCurrentKeyword - the currently stored keyword for the attribute

    Returns:
       * all the attribute names of attributes that have int or string as
            field type
       * the position of the theCurrentKeyword in the attribute names list,
            this is None if theCurrentKeyword is not in the lis of attributes
    Raises:
       no exceptions explicitly raised
    """

    if theLayer.type() == QgsMapLayer.VectorLayer:
        myProvider = theLayer.dataProvider()
        myProvider = myProvider.fields()
        myFields = []
        mySelectedIndex = None
        i = 0
        for f in myProvider:
            # show only int or string myFields to be chosen as aggregation
            # attribute other possible would be float
            if myProvider[f].type() in theAllowedTypes:
                myCurrentFieldName = myProvider[f].name()
                myFields.append(myCurrentFieldName)
                if theCurrentKeyword == myCurrentFieldName:
                    mySelectedIndex = i
                i += 1
        return myFields, mySelectedIndex
    else:
        return None, None


def getDefaults(theDefault=None):
    """returns a dictionary of defaults values to be used
        it takes the DEFAULTS from safe and modifies them according to qgis
        QSettings

    Args:
       * theDefault: a key of the defaults dictionary

    Returns:
       * A dictionary of defaults values to be used
       * or the default value if a key is passed
       * or None if the requested default value is not valid
    Raises:
       no exceptions explicitly raised
    """
    mySettings = QtCore.QSettings()
    myDefaults = DEFAULTS

    myDefaults['FEM_RATIO'] = mySettings.value(
        'inasafe/defaultFemaleRatio',
        DEFAULTS['FEM_RATIO']).toDouble()[0]

    if theDefault is None:
        return myDefaults
    elif theDefault in myDefaults:
        return myDefaults[theDefault]
    else:
        return None


def copyInMemory(vLayer, copyName=''):
    """Return a memory copy of a layer

    Input
        origLayer: layer
        copyName: the name of the copy
    Output
        memory copy of a layer

    """

    if copyName is '':
        copyName = vLayer.name() + ' TMP'

    if vLayer.type() == QgsMapLayer.VectorLayer:
        vType = vLayer.geometryType()
        if vType == QGis.Point:
            typeStr = 'Point'
        elif vType == QGis.Line:
            typeStr = 'Line'
        elif vType == QGis.Polygon:
            typeStr = 'Polygon'
        else:
            raise MemoryLayerCreationError('Layer is whether Point nor '
                                           'Line nor Polygon')
    else:
        raise MemoryLayerCreationError('Layer is not a VectorLayer')

    crs = vLayer.crs().authid().toLower()
    myUUID = str(uuid.uuid4())
    uri = '%s?crs=%s&index=yes&uuid=%s' % (typeStr, crs, myUUID)
    memLayer = QgsVectorLayer(uri, copyName, 'memory')
    memProvider = memLayer.dataProvider()

    vProvider = vLayer.dataProvider()
    vAttrs = vProvider.attributeIndexes()
    vFields = vProvider.fields()

    fields = []
    for i in vFields:
        fields.append(vFields[i])

    memProvider.addAttributes(fields)

    vProvider.select(vAttrs)
    ft = QgsFeature()
    while vProvider.nextFeature(ft):
        memProvider.addFeatures([ft])

    if qgisVersion() <= 10800:
        # Next two lines a workaround for a QGIS bug (lte 1.8)
        # preventing mem layer attributes being saved to shp.
        memLayer.startEditing()
        memLayer.commitChanges()

    return memLayer


def mmToPoints(theMM, theDpi):
    """Convert measurement in points to one in mm.

    Args:
        * theMM: int - distance in millimeters
        * theDpi: int - dots per inch in the print / display medium
    Returns:
        mm converted value
    Raises:
        Any exceptions raised by the InaSAFE library will be propagated.
    """
    myInchAsMM = 25.4
    myPoints = (theMM * theDpi) / myInchAsMM
    return myPoints


def pointsToMM(thePoints, theDpi):
    """Convert measurement in points to one in mm.

    Args:
        * thePoints: int - number of points in display / print medium
        * theDpi: int - dots per inch in the print / display medium
    Returns:
        mm converted value
    Raises:
        Any exceptions raised by the InaSAFE library will be propagated.
    """
    myInchAsMM = 25.4
    myMM = (float(thePoints) / theDpi) * myInchAsMM
    return myMM


def dpiToMeters(theDpi):
    """Convert dots per inch (dpi) to dots perMeters.

    Args:
        theDpi: int - dots per inch in the print / display medium
    Returns:
        int - dpm converted value
    Raises:
        Any exceptions raised by the InaSAFE library will be propagated.
    """
    myInchAsMM = 25.4
    myInchesPerM = 1000.0 / myInchAsMM
    myDotsPerM = myInchesPerM * theDpi
    return myDotsPerM


def setupPrinter(theFilename,
                 theResolution=300,
                 thePageHeight=297,
                 thePageWidth=210):
    """Create a QPrinter instance defaulted to print to an A4 portrait pdf

    Args:
        theFilename - filename for pdf generated using this printer
    Returns:
        None
    Raises:
        None
    """
    #
    # Create a printer device (we are 'printing' to a pdf
    #
    LOGGER.debug('InaSAFE Map setupPrinter called')
    myPrinter = QtGui.QPrinter()
    myPrinter.setOutputFormat(QtGui.QPrinter.PdfFormat)
    myPrinter.setOutputFileName(theFilename)
    myPrinter.setPaperSize(
        QtCore.QSizeF(thePageWidth, thePageHeight),
        QtGui.QPrinter.Millimeter)
    myPrinter.setFullPage(True)
    myPrinter.setColorMode(QtGui.QPrinter.Color)
    myPrinter.setResolution(theResolution)
    return myPrinter


def humaniseSeconds(theSeconds):
    """Utility function to humanise seconds value into e.g. 10 seconds ago.

    The function will try to make a nice phrase of the seconds count
    provided.

    .. note:: Currently theSeconds that amount to days are not supported.

    Args:
        theSeconds: int - mandatory seconds value e.g. 1100

    Returns:
        str: A humanised version of the seconds count.

    Raises:
        None
    """
    myDays = theSeconds / (3600 * 24)
    myDayModulus = theSeconds % (3600 * 24)
    myHours = myDayModulus / 3600
    myHourModulus = myDayModulus % 3600
    myMinutes = myHourModulus / 60

    if theSeconds < 60:
        return tr('%i seconds' % theSeconds)
    if theSeconds < 120:
        return tr('a minute')
    if theSeconds < 3600:
        return tr('%s minutes' % myMinutes)
    if theSeconds < 7200:
        return tr('over an hour')
    if theSeconds < 86400:
        return tr('%i hours and %i minutes' % (myHours, myMinutes))
    else:
        # If all else fails...
        return tr('%i days, %i hours and %i minutes' % (
            myDays, myHours, myMinutes))


def impactLayerAttribution(theKeywords, theInaSAFEFlag=False):
    """Make a little table for attribution of data sources used in impact.

    Args:
        * theKeywords: dict{} - a keywords dict for an impact layer.
        * theInaSAFEFlag: bool - whether to show a little InaSAFE promotional
            text in the attribution output. Defaults to False.

    Returns:
        Text: an snippet containing attribution information for the impact
            layer. If no keywords are present or no appropriate keywords are
            present, None is returned.

    Raises:
        None
    """
    if theKeywords is None:
        return None

    myJoinWords = ' - %s ' % tr('sourced from')
    myHazardDetails = tr('Hazard details')
    myHazardTitleKeyword = 'hazard_title'
    myHazardSourceKeyword = 'hazard_source'
    myExposureDetails = tr('Exposure details')
    myExposureTitleKeyword = 'exposure_title'
    myExposureSourceKeyword = 'exposure_source'

    if myHazardTitleKeyword in theKeywords:
        # We use safe translation infrastructure for this one (rather than Qt)
        myHazardTitle = safeTr(theKeywords[myHazardTitleKeyword])
    else:
        myHazardTitle = tr('Hazard layer')

    if myHazardSourceKeyword in theKeywords:
        # We use safe translation infrastructure for this one (rather than Qt)
        myHazardSource = safeTr(theKeywords[myHazardSourceKeyword])
    else:
        myHazardSource = tr('an unknown source')

    if myExposureTitleKeyword in theKeywords:
        myExposureTitle = theKeywords[myExposureTitleKeyword]
    else:
        myExposureTitle = tr('Exposure layer')

    if myExposureSourceKeyword in theKeywords:
        myExposureSource = theKeywords[myExposureSourceKeyword]
    else:
        myExposureSource = tr('an unknown source')

    myReport = m.Message()
    myReport.add(m.Heading(myHazardDetails, **INFO_STYLE))
    myReport.add(m.Paragraph(
        myHazardTitle,
        myJoinWords,
        myHazardSource))

    myReport.add(m.Heading(myExposureDetails, **INFO_STYLE))
    myReport.add(m.Paragraph(
        myExposureTitle,
        myJoinWords,
        myExposureSource))

    if theInaSAFEFlag:
        myReport.add(m.Heading(tr('Software notes'), **INFO_STYLE))
        myInaSAFEPhrase = tr(
            'This report was created using InaSAFE version %1. Visit '
            'http://inasafe.org to get your free copy of this software!'
            'InaSAFE has been jointly developed by BNPB, AusAid/AIFDRR & the '
            'World Bank').arg(get_version())

        myReport.add(m.Paragraph(m.Text(myInaSAFEPhrase)))
    return myReport


def addComboItemInOrder(theCombo, theItemText, theItemData=None):
    """Although QComboBox allows you to set an InsertAlphabetically enum
    this only has effect when a user interactively adds combo items to
    an editable combo. This we have this little function to ensure that
    combos are always sorted alphabetically.

    Args:
        * theCombo - combo box receiving the new item
        * theItemText - display text for the combo
        * theItemData - optional UserRole data to be associated with
          the item

    Returns:
        None

    Raises:

    ..todo:: Move this to utilities
    """
    mySize = theCombo.count()
    for myCount in range(0, mySize):
        myItemText = str(theCombo.itemText(myCount))
        # see if theItemText alphabetically precedes myItemText
        if cmp(str(theItemText).lower(), myItemText.lower()) < 0:
            theCombo.insertItem(myCount, theItemText, theItemData)
            return
        #otherwise just add it to the end
    theCombo.insertItem(mySize, theItemText, theItemData)


def isPolygonLayer(theLayer):
    """Tell if a QGIS layer is vector and its geometries are polygons.

   Args:
       the theLayer

    Returns:
        bool - true if the theLayer contains polygons

    Raises:
       None
    """
    try:
        return (theLayer.type() == QgsMapLayer.VectorLayer) and (
            theLayer.geometryType() == QGis.Polygon)
    except AttributeError:
        return False


def isPointLayer(theLayer):
    """Tell if a QGIS layer is vector and its geometries are points.

   Args:
       the theLayer

    Returns:
        bool - true if the theLayer is a point layer.

    Raises:
       None
    """
    try:
        return (theLayer.type() == QgsMapLayer.VectorLayer) and (
            theLayer.geometryType() == QGis.Point)
    except AttributeError:
        return False


def isRasterLayer(theLayer):
    """Check if a QGIS layer is raster.

   Args:
       theLayer

    Returns:
        bool - true if the theLayer is a raster

    Raises:
       None
    """
    try:
        return theLayer.type() == QgsMapLayer.RasterLayer
    except AttributeError:
        return False


def which(name, flags=os.X_OK):
    """Search PATH for executable files with the given name.

    ..note:: This function was taken verbatim from the twisted framework,
      licence available here:
      http://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/LICENSE

    On newer versions of MS-Windows, the PATHEXT environment variable will be
    set to the list of file extensions for files considered executable. This
    will normally include things like ".EXE". This fuction will also find files
    with the given name ending with any of these extensions.

    On MS-Windows the only flag that has any meaning is os.F_OK. Any other
    flags will be ignored.

    @type name: C{str}
    @param name: The name for which to search.

    @type flags: C{int}
    @param flags: Arguments to L{os.access}.

    @rtype: C{list}
    @param: A list of the full paths to files found, in the
    order in which they were found.
    """
    result = []
    #pylint: disable=W0141
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    #pylint: enable=W0141
    path = os.environ.get('PATH', None)
    # In c6c9b26 we removed this hard coding for issue #529 but I am
    # adding it back here in case the user's path does not include the
    # gdal binary dir on OSX but it is actually there. (TS)
    if sys.platform == 'darwin':  # Mac OS X
        myGdalPrefix = ('/Library/Frameworks/GDAL.framework/'
                        'Versions/1.9/Programs/')
        path = '%s:%s' % (path, myGdalPrefix)

    LOGGER.debug('Search path: %s' % path)

    if path is None:
        return []

    for p in path.split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)

    return result


def extentToGeoArray(theExtent, theSourceCrs):
    """Convert the supplied extent to geographic and return as an array.

    Args:
        * theExtent: QgsRectangle defining a spatial extent in any CRS
        * theSourceCrs: QgsCoordinateReferenceSystem for theExtent.

    Returns:
        list: a list in the form [xmin, ymin, xmax, ymax] where all
            coordinates provided are in Geographic / EPSG:4326.

    Raises:
        None
    """

    myGeoCrs = QgsCoordinateReferenceSystem()
    myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    myXForm = QgsCoordinateTransform(theSourceCrs, myGeoCrs)

    # Get the clip area in the layer's crs
    myTransformedExtent = myXForm.transformBoundingBox(theExtent)

    myGeoExtent = [myTransformedExtent.xMinimum(),
                   myTransformedExtent.yMinimum(),
                   myTransformedExtent.xMaximum(),
                   myTransformedExtent.yMaximum()]
    return myGeoExtent


def safeToQGISLayer(theLayer):
    """Helper function to read and validate layer.

    Args
        theLayer: Layer object as provided by InaSAFE engine.

    Returns
        validated QGIS layer or None

    Raises
        Exception if layer is not valid
    """

    myMessage = tr(
        'Input layer must be a InaSAFE spatial object. I got %1'
    ).arg(str(type(theLayer)))
    if not hasattr(theLayer, 'is_inasafe_spatial_object'):
        raise Exception(myMessage)
    if not theLayer.is_inasafe_spatial_object:
        raise Exception(myMessage)

    # Get associated filename and symbolic name
    myFilename = theLayer.get_filename()
    myName = theLayer.get_name()

    myQGISLayer = None
    # Read layer
    if theLayer.is_vector:
        myQGISLayer = QgsVectorLayer(myFilename, myName, 'ogr')
    elif theLayer.is_raster:
        myQGISLayer = QgsRasterLayer(myFilename, myName)

    # Verify that new qgis layer is valid
    if myQGISLayer.isValid():
        return myQGISLayer
    else:
        myMessage = tr('Loaded impact layer "%1" is not valid').arg(myFilename)
        raise Exception(myMessage)
