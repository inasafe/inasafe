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

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from datetime import datetime, date
NoneType = type(None)

from qgis.PyQt.QtCore import QDate, Qt, QDateTime

from safe.common.exceptions import MetadataCastError
from safe.metadata35.property import BaseProperty


class DateProperty(BaseProperty):

    """A property that accepts date input."""

    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [QDate, datetime, date, NoneType, QDateTime]

    def __init__(self, name, value, xml_path):
        super(DateProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        # the date types constructors already complain if a date is not valid.
        return True

    def cast_from_str(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except ValueError as e:
                    raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is QDate:
            return self.value.toString(Qt.ISODate)
        elif self.python_type is QDateTime:
            return self.value.toString(Qt.ISODate)
        elif self.python_type is date:
            return self.value.isoformat()
        elif self.python_type is datetime:
            return self.value.date().isoformat()
        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
