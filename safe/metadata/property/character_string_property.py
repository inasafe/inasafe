# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **metadata module.**

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


from safe.metadata.property.base_property import BaseProperty


class CharacterStringProperty(BaseProperty):
    # if you edit this you need to adapt accordingly xml_value and is_valid
    _allowed_python_types = [str, int, float]

    def __init__(self, name, value, xml_path, xml_type):
        super(CharacterStringProperty, self).__init__(
            name, value, xml_path, xml_type, self._allowed_python_types)

    def is_valid(self, value):
        # any string sequence is valid.
        return True

    @property
    def xml_value(self):
        if self.python_type in self.allowed_python_types:
            return str(self.value)
        else:
            raise RuntimeError('self._allowed_python_types and self.xml_value'
                               'are out of sync. This should never happen')
