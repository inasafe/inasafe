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
__version__ = '0.5.0'
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


class NoKeywordsFoundError(InaSAFEError):
    """When no keywords could be found for a layer."""
    pass
