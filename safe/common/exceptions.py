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

from safe.messaging.item.message_element import MessageElement

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '17/06/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class InaSAFEError(RuntimeError):

    """Base class for all user defined exceptions."""

    suggestion = 'An unspecified error occurred.'

    def __init__(self, message=None):
        """General constructor.

        :param message: The optional error message.
        :type message: str, unicode, MessageElement
        """
        if isinstance(message, str):
            super(InaSAFEError, self).__init__(message)

        elif isinstance(message, MessageElement):
            super(InaSAFEError, self).__init__(message.to_text())

        elif message is None:
            pass

        elif isinstance(message, BaseException):
            super(InaSAFEError, self).__init__(str(message))
        # This shouldn't happen...
        else:
            raise TypeError


class ReadLayerError(InaSAFEError):

    """When a layer can't be read."""

    suggestion = (
        'Check that the file exists and you have permissions to read it')


class WriteLayerError(InaSAFEError):

    """When a layer can't be written."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class BoundingBoxError(InaSAFEError):

    """For errors relating to bboxes."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class VerificationError(InaSAFEError):

    """Exception thrown by verify()"""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class PolygonInputError(InaSAFEError):

    """For invalid inputs to numeric polygon functions."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class PointsInputError(InaSAFEError):

    """For invalid inputs to numeric point functions."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class BoundsError(InaSAFEError):

    """For points falling outside interpolation grid."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class GetDataError(InaSAFEError):

    """When layer data cannot be obtained."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class WindowsError(InaSAFEError):

    """For windows specific errors."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class GridXmlFileNotFoundError(InaSAFEError):

    """An exception for when an grid.xml could not be found"""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class GridXmlParseError(InaSAFEError):

    """An exception for when something went wrong parsing the grid.xml """

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class ContourCreationError(InaSAFEError):

    """An exception for when creating contours from shakemaps goes wrong."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class InvalidLayerError(InaSAFEError):

    """Raised when a gis layer is invalid."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class ZeroImpactException(InaSAFEError):

    """Raised if an impact function return zero impact."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class WrongDataTypeException(InaSAFEError):

    """Raised if expected and received data types are different."""

    suggestion = 'Please ask the developers of InaSAFE to add a suggestion.'


class InvalidClipGeometryError(InaSAFEError):

    """Custom exception for when clip geometry is invalid."""

    pass


class SpatialIndexCreationError(InaSAFEError):

    """Custom exception for when a spatial index failed to be created."""

    pass


class FileNotFoundError(InaSAFEError):

    """Custom exception for when a file could not be found."""

    pass


class FunctionParametersError(InaSAFEError):

    """Custom exception for when function parameters are not valid."""

    pass


class KeywordDbError(InaSAFEError):

    """Custom exception for when an error is encountered with keyword cache db.
    """

    pass


class WrongEarthquakeFunction(InaSAFEError):

    """Earthquake function to recognised."""

    pass


class KeywordNotFoundError(InaSAFEError):

    """Custom exception for when a keyword's key (e.g. unit) cannot be found.
    """

    def __init__(self, message, **kwargs):
        # Call the base class constructor with the parameters it needs
        super(KeywordNotFoundError, self).__init__(message)

        self.layer_name = kwargs.get('layer_name', 'Missing Layer Name')
        self.keyword = kwargs.get('keyword', 'Missing Keyword')


class HashNotFoundError(InaSAFEError):

    """Custom exception for when a no keyword hash can be found."""

    pass


class InvalidParameterError(InaSAFEError):

    """Custom exception for when an invalid parameter is passed to a function.
    """

    pass


class NoKeywordsFoundError(InaSAFEError):

    """Custom exception for when no keywords file exist for a layer."""

    pass


class TranslationLoadError(InaSAFEError):

    """Custom exception handler for whe translation file fails to load."""

    pass


class ComputationError(InaSAFEError):

    """Custom exception when a calculation went wrong."""

    pass


class NoFeaturesInExtentError(InaSAFEError):

    """An exception that gets thrown when no features are within the extent
    being clipped.
    """

    pass


class InvalidProjectionError(InaSAFEError):

    """An exception raised if a layer needs to be reprojected."""

    pass


class InsufficientOverlapError(InaSAFEError):

    """An exception raised if an error occurs during extent calculation
    because the bounding boxes do not overlap.
    """

    pass


class StyleError(InaSAFEError):

    """An exception relating to reading / generating GIS styles."""

    pass


class MemoryLayerCreationError(InaSAFEError):

    """Raised if an error occurs creating the cities file."""

    pass


class CallGDALError(InaSAFEError):

    """Raised if failed to call gdal command. Indicate by error message that is
    not empty.
    """

    pass


class FileMissingError(InaSAFEError):

    """Raised if a file cannot be found."""

    pass


class CanceledImportDialogError(InaSAFEError):

    """Raised if import process canceled."""

    pass


class InvalidGeometryError(InaSAFEError):

    """Custom exception for when a feature geometry is invalid or none."""

    pass


class UnsupportedProviderError(InaSAFEError):

    """For unsupported provider (e.g. openlayers plugin) encountered."""

    pass


class TemplateLoadingError(InaSAFEError):

    """Raised when loading the template is error."""

    pass


class DownloadError(InaSAFEError):

    """Raised when downloading file is error."""

    pass


class NoValidLayerError(InaSAFEError):

    """Raised when there no valid layer in inasafe."""

    pass


class InsufficientMemoryWarning(InaSAFEError):

    """Raised when there is a possible insufficient memory."""

    pass


class InvalidKeywordsForProcessingAlgorithm(InaSAFEError):

    """Raised if the algorithm don't have proper keywords to run."""

    pass


class InvalidExtentError(InaSAFEError):

    """Raised if an extent is not valid."""

    pass


class NoAttributeInLayerError(InaSAFEError):

    """Raised if the attribute not exists in the vector layer."""

    pass


class MetadataLayerConstraintError(InaSAFEError):

    """Raised if the metadata does not match with the IF base class.

    It means the layer constraint specified in the metadata is not supported
    by the base class
    """


class MetadataReadError(InaSAFEError):

    """When a metadata xml is not correctly formatted can't be read."""

    suggestion = (
        'Check that the file is correct')


class MetadataInvalidPathError(InaSAFEError):

    """When a path for a metadata xml is not correct."""

    suggestion = 'Check that the XML path of the property is correct'


class MetadataCastError(InaSAFEError):

    """When a path for a metadata xml is not correct."""

    suggestion = 'Check that the XML value is of the correct type'


class InvalidProvenanceDataError(InaSAFEError):

    """When a path for a metadata xml is not correct."""

    suggestion = 'Check that the IF produced all the required data'


class MissingMetadata(InaSAFEError):

    """When old version of metadata is not properly read."""

    pass


class MissingImpactReport(InaSAFEError):

    """When Impact Report do not have proper input."""

    pass


class ErrorDataStore(InaSAFEError):

    """When the datastore has an error."""

    pass


class InvalidWizardStep(InaSAFEError):

    """When there is an invalid wizard step."""

    pass


class ProcessingInstallationError(InaSAFEError):

    """When there is an error with Processing."""

    pass


class AlignRastersError(Exception):

    """Raised if alignment of hazard and exposure rasters failed."""

    pass


class MetadataConversionError(InaSAFEError):

    """When failed to convert metadata."""

    pass


class GeoNodeInstanceError(InaSAFEError):

    """When failed to access GeoNode instance (probably not valid)."""

    pass


class GeoNodeLoginError(InaSAFEError):

    """When failed to login to GeoNode instance."""

    pass


class GeoNodeLayerUploadError(InaSAFEError):

    """When failed to upload layer to GeoNode instance."""

    pass
