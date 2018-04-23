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
from builtins import str
from types import NoneType
from safe.metadata35.property import BaseProperty

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class CharacterStringProperty(BaseProperty):

    """A property that accepts any type of input and stores it as string."""
    
    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [str, str, int, float, NoneType]

    def __init__(self, name, value, xml_path):
        if isinstance(value, str):
            value = str(value)
        super(CharacterStringProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        # any string sequence is valid.
        return True

    def cast_from_str(self, value):
        # return the original string
        return value

    @property
    def xml_value(self):
        if self.python_type is NoneType:
            return ''
        elif (self.python_type in self.allowed_python_types and
                      self.python_type != str):
            return str(self.value)
        elif self.python_type == str:
            return str(self.value)
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
