# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '12/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# FIXME (Ole): Shouldn't at least some these move to safe.common.exceptions
#              so that they can be reused


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
    """Custom exception for when an error is encountered with keyword cach db.
    """
    pass


class KeywordNotFoundError(Exception):
    """Custom exception for when a no keyword can be found."""
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
    """Custom exception for when no keywords exist for a layer.
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


#class ShapefileCreationError(Exception):
#    """Raised if an error occurs creating the cities file"""
#    pass
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


class CanceledImportDialogError(Exception):
    """Raised if import process canceled"""
    pass


class InvalidAggregatorError(Exception):
    """Raised if aggregator state is not valid when trying to run it."""
    pass


class AggregatioError(Exception):
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


class InvalidLayerError(Exception):
    """For when an invalid layer is encountered."""
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
