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
__version__ = '0.3.0'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import traceback
import tempfile
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QCoreApplication
from qgis.core import (QGis,
                       QgsRasterLayer,
                       QgsMapLayer,
                       QgsCoordinateReferenceSystem,
                       QgsGraduatedSymbolRendererV2,
                       QgsSymbolV2,
                       QgsRendererRangeV2,
                       QgsSymbolLayerV2Registry,
                       QgsColorRampShader,
                       QgsRasterTransparency)
import sqlite3 as sqlite
import cPickle as pickle
from is_exceptions import (KeywordNotFoundException,
                           HashNotFoundException)
#do not remove this even if it is marked as unused by your IDE
import resources


def setVectorStyle(theQgisVectorLayer, style):
    """Set QGIS vector style based on InaSAFE style dictionary

    Input
        theQgisVectorLayer: Qgis layer
        style: Dictionary of the form as in the example below

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
    myTargetField = style['target_field']
    myClasses = style['style_classes']
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
        myMax = myClass['max']
        myMin = myClass['min']
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
            #check if range extrema are integers so we know if we can
            #use them to calculate a value range
            if ((myLastValue == int(myLastValue)) and (myMax == int(myMax))):
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


def getExceptionWithStacktrace(e, html=False):
    """Convert exception into a string and and stack trace

    Input
        e: Exception object
        html: Optional flat if output is to wrapped as html

    Output
        Exception with stack trace info suitable for display
    """

    info = ''.join(traceback.format_tb(sys.exc_info()[2]))
    errmsg = str(e)

    if not html:
        return errmsg + "\n" + info
    else:
        # Wrap string in html
        s = '<div>'
        s += tr('<span class="label label-warning">Problem:</span> ')
        s += errmsg
        s += ('</div>'
        '<div>'
        '<span class="label label-info" style="cursor:pointer;"'
        ' onclick="$(\'#traceback\').toggle();">')
        s += tr('Toggle traceback...')
        s += '</span>'
        s += ('<pre id="traceback" class="prettyprint"'
              ' style="display: none;">\n')
        s += info
        s += '</pre></div>'
        return s


def getTempDir(theSubDirectory=None):
    """Obtain the temporary working directory for the operating system.

    A inasafe subdirectory will automatically be created under this and
    if specified, a user subdirectory under that.

    Args:
        theSubDirectory - optional argument which will cause an additional
                subirectory to be created e.g. /tmp/inasafe/foo/

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       Any errors from the underlying system calls.
    """
    myDir = tempfile.gettempdir()
    if os.name is 'nt':  # Windows
        myDir = 'c://temp'
    elif os.name is 'posix':  # linux, osx
        myDir = '/tmp'
    myPath = os.path.join(myDir, 'inasafe')
    if theSubDirectory is not None:
        myPath = os.path.join(myPath, 'theSubDirectory')
    if not os.path.exists(myPath):
        os.makedirs(myPath)

    return myPath


def getWGS84resolution(theLayer, theGeoExtent=None):
    """Return resolution of raster layer in EPSG:4326

    Input
        theLayer: Raster layer
        theGeoExtent: Bounding box in EPSG:4326
        # FIXME (Ole), the second argumunt should be obtained within
                       this function to make it independent
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
        myGeoCrs.createFromEpsg(4326)

        # Estimate cellsize
        # FIXME (Ole): Get geoextent from layer
        myColumns = theLayer.width()
        myGeoWidth = abs(theGeoExtent[3] - theGeoExtent[0])
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


def getHashForDatasource(theDataSource):
    """
    Args:
        None
    Returns:
        None
    Raises:
        None
    """
    import hashlib
    myHash = hashlib.md5()
    myHash.update(theDataSource)
    myHash = myHash.hexdigest()
    return myHash


def getCursor(theConnection):
    """Get a cursor for the active connection. The cursor can be used to
    execute arbitrary queries against the database. This method also checks
    that the keywords table exists in the schema, and if not, it creates it.
    Args:
        theConnection - a valid, open sqlite3 database connection.
    Returns:
        a valid cursor opened against the connection.
    Raises:
        An sqlite.Error will be raised if anything goes wrong
    """
    try:
        myCursor = theConnection.cursor()
        myCursor.execute('SELECT SQLITE_VERSION()')
        myData = myCursor.fetchone()
        #print "SQLite version: %s" % myData
        # Check if we have some tables, if not create them
        mySQL = 'select sql from sqlite_master where type = \'table\';'
        myCursor.execute(mySQL)
        myData = myCursor.fetchone()
        #print "Tables: %s" % myData
        if myData is None:
            print 'No tables found'
            mySQL = ('create table keyword (hash varchar(32) primary key,'
                     'dict text);')
            print mySQL
            myCursor.execute(mySQL)
            myData = myCursor.fetchone()
        else:
            print 'Keywords table already exists'
            pass
        return myCursor
    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
        raise


def defaultKeywordDbPath():
    """Helper to get the default path for the keywords file (which is
    <plugin dir>/keywords.db
    Args:
        None
    Returns:
        A string representing the path to where the keywords file is to be.
    Raises:
        None
    """
    myParentDir = os.path.abspath(
                                os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(myParentDir, 'keywords.db')


def openConnection(thePath=None):
    """Open an sqlite connection to the keywords database.
    By default the keywords database will be used in the plugin dir,
    unless an explicit path is provided. If the db does not exist it will
    be created.
    Args:
        thePath - path to the desired sqlite db to use.
    Returns:
        A valid open connection to the sqlite database
    Raises:
        An sqlite.Error is raised if anything goes wrong
    """
    myConnection = None
    if thePath is None:
        thePath = defaultKeywordDbPath()
    try:
        myConnection = sqlite.connect(thePath)
    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
        raise
    return myConnection


def closeConnection(theConnection):
    """Given an sqlite3 connection, close it
    Args:
        theConnection - an open SQLITE connection
    Returns:
        None
    Raises:
        None
    """
    if theConnection:
        theConnection.close()


def deleteKeywordsForUri(theUri, theDatabasePath=None):
    """Delete keywords for a URI in the keywords database.
    A hash will be constructed from the supplied uri and a lookup made
    in a local SQLITE database for the keywords. If there is an existing
    record for the hash, the entire record will be erased.

    .. seealso:: writeKeywordsForUri, readKeywordsForUri

    Args:

       * theUri -  a str representing a layer uri as parameter.
         .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
       * theDatabasePath - optional string giving path to the sqlite
         database to use. If the database does not exist it will be
         created.

    Returns:
       None

    Raises:
       None
    """
    myHash = getHashForDatasource(theUri)
    myConnection = openConnection(theDatabasePath)
    try:
        myCursor = getCursor(myConnection)
        #now see if we have any data for our hash
        mySQL = 'delete from keyword where hash = \'' + myHash + '\';'
        myCursor.execute(mySQL)
        myConnection.commit()
    except sqlite.Error, e:
        print "SQLITE Error %s:" % e.args[0]
        myConnection.rollback()
    except Exception, e:
        print "Error %s:" % e.args[0]
        myConnection.rollback()
        raise
    finally:
        closeConnection(myConnection)


def writeKeywordsForUri(theUri, theKeywords, theDatabasePath=None):
    """Write keywords for a URI into the keywords database. All the
    keywords for the uri should be written in a single operation.
    A hash will be constructed from the supplied uri and a lookup made
    in a local SQLITE database for the keywords. If there is an existing
    record it will be updated, if not, a new one will be created.

    .. seealso:: readKeywordFromUri, deleteKeywordsForUri

    Args:

       * theUri -  a str representing a layer uri as parameter.
         .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
       * keywords - mandatory - the metadata keyword to retrieve e.g. 'title'
       * theDatabasePath - optional string giving path to the sqlite
         database to use. If the database does not exist it will be
         created.

    Returns:
       A string containing the retrieved value for the keyword if
       the keyword argument is specified, otherwise the
       complete keywords dictionary is returned.

    Raises:
       KeywordNotFoundException if the keyword is not recognised.
    """
    myHash = getHashForDatasource(theUri)
    myConnection = openConnection(theDatabasePath)
    try:
        myCursor = getCursor(myConnection)
        #now see if we have any data for our hash
        mySQL = 'select dict from keyword where hash = \'' + myHash + '\';'
        myCursor.execute(mySQL)
        myData = myCursor.fetchone()
        myPickle = pickle.dumps(theKeywords, pickle.HIGHEST_PROTOCOL)
        if myData is None:
            #insert a new rec
            #myCursor.execute('insert into keyword(hash) values(:hash);',
            #             {'hash': myHash})
            myCursor.execute('insert into keyword(hash, dict) values('
                             ':hash, :dict);',
                         {'hash': myHash, 'dict': sqlite.Binary(myPickle)})
            myConnection.commit()
        else:
            #update existing rec
            myCursor.execute('update keyword set dict=? where hash = ?;',
                         (sqlite.Binary(myPickle), myHash))
            myConnection.commit()
    except sqlite.Error, e:
        print "SQLITE Error %s:" % e.args[0]
        myConnection.rollback()
    except Exception, e:
        print "Error %s:" % e.args[0]
        myConnection.rollback()
        raise
    finally:
        closeConnection(myConnection)


def readKeywordFromUri(theUri, theKeyword=None, theDatabasePath=None):
    """Get metadata from the keywords file associated with a
    non local layer (e.g. postgresql connection).

    A hash will be constructed from the supplied uri and a lookup made
    in a local SQLITE database for the keywords. If there is an existing
    record it will be returned, if not and error will be thrown.

    .. seealso:: writeKeywordsForUri,deleteKeywordsForUri

    Args:

       * theUri -  a str representing a layer uri as parameter.
         .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
       * keyword - optional - the metadata keyword to retrieve e.g. 'title'
       * theDatabasePath - optional string giving path to the sqlite
         database to use. If the database does not exist it will be
         created.

    Returns:
       A string containing the retrieved value for the keyword if
       the keyword argument is specified, otherwise the
       complete keywords dictionary is returned.

    Raises:
       KeywordNotFoundException if the keyword is not found.
    """
    myHash = getHashForDatasource(theUri)
    myConnection = openConnection(theDatabasePath)
    try:
        myCursor = getCursor(myConnection)
        #now see if we have any data for our hash
        mySQL = 'select dict from keyword where hash = \'' + myHash + '\';'
        myCursor.execute(mySQL)
        myData = myCursor.fetchone()
        #unpickle it to get our dict back
        if myData is None:
            raise HashNotFoundException('No hash found for %s' % myHash)
        myData = myData[0]  # first field
        myDict = pickle.loads(str(myData))
        if theKeyword is None:
            return myDict
        if theKeyword in myDict:
            return myDict[theKeyword]
        else:
            raise KeywordNotFoundException('No hash found for %s' % myHash)

    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
    except Exception, e:
        print "Error %s:" % e.args[0]
        raise
    finally:
        closeConnection(myConnection)
