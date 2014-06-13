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
    PostProcessorError,
    get_plugins, get_version,
    in_and_outside_polygon as points_in_and_outside_polygon,
    calculate_polygon_centroid,
    get_postprocessors,
    get_postprocessor_human_name,
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
    styles,
    feature_attributes_as_dict,
    get_utm_epsg,
    which)
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


def tr(text):
    """We define a tr() alias here since the is_safe_interface implementation
    below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    context = "@default"
    return QCoreApplication.translate(context, text)


def verify(statement, message=None):
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
        verify_util(statement, message)
    except:
        raise


def get_optimal_extent(
        hazard_geo_extent, exposure_geo_extent, view_port_geo_extent=None):
    """ A helper function to determine what the optimal extent is.
    Optimal extent should be considered as the intersection between
    the three inputs. The inasafe library will perform various checks
    to ensure that the extent is tenable, includes data from both
    etc.

    This is just a thin wrapper around safe.api.bbox_intersection.

    Typically the result of this function will be used to clip
    input layers to a commone extent before processing.

    Args:

        * hazard_geo_extent - an array representing the hazard layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * exposure_geo_extent - an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
        * view_port_geo_extent (optional) - an array representing the viewport
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
    message = tr(
        'theHazardGeoExtent or theExposureGeoExtent cannot be None.Found: '
        '/ntheHazardGeoExtent: %s /ntheExposureGeoExtent: %s' %
        (hazard_geo_extent, exposure_geo_extent))

    if (hazard_geo_extent is None) or (exposure_geo_extent is None):
        raise BoundingBoxError(message)

    # .. note:: The bbox_intersection function below assumes that
    #           all inputs are in EPSG:4326
    optimal_extent = bbox_intersection(
        hazard_geo_extent, exposure_geo_extent, view_port_geo_extent)

    if optimal_extent is None:
        # Bounding boxes did not overlap
        message = tr(
            'Bounding boxes of hazard data, exposure data and viewport did '
            'not overlap, so no computation was done. Please make sure you '
            'pan to where the data is and that hazard and exposure data '
            'overlaps.')
        raise InsufficientOverlapError(message)

    return optimal_extent


def get_buffered_extent(geo_extent, cell_size):
    """Grow bounding box with one unit of resolution in each direction.

    Args:

        * geo_extent - Bounding box with format [W, S, E, N]
        * cell_size - (resx, resy) Raster resolution in each direction.

        If resolution is None bbox is returned unchanged.

    Returns:
        Adjusted bounding box

    Raises:
        Any exceptions are propogated

    Note: See docstring for underlying function buffered_bounding_box
          for more details.
    """
    try:
        return buffered_bounding_box(geo_extent, cell_size)
    except:
        raise


def available_functions(keyword_list=None):
    """ Query the inasafe engine to see what plugins are available.

    Args:

       keyword_list - an optional parameter which should contain
       a list of 2 dictionaries (the number of items in the list
       is not enforced). The dictionaries should be obtained by using
       readKeywordsFromFile e.g.::

           myFile1 = foo.shp
           myFile2 = bar.asc
           keywords1 = readKeywordsFromFile(myFile1)
           keywords2 = readKeywordsFromFile(myFile2)
           myList = [keywords1, keywords2]
           myFunctions = available_functions(myList)

    Returns:
       A dictionary of strings where each is a plugin name.

       .. note:: If keyword_list is not provided, all available
        plugins will be returned in the list.

    Raises:
       NoFunctionsFoundError if no functions are found.
    """
    try:
        dictionary = get_admissible_plugins(keyword_list)
        #if len(dictionary) < 1:
        #    message = 'No InaSAFE impact functions could be found'
        #    raise NoFunctionsFoundError(message)
        return dictionary
    except:
        raise


def read_keywords_from_layer(layer, keyword):
    """Get metadata from the keywords file associated with a layer.

    .. note:: Requires a inasafe layer instance as parameter.
    .. seealso:: getKeywordFromPath

    Args:

       * layer - a InaSAFE layer (vector or raster)
       * keyword - the metadata keyword to retrieve e.g. 'title'

    Returns:
       A string containing the retrieved value for the keyword.

    Raises:
       KeywordNotFoundError if the keyword is not recognised.
    """
    if layer is None:
        raise InvalidParameterError()
    try:
        value = layer.get_keywords(keyword)
    except Exception, e:
        message = tr(
            'Keyword retrieval failed for %s (%s) \n %s' % (
                layer.get_filename(), keyword, str(e)))
        raise KeywordNotFoundError(message)
    if not value or value == '':
        message = tr('No value was found for keyword %s in layer %s' % (
            layer.get_filename(), keyword))
        raise KeywordNotFoundError(message)
    return value


def read_file_keywords(layer_path, keyword=None):
    """Get metadata from the keywords file associated with a local
     file in the file system.

    .. note:: Requires a str representing a file path instance
              as parameter As opposed to read_keywords_from_layer which
              takes a inasafe file object as parameter.

    .. seealso:: read_keywords_from_layer

    :param: layer_path: a string representing a path to a layer
           (e.g. '/tmp/foo.shp', '/tmp/foo.tif')
    :type layer_path: str

    :param keyword: optional - the metadata keyword to retrieve e.g. 'title'
    :type keyword: str

    :return: A string containing the retrieved value for the keyword if
             the keyword argument is specified, otherwise the
             complete keywords dictionary is returned.

    :raises: KeywordNotFoundError, NoKeywordsFoundError, InvalidParameterError

    Note:
        * KeywordNotFoundError - occurs when the keyword is not recognised.
        * NoKeywordsFoundError - occurs when no keyword file exists.
        * InvalidParameterError - occurs when the layer does not exist.
    """
    # check the source layer path is valid
    if not os.path.isfile(layer_path):
        message = tr('Cannot get keywords from a non-existent file. File '
                     '%s does not exist.' % layer_path)
        raise InvalidParameterError(message)

    # check there really is a keywords file for this layer
    keyword_file_path = os.path.splitext(layer_path)[0]
    keyword_file_path += '.keywords'
    if not os.path.isfile(keyword_file_path):
        message = tr('No keywords file found for %s' % keyword_file_path)
        raise NoKeywordsFoundError(message)

    # now get the requested keyword using the inasafe library
    try:
        dictionary = read_keywords(keyword_file_path)
    except Exception, e:
        message = tr(
            'Keyword retrieval failed for %s (%s) \n %s' % (
                keyword_file_path, keyword, str(e)))
        raise KeywordNotFoundError(message)

    # if no keyword was supplied, just return the dict
    if keyword is None:
        return dictionary
    if not keyword in dictionary:
        message = tr('No value was found in file %s for keyword %s' % (
            keyword_file_path, keyword))
        raise KeywordNotFoundError(message)

    try:
        value = dictionary[keyword]
    except:
        raise
    return value


def write_keywords_to_file(filename, keywords):
    """Thin wrapper around the safe write_keywords function.

    Args:
        * filename - str representing path to layer that must be written.
          If the file does not end in .keywords, its extension will be
          stripped off and the basename + .keywords will be used as the file.
        * keywords - a dictionary of keywords to be written
    Returns:
        None
    Raises:
        Any exceptions are propogated
    """
    basename, extension = os.path.splitext(filename)
    if 'keywords' not in extension:
        filename = basename + '.keywords'
    try:
        safe_write_keywords(keywords, filename)
    except:
        raise


def get_style_info(layer):
    """Get styleinfo associated with a layer.

    Args:

       * layer - InaSAFE layer (raster or vector)

    Returns:
       A list of dictionaries containing styleinfo info for a layer.

    Raises:

       * StyleInfoNotFoundError if the style is not found.
       * InvalidParameterError if the paramers are not correct.
    """

    if not layer:
        raise InvalidParameterError()

    if not hasattr(layer, 'get_style_info'):
        message = tr('Argument "%s" was not a valid layer instance' % layer)
        raise StyleInfoNotFoundError(message)

    try:
        value = layer.get_style_info()
    except Exception, e:
        message = tr('Styleinfo retrieval failed for %s\n %s' % (
            layer.get_filename(), str(e)))
        raise StyleInfoNotFoundError(message)

    if not value or value == '':
        message = tr('No styleInfo was found for layer %s' % (
            layer.get_filename()))
        raise StyleInfoNotFoundError(message)
    return value


def make_ascii(x):
    """Convert QgsString to ASCII"""
    x = unicode(x)
    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
    return x


def read_safe_layer(path):
    """Thin wrapper around the safe read_layer function.

    Args:
        path - str representing path to layer that must be opened.
    Returns:
        A safe read_safe_layer object is returned.
    Raises:
        Any exceptions are propogated
    """
    try:
        return safe_read_layer(make_ascii(path))
    except:
        raise


def convert_to_safe_layer(layer):
    """Thin wrapper around the safe read_layer function.

    Args:
        layer - QgsMapLayer or Safe layer.
    Returns:
        A safe read_safe_layer object is returned.
    Raises:
        Any exceptions are propogated
    """
    # FIXME (DK): it is a stub now.
    #   Do not call read_safe_layer, but write function
    #     safe.storage.core.convert_layer to convert QgsMapLayer to SAFE layer

    if isinstance(layer, Layer):
        return layer
    try:
        return read_safe_layer(layer.source())
    except:
        raise


def get_safe_impact_function(function=None):
    """Thin wrapper around the safe impact_functions function.

    Args:
        function - optional str giving a specific plugins name that should
        be fetched.
    Returns:
        A safe impact function is returned
    Raises:
        Any exceptions are propogated
    """
    try:
        return safe_get_plugins(make_ascii(function))
    except:
        raise


def get_safe_impact_function_type(function_id):
    """
    Args:
        function_id - str giving a specific plugins name that should be
        fetched.
    Returns:
        A str type of safe impact function is returned:
            'old-style' is "classic" safe impact function
            'qgis2.0'   is impact function with native qgis layers support
    Raises:
        Any exceptions are propogated
    """
    try:
        # Get an instance of the impact function and get the type
        function = get_safe_impact_function(function_id)[0][function_id]
        function = function()

        try:
            fun_type = function.get_function_type()
        except AttributeError:
            fun_type = 'old-style'
    except:
        raise

    return fun_type


def calculate_safe_impact(
        layers, function, extent=None, check_integrity=True):
    """Thin wrapper around the safe calculate_impact function.

    Args:
        * layers - a list of layers to be used. They should be ordered
          with hazard layer first and exposure layer second.
        * function - SAFE impact function instance to be used
        * extent - List of [xmin, ymin, xmax, ymax]
                the coordinates of the bounding box.
        * check_integrity - If true, perform checking of
                input data integrity before running
                impact calculation
    Returns:
        A safe impact function is returned
    Raises:
        Any exceptions are propogated
    """
    try:
        return safe_calculate_impact(
            layers,
            function,
            extent=extent,
            check_integrity=check_integrity)
    except:
        raise
