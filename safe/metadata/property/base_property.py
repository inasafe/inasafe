# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from builtins import object
from future.utils import with_metaclass

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import abc

from safe.common.exceptions import MetadataInvalidPathError, MetadataCastError


class BaseProperty(with_metaclass(abc.ABCMeta, object)):
    """
    Abstract Metadata Property class, this has to be subclassed.

    This class represents the base for all properties. A property is a
    container with name, value, xml_path and allowed_python_types.

    properties are instantiated by checking the xml_type in the
    xml_path in BaseMetadata.

    Each property allows certain python data types and has to have an
    is_valid method to check if the passed value is ok.

    cast_from_str and xml_value need also to be implemented in the subclasses

    .. versionadded:: 3.2
    """

    def __init__(self, name, value, xml_path, allowed_python_types):

        # private members
        self._value = value
        self._allowed_python_types = allowed_python_types
        self._python_type = None
        self._xml_path = None

        # check if the desired xml path is correct
        if self._is_valid_xml_path(xml_path):
            self._xml_path = xml_path

        # check if the desired type is correct
        self.is_allowed_type(self._value)

        # check if value is valid
        self.is_valid(self.value)

        # public properties
        self.name = name
        self.value = value

    def __str__(self):
        return "%s: %s\n(%s)" % (self.name, self.value, self.xml_path)

    @property
    def dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'xml_path': self._xml_path,
            'python_type': self.python_type.__name__,
            'allowed_python_types': [t.__name__ for t in
                                     self.allowed_python_types]
        }

    def is_allowed_type(self, value):
        # pylint: disable=unidiomatic-typecheck
        if type(value) in self.allowed_python_types:
            self._python_type = type(value)
            self._value = value
            return True
        # pylint: disable=unidiomatic-typecheck
        elif type(value) in [str, str]:
            try:
                casted_value = self.cast_from_str(value)
                self.is_allowed_type(casted_value)
            except MetadataCastError as e:
                error_message = (
                    'We could not cast the string: "%s" to an allowed type '
                    '(valid types: %s' % (value, self.allowed_python_types))
                raise TypeError(error_message, e)
        else:
            error_message = (
                'The value %s (type: %s) is not of the correct type (valid'
                ' types: %s' % (value, type(value), self.allowed_python_types))
            raise TypeError(error_message)

    @abc.abstractmethod
    def is_valid(self, value):
        return

    @abc.abstractmethod
    def cast_from_str(self, value):
        return

    @abc.abstractproperty
    def xml_value(self):
        return

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.is_allowed_type(value):
            self._value = value

    @property
    # there is no setter because the type of a MetadataProperty should not
    # change overtime
    def python_type(self):
        return self._python_type

    @property
    # there is no setter because the allowed_python_types should not
    # change overtime
    def allowed_python_types(self):
        return self._allowed_python_types

    @property
    # there is no setter because the path of a MetadataProperty should not
    # change overtime
    def xml_path(self):
        return self._xml_path

    @staticmethod
    def _is_valid_xml_path(xml_path):
        # TODO (MB): maybe implement stronger check
        if isinstance(xml_path, str):
            return True
        else:
            raise MetadataInvalidPathError(
                'The xml path %s is invalid (type: %s)' % (
                    xml_path, type(xml_path)))
