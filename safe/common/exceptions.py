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
    """Base class for all user defined execptions"""
    pass


class ReadLayerError(InaSAFEError):
    """When a layer can't be read"""
    pass


class WriteLayerError(InaSAFEError):
    """When a layer can't be written"""
    pass


class BoundingBoxError(InaSAFEError):
    """For errors relating to bboxes"""
    pass


class VerificationError(InaSAFEError):
    """Exception thrown by verify()
    """
    pass


class PolygonInputError(InaSAFEError):
    """For invalid inputs to numeric polygon functions"""
    pass


class BoundsError(InaSAFEError):
    """For points falling outside interpolation grid"""
    pass


class GetDataError(InaSAFEError):
    """When layer data cannot be obtained"""
    pass


class PostProcessorError(Exception):
    """Raised when requested import cannot be performed if QGIS is too old."""
    pass


class WindowsError(Exception):
    """For windows specific errors."""
    pass


class GridXmlFileNotFoundError(Exception):
    """An exception for when an grid.xml could not be found"""
    pass


class GridXmlParseError(Exception):
    """An exception for when something went wrong parsing the grid.xml """
    pass


class ContourCreationError(Exception):
    """An exception for when creating contours from shakemaps goes wrong"""
    pass


class InvalidLayerError(Exception):
    """Raised when a gis layer is invalid"""
    pass


class ShapefileCreationError(Exception):
    """Raised if an error occurs creating the cities file"""
    pass
