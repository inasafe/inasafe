"""
InaSafe Disaster risk assessment tool developed by AusAid - **Exception Classes.**

Custom exception classes for the Riab application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '12/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class QgisPathException(Exception):
    """Custom exception for when qgispath.txt could not be read."""
    pass


class TestNotImplementedException(Exception):
    """Custom exception for when a test exists only as a stub."""
    pass


class InsufficientParametersException(Exception):
    """Custom exception for when a test exists only as a stub."""
    pass


class NoFunctionsFoundException(Exception):
    """Custom exception for when a no impact calculation
    functions can be found."""
    pass


class KeywordNotFoundException(Exception):
    """Custom exception for when a no keyword can be found."""
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
