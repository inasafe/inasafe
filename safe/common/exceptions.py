# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the SAFE library

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '17/06/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class InaSAFEError(RuntimeError):
    """Base class for all user defined exceptions"""
    suggestion = 'An unspecified error occurred.'


class ReadMetadataError(InaSAFEError):
    """When a metadata xml is not correctly formatted can't be read"""
    suggestion = (
        'Check that the file is correct')


class ReadLayerError(InaSAFEError):
    """When a layer can't be read"""
    suggestion = (
        'Check that the file exists and you have permissions to read it')


class WriteLayerError(InaSAFEError):
    """When a layer can't be written"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class BoundingBoxError(InaSAFEError):
    """For errors relating to bboxes"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class VerificationError(InaSAFEError):
    """Exception thrown by verify()
    """
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class PolygonInputError(InaSAFEError):
    """For invalid inputs to numeric polygon functions"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class PointsInputError(InaSAFEError):
    """For invalid inputs to numeric point functions"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class BoundsError(InaSAFEError):
    """For points falling outside interpolation grid"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class GetDataError(InaSAFEError):
    """When layer data cannot be obtained"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class PostProcessorError(Exception):
    """Raised when requested import cannot be performed if QGIS is too old."""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class WindowsError(Exception):
    """For windows specific errors."""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class GridXmlFileNotFoundError(Exception):
    """An exception for when an grid.xml could not be found"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class GridXmlParseError(Exception):
    """An exception for when something went wrong parsing the grid.xml """
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class ContourCreationError(Exception):
    """An exception for when creating contours from shakemaps goes wrong"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class InvalidLayerError(Exception):
    """Raised when a gis layer is invalid"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class ShapefileCreationError(Exception):
    """Raised if an error occurs creating the cities file"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class ZeroImpactException(Exception):
    """Raised if an impact function return zero impact"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class WrongDataTypeException(Exception):
    """Raised if expected and received data types are different"""
    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class RadiiException(Exception):
    """Raised if radii for volcano buffer is not as we expect."""
    suggestion = ('Please make sure the radii for volcano buffer are '
                  'monotonically increasing.')


class InvalidClipGeometryError(Exception):
    """Custom exception for when clip geometry is invalid."""
    pass


class FileNotFoundError(Exception):
    """Custom exception for when a file could not be found."""
    pass


class TestNotImplementedError(Exception):
    """Custom exception for when a test exists only as a stub."""
    pass


class InsufficientParametersError(Exception):
    """Custom exception for when insufficient parameters have been set."""
    pass


class NoFunctionsFoundError(Exception):
    """Custom exception for when a no impact calculation
    functions can be found."""
    pass


class KeywordDbError(Exception):
    """Custom exception for when an error is encountered with keyword cache db.
    """
    pass


class KeywordNotFoundError(Exception):
    """Custom exception for when a keyword's key (e.g. unit) cannot be found.
    """
    pass


class HashNotFoundError(Exception):
    """Custom exception for when a no keyword hash can be found."""
    pass


class StyleInfoNotFoundError(Exception):
    """Custom exception for when a no styleInfo can be found."""
    pass


class InvalidParameterError(Exception):
    """Custom exception for when an invalid parameter is passed to a function.
    """
    pass


class NoKeywordsFoundError(Exception):
    """Custom exception for when no keywords file exist for a layer.
    """
    pass


class TranslationLoadError(Exception):
    """Custom exception handler for whe translation file fails
    to load."""
    pass


class InvalidKVPError(Exception):
    """An exception raised when a key value pair is invalid -
    for example if the key of value is None or an empty string."""
    pass


class LegendLayerError(Exception):
    """An exception raised when trying to create a legend from
    a QgsMapLayer that does not have suitable characteristics to
    allow a legend to be created from it."""
    pass


class NoFeaturesInExtentError(Exception):
    """An exception that gets thrown when no features are within
    the extent being clipped."""
    pass


class InvalidProjectionError(Exception):
    """An exception raised if a layer needs to be reprojected."""
    pass


class InsufficientOverlapError(Exception):
    """An exception raised if an error occurs during extent calculation
    because the bounding boxes do not overlap."""
    pass


class InvalidBoundingBoxError(Exception):
    """An exception raised if an error occurs during extent calculation
    because one of the extents is invalid."""
    pass


class StyleError(Exception):
    """An exception relating to reading / generating GIS styles"""
    pass


# class ShapefileCreationError(Exception):
#     """Raised if an error occurs creating the cities file"""
#     pass
#
#
class MemoryLayerCreationError(Exception):
    """Raised if an error occurs creating the cities file"""
    pass


class MethodUnavailableError(Exception):
    """Raised if the requested import cannot be performed dur to qgis being
    to old"""
    pass


class CallGDALError(Exception):
    """Raised if failed to call gdal command. Indicate by error message that is
    not empty"""
    pass


class ImportDialogError(Exception):
    """Raised if import process failed."""
    pass


class FileMissingError(Exception):
    """Raised if a file cannot be found."""
    pass


class CanceledImportDialogError(Exception):
    """Raised if import process canceled"""
    pass


class InvalidAggregatorError(Exception):
    """Raised if aggregator state is not valid when trying to run it."""
    pass


class AggregationError(Exception):
    """Raised if aggregator state is not valid when trying to run it."""
    pass


class HelpFileMissingError(Exception):
    """Raised if a help file cannot be found."""
    pass


class InvalidGeometryError(Exception):
    """Custom exception for when a feature geometry is invalid or none."""
    pass


class UnsupportedProviderError(Exception):
    """For unsupported provider (e.g. openlayers plugin) encountered."""
    pass


class TemplateLoadingError(Exception):
    """Raised when loading the template is error."""
    pass


class TemplateElementMissingError(Exception):
    """Raised when some element ids are missing from template."""


class ReportCreationError(Exception):
    """Raised when error occurs during report generation."""
    pass


class EmptyDirectoryError(Exception):
    """Raised when output directory is empty string path."""
    pass


class DownloadError(Exception):
    """Raised when downloading file is error."""
    pass


class NoValidLayerError(Exception):
    """Raised when there no valid layer in inasafe."""
    pass


class InsufficientMemoryWarning(Exception):
    """Raised when there is a possible insufficient memory."""
    pass


class InvalidAggregationKeywords(Exception):
    """Raised when the aggregation keywords is invalid."""
    pass


class InvalidExtentError(Exception):
    """Raised if an extent is not valid."""
    pass
