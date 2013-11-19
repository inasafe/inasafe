# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
**IS Safe Interface.**

The purpose of the module is to centralise interactions between the gui
package and the underlying InaSAFE packages. This should be the only place
where SAFE modules are imported directly.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '04/04/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


# Standard modules
import os
import unicodedata
import logging

# SAFE functionality - passed on to QGIS modules
# pylint: disable=W0611

# We want all these imports as they for part of the API wrapper used by other
# modules in safe_qgis
# noinspection PyUnresolvedReferences

from safe.api import (
    load_plugins,
    get_admissible_plugins,
    get_function_title,
    get_plugins as safe_get_plugins,
    read_keywords, bbox_intersection,
    write_keywords as safe_write_keywords,
    read_layer as safe_read_layer,
    buffered_bounding_box,
    verify as verify_util,
    VerificationError,
    InaSAFEError,
    temp_dir,
    unique_filename,
    safe_tr as safeTr,
    get_free_memory,
    calculate_impact as safe_calculate_impact,
    BoundingBoxError,
    GetDataError,
    ReadLayerError,
    get_plugins, get_version,
    in_and_outside_polygon as points_in_and_outside_polygon,
    calculate_polygon_centroid,
    get_postprocessors,
    get_postprocessor_human_name,
    convert_mmi_data,
    format_int,
    get_unique_values,
    get_plugins_as_table,
    evacuated_population_weekly_needs,
    Layer,
    Vector,
    Raster,
    nan_allclose,
    DEFAULTS,
    messaging,
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    ErrorMessage,
    ZeroImpactException,
    PointsInputError,
    get_decimal_separator,
    get_thousand_separator,
    styles)
# noinspection PyUnresolvedReferences
# hack for excluding test-related import in builded package

try:
    from safe.api import (
        HAZDATA, EXPDATA, TESTDATA, UNITDATA, BOUNDDATA)
except ImportError:
    pass
# pylint: enable=W0611

# InaSAFE GUI specific functionality
from PyQt4.QtCore import QCoreApplication
from safe_qgis.exceptions import (
    KeywordNotFoundError,
    StyleInfoNotFoundError,
    InvalidParameterError,
    InsufficientOverlapError,
    NoKeywordsFoundError)

LOGGER = logging.getLogger('InaSAFE')


def tr(theText):
    """We define a tr() alias here since the is_safe_interface implementation
    below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "@default"
    return QCoreApplication.translate(myContext, theText)


def verify(theStatement, theMessage=None):
    """This is just a thin wrapper around safe.api.verify.

    Args:
        * theStatement - expression to verify
        * theMessage - message to display on failure
    Returns:
        None
    Raises:
        VerificationError
    """
    try:
        verify_util(theStatement, theMessage)
    except:
        raise


def getOptimalExtent(
        theHazardGeoExtent,
        theExposureGeoExtent,
        theViewportGeoExtent=None):
    """ A helper function to determine what the optimal extent is.
    Optimal extent should be considered as the intersection between
    the three inputs. The inasafe library will perform various checks
    to ensure that the extent is tenable, includes data from both
    etc.

    This is just a thin wrapper around safe.api.bbox_intersection.

    Typically the result of this function will be used to clip
    input layers to a commone extent before processing.

    Args:

        * theHazardGeoExtent - an array representing the hazard layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * theExposureGeoExtent - an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * theViewPortGeoExtent (optional) - an array representing the viewport
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.

       ..note:: We do minimal checking as the inasafe library takes
         care of it for us.

    Returns:
       An array containing an extent in the form [xmin, ymin, xmax, ymax]
       e.g.::

          [100.03, -1.14, 100.81, -0.73]

    Raises:
        Any exceptions raised by the InaSAFE library will be propogated.
    """

    #
    myMessage = tr('theHazardGeoExtent or theExposureGeoExtent cannot be None.'
                   'Found: /ntheHazardGeoExtent: %s '
                   '/ntheExposureGeoExtent: %s' %
                   (theHazardGeoExtent, theExposureGeoExtent))

    if (theHazardGeoExtent is None) or (theExposureGeoExtent is None):
        raise BoundingBoxError(myMessage)

    # .. note:: The bbox_intersection function below assumes that
    #           all inputs are in EPSG:4326
    myOptimalExtent = \
        bbox_intersection(theHazardGeoExtent,
                          theExposureGeoExtent,
                          theViewportGeoExtent)

    if myOptimalExtent is None:
        # Bounding boxes did not overlap
        myMessage = \
            tr('Bounding boxes of hazard data, exposure data '
               'and viewport did not overlap, so no computation was '
               'done. Please make sure you pan to where the data is and '
               'that hazard and exposure data overlaps.')
        raise InsufficientOverlapError(myMessage)

    return myOptimalExtent


def getBufferedExtent(theGeoExtent, theCellSize):
    """Grow bounding box with one unit of resolution in each direction.

    Args:

        * theGeoExtent - Bounding box with format [W, S, E, N]
        * theCellSize - (resx, resy) Raster resolution in each direction.

        If resolution is None bbox is returned unchanged.

    Returns:
        Adjusted bounding box

    Raises:
        Any exceptions are propogated

    Note: See docstring for underlying function buffered_bounding_box
          for more details.
    """
    try:
        return buffered_bounding_box(theGeoExtent, theCellSize)
    except:
        raise


def availableFunctions(theKeywordList=None):
    """ Query the inasafe engine to see what plugins are available.

    Args:

       theKeywordList - an optional parameter which should contain
       a list of 2 dictionaries (the number of items in the list
       is not enforced). The dictionaries should be obtained by using
       readKeywordsFromFile e.g.::

           myFile1 = foo.shp
           myFile2 = bar.asc
           myKeywords1 = readKeywordsFromFile(myFile1)
           myKeywords2 = readKeywordsFromFile(myFile2)
           myList = [myKeywords1, myKeywords2]
           myFunctions = availableFunctions(myList)

    Returns:
       A dictionary of strings where each is a plugin name.

       .. note:: If theKeywordList is not provided, all available
        plugins will be returned in the list.

    Raises:
       NoFunctionsFoundError if no functions are found.
    """
    try:
        myDict = get_admissible_plugins(theKeywordList)
        #if len(myDict) < 1:
        #    myMessage = 'No InaSAFE impact functions could be found'
        #    raise NoFunctionsFoundError(myMessage)
        return myDict
    except:
        raise


def readKeywordsFromLayer(theLayer, keyword):
    """Get metadata from the keywords file associated with a layer.

    .. note:: Requires a inasafe layer instance as parameter.
    .. seealso:: getKeywordFromPath

    Args:

       * theLayer - a InaSAFE layer (vector or raster)
       * keyword - the metadata keyword to retrieve e.g. 'title'

    Returns:
       A string containing the retrieved value for the keyword.

    Raises:
       KeywordNotFoundError if the keyword is not recognised.
    """
    myValue = None
    if theLayer is None:
        raise InvalidParameterError()
    try:
        myValue = theLayer.get_keywords(keyword)
    except Exception, e:
        myMessage = \
            tr('Keyword retrieval failed for %s (%s) \n %s' % (
                theLayer.get_filename(), keyword, str(e)))
        raise KeywordNotFoundError(myMessage)
    if not myValue or myValue == '':
        myMessage = \
            tr('No value was found for keyword %s in layer %s' % (
                theLayer.get_filename(), keyword))
        raise KeywordNotFoundError(myMessage)
    return myValue


def read_file_keywords(theLayerPath, theKeyword=None):
    """Get metadata from the keywords file associated with a local
     file in the file system.

    .. note:: Requires a str representing a file path instance
              as parameter As opposed to readKeywordsFromLayer which
              takes a inasafe file object as parameter.

    .. seealso:: readKeywordsFromLayer

    Args:

       * theLayerPath - a string representing a path to a layer
           (e.g. '/tmp/foo.shp', '/tmp/foo.tif')
       * theKeyword - optional - the metadata keyword to retrieve e.g. 'title'

    Returns:
       A string containing the retrieved value for the keyword if
       the keyword argument is specified, otherwise the
       complete keywords dictionary is returned.

    Raises:
       KeywordNotFoundError if the keyword is not recognised.
       NoKeywordsFoundError if no keyword file exists.
       InvalidParameterError if the layer does not exist.
    """
    # check the source layer path is valid
    if not os.path.isfile(theLayerPath):
        myMessage = tr('Cannot get keywords from a non-existent file.'
                       '%s does not exist.' % theLayerPath)
        raise InvalidParameterError(myMessage)

    # check there really is a keywords file for this layer
    myKeywordFilePath = os.path.splitext(theLayerPath)[0]
    myKeywordFilePath += '.keywords'
    if not os.path.isfile(myKeywordFilePath):
        myMessage = tr('No keywords file found for %s' % myKeywordFilePath)
        raise NoKeywordsFoundError(myMessage)

    # now get the requested keyword using the inasafe library
    myDictionary = None
    try:
        myDictionary = read_keywords(myKeywordFilePath)
    except Exception, e:
        myMessage = \
            tr('Keyword retrieval failed for %s (%s) \n %s' % (
                myKeywordFilePath, theKeyword, str(e)))
        raise KeywordNotFoundError(myMessage)

    # if no keyword was supplied, just return the dict
    if theKeyword is None:
        return myDictionary
    if not theKeyword in myDictionary:
        myMessage = \
            tr('No value was found in file %s for keyword %s' % (
                myKeywordFilePath, theKeyword))
        raise KeywordNotFoundError(myMessage)

    try:
        myValue = myDictionary[theKeyword]
    except:
        raise
    return myValue


def writeKeywordsToFile(theFilename, theKeywords):
    """Thin wrapper around the safe write_keywords function.

    Args:
        * thePath - str representing path to layer that must be written.
          If the file does not end in .keywords, its extension will be
          stripped off and the basename + .keywords will be used as the file.
        * theKeywords - a dictionary of keywords to be written
    Returns:
        None
    Raises:
        Any exceptions are propogated
    """
    myBasename, myExtension = os.path.splitext(theFilename)
    if 'keywords' not in myExtension:
        theFilename = myBasename + '.keywords'
    try:
        safe_write_keywords(theKeywords, theFilename)
    except:
        raise


def getStyleInfo(theLayer):
    """Get styleinfo associated with a layer.

    Args:

       * theLayer - InaSAFE layer (raster or vector)

    Returns:
       A list of dictionaries containing styleinfo info for a layer.

    Raises:

       * StyleInfoNotFoundError if the style is not found.
       * InvalidParameterError if the paramers are not correct.
    """

    if not theLayer:
        raise InvalidParameterError()

    if not hasattr(theLayer, 'get_style_info'):
        myMessage = \
            tr('Argument "%s" was not a valid layer instance' %
               theLayer)
        raise StyleInfoNotFoundError(myMessage)

    try:
        myValue = theLayer.get_style_info()
    except Exception, e:
        myMessage = \
            tr('Styleinfo retrieval failed for %s\n %s' % (
                theLayer.get_filename(), str(e)))
        raise StyleInfoNotFoundError(myMessage)

    if not myValue or myValue == '':
        myMessage = \
            tr('No styleInfo was found for layer %s' % (
                theLayer.get_filename()))
        raise StyleInfoNotFoundError(myMessage)
    return myValue


def makeAscii(x):
    """Convert QgsString to ASCII"""
    x = unicode(x)
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
    return x


def readSafeLayer(thePath):
    """Thin wrapper around the safe read_layer function.

    Args:
        thePath - str representing path to layer that must be opened.
    Returns:
        A safe readSafeLayer object is returned.
    Raises:
        Any exceptions are propogated
    """
    try:
        return safe_read_layer(makeAscii(thePath))
    except:
        raise


def convertToSafeLayer(layer):
    """Thin wrapper around the safe read_layer function.

    Args:
        layer - QgsMapLayer or Safe layer.
    Returns:
        A safe readSafeLayer object is returned.
    Raises:
        Any exceptions are propogated
    """
    # FIXME (DK): it is a stub now.
    #   Do not call readSafeLayer, but write function
    #     safe.storage.core.convert_layer to convert QgsMapLayer to SAFE layer

    if isinstance(layer, Layer):
        return layer
    try:
        return readSafeLayer(layer.source())
    except:
        raise


def getSafeImpactFunctions(theFunction=None):
    """Thin wrapper around the safe impact_functions function.

    Args:
        theFunction - optional str giving a specific plugins name that should
        be fetched.
    Returns:
        A safe impact function is returned
    Raises:
        Any exceptions are propogated
    """
    try:
        return safe_get_plugins(makeAscii(theFunction))
    except:
        raise


def getSafeImpactFunctionType(function_id):
    """
    Args:
        function_id - str giving a specific plugins name that should be fetched.
    Returns:
        A str type of safe impact function is returned:
            'old-style' is "classic" safe impact function
            'qgis2.0'   is impact function with native qgis layers support
    Raises:
        Any exceptions are propogated
    """
    try:
        # Get an instance of the impact function and get the type
        my_function = getSafeImpactFunctions(function_id)[0][function_id]
        my_function = my_function()

        try:
            fun_type = my_function.get_function_type()
        except AttributeError:
            fun_type = 'old-style'
    except:
        raise

    return fun_type


def calculateSafeImpact(theLayers, theFunction):
    """Thin wrapper around the safe calculate_impact function.

    Args:
        * theLayers - a list of layers to be used. They should be ordered
          with hazard layer first and exposure layer second.
        * theFunction - SAFE impact function instance to be used
    Returns:
        A safe impact function is returned
    Raises:
        Any exceptions are propogated
    """
    try:
        return safe_calculate_impact(theLayers, theFunction)
    except:
        raise
