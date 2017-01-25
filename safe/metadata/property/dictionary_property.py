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
__date__ = '03/12/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import json
from types import NoneType
from PyQt4.QtCore import QUrl, QDate, QDateTime, Qt
from datetime import datetime, date

from safe.common.exceptions import MetadataCastError
from safe.metadata.property import BaseProperty


class DictionaryProperty(BaseProperty):
    """A property that accepts dictionary input
    """
    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [dict, NoneType]

    def __init__(self, name, value, xml_path):
        super(DictionaryProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        return True

    def cast_from_str(self, value):
        try:
            value = json.loads(value)
            # Checking if the v is basestring, try to decode if it's json
            for k, v in value.items():
                if isinstance(v, basestring):
                    try:
                        # Try to get dictionary, if possible.
                        dictionary_value = json.loads(v)
                        if isinstance(dictionary_value, dict):
                            value[k] = dictionary_value
                        else:
                            pass
                    except ValueError:
                        # Try to get time, if possible.
                        try:
                            value[k] = datetime.strptime(
                                v, "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            pass
            return value
        except ValueError as e:
            raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is dict:
            try:
                return json.dumps(self.value)
            except (TypeError, ValueError):
                string_value = {}
                for k, v in self.value.items():
                    if isinstance(v, QUrl):
                        string_value[k] = v.toString()
                    elif isinstance(v, (QDate, QDateTime)):
                        string_value[k] = v.toString(Qt.ISODate)
                    elif isinstance(v, datetime):
                        string_value[k] = v.isoformat()
                    elif isinstance(v, date):
                        string_value[k] = v.isoformat()
                    elif isinstance(v, dict):
                        string_value[k] = json.dumps(v)
                    else:
                        string_value[k] = v
                return json.dumps(string_value)

        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
