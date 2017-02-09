# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Realtime Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '31/07/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class FileNotFoundError(Exception):
    """Exception for when a file could not be found."""
    pass


class EventIdError(Exception):
    """Exceptions relating to null or incorrect event id's"""
    pass


class EventUndefinedError(Exception):
    """Exception for when trying to work with an event that is not defined."""
    pass


class EventValidationError(Exception):
    """Exception for when an event is deemed to be invalid - typically for
    when no matching event can be located on the server or local filesystem
    cache."""
    pass


class InvalidInputZipError(Exception):
    """A exception for when the inp zip is invalid."""
    pass


class InvalidOutputZipError(Exception):
    """An exception for then the out zip is invalid."""
    pass


class ExtractionError(Exception):
    """An exception for when something went wrong extracting the event and mi
        datasets"""
    pass


class ContourCreationError(Exception):
    """An exception for when creating contours from shakemaps goes wrong"""
    pass


class GridXmlParseError(Exception):
    """An exception for when something went wrong parsing the grid.xml """
    pass


class GridXmlFileNotFoundError(Exception):
    """An exception for when an grid.xml could not be found"""
    pass


class InvalidLayerError(Exception):
    """Raised when a gis layer is invalid"""
    pass


class ShapefileCreationError(Exception):
    """Raised if an error occurs creating the cities file"""
    pass


class CityMemoryLayerCreationError(Exception):
    """Raised if an error occurs creating the cities memory layer"""
    pass


class MapComposerError(Exception):
    """Raised if a problem occurs rendering a map"""
    pass


class CopyError(Exception):
    """Raised if a problem occurs copying a file"""
    pass


class EmptyShakeDirectoryError(Exception):
    """Raised if the working directory does not contain any shakemaps."""
    pass


class RESTRequestFailedError(Exception):
    """Raised if a REST request is failed
    """

    def __init__(self, url=None, status_code=None, data=None, files=None):
        """
        :param url: the url of the request
        :param data: the data sent to the url
        """
        self.url = url
        self.status_code = status_code
        self.data = data
        self.files = files
        self.message = 'The request %s has failed with status code: ' \
                       '%d.\nData: %s\nFiles: %s' % \
                       (self.url, self.status_code, self.data, self.files)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.__unicode__()


class FloodDataSourceAPIError(Exception):
    """Raised if Flood Data Source REST API can't be accessed
    """
    pass
