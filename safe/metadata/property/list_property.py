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

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '10/12/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import json
from types import NoneType

from safe.common.exceptions import MetadataCastError
from safe.metadata.property import BaseProperty


class ListProperty(BaseProperty):
    """
    A property that accepts date input
    """
    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [list, NoneType]

    def __init__(self, name, value, xml_path):
        super(ListProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        # the date types constructors already complain if a date is not valid.
        return True

    def cast_from_str(self, value):
        try:
            return json.loads(value)
        except ValueError as e:
            raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is list:
            return json.dumps(self.value)
        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
