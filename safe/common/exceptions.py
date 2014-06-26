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

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '17/06/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class InaSAFEError(RuntimeError):
    """Base class for all user defined exceptions"""
    suggestion = 'An unspecified error occurred.'


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
