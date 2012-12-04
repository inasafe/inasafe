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


class QgisPathException(Exception):
    """Custom exception for when qgispath.txt could not be read."""
    pass


class TestNotImplementedException(Exception):
    """Custom exception for when a test exists only as a stub."""
    pass


class InsufficientParametersException(Exception):
    """Custom exception for when insufficient parameters have been set."""
    pass


class NoFunctionsFoundException(Exception):
    """Custom exception for when a no impact calculation
    functions can be found."""
    pass


class KeywordNotFoundException(Exception):
    """Custom exception for when a no keyword can be found."""
    pass


class HashNotFoundException(Exception):
    """Custom exception for when a no keyword hash can be found."""
    pass


class StyleInfoNotFoundException(Exception):
    """Custom exception for when a no styleInfo can be found."""
    pass


class InvalidParameterException(Exception):
    """Custom exception for when an invalid parameter is
    passed to a function."""
    pass


class TranslationLoadException(Exception):
    """Custom exception handler for whe translation file fails
    to load."""
    pass


class InvalidKVPException(Exception):
    """An exception raised when a key value pair is invalid -
    for example if the key of value is None or an empty string."""
    pass


class LegendLayerException(Exception):
    """An exception raised when trying to create a legend from
    a QgsMapLayer that does not have suitable characteristics to
    allow a legend to be created from it."""
    pass


class NoFeaturesInExtentException(Exception):
    """An exception that gets thrown when no features are within
    the extent being clipped."""
    pass


class InvalidProjectionException(Exception):
    """An exception raised if a layer needs to be reprojected."""
    pass


class InsufficientOverlapException(Exception):
    """An exception raised if an error occurs during extent calculation
    because the bounding boxes do not overlap."""
    pass


class InvalidBoundingBoxException(Exception):
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
#class memoryLayerCreationError(Exception):
#    """Raised if an error occurs creating the cities file"""
#    pass


class MethodUnavailableError(Exception):
    """Raised if the requested import cannot be performed dur to qgis being
    to old"""
    pass


class CallGDALError(Exception):
    """Raised if failed to call gdal command. Indicate by error message that is
    not empty"""
    pass
