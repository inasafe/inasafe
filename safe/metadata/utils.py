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
from safe.metadata.property.character_string_property import \
    CharacterStringProperty
from safe.metadata.property.url_property import UrlProperty

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.metadata.property.date_property import DateProperty


# XML to python types conversions
TYPE_CONVERSIONS = {
    'gco:CharacterString': CharacterStringProperty,
    'gco:Date': DateProperty,
    'gmd:URL': UrlProperty
}
