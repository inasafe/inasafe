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


from types import NoneType

from qgis.PyQt.QtCore import QUrl

from safe.common.exceptions import MetadataCastError
from safe.metadata35.property import BaseProperty


class UrlProperty(BaseProperty):

    """A property that accepts urls"""

    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [QUrl, NoneType]

    def __init__(self, name, value, xml_path):
        super(UrlProperty, self).__init__(
            name, value, xml_path, self._allowed_python_types)

    @classmethod
    def is_valid(cls, value):
        # TODO (MB): this check could be a bit stronger
        if value is None or value.isValid():
            return True
        else:
            error = '%s is not a valid formatted URL' % value.toString()
            raise ValueError(error)

    def cast_from_str(self, value):
        try:
            value = QUrl(value)
            self.is_valid(value)
            return value
        except (TypeError, ValueError) as e:
            raise MetadataCastError(e)

    @property
    def xml_value(self):
        if self.python_type is QUrl:
            return self.value.toString()
        elif self.python_type is NoneType:
            return ''
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
