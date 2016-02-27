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

# expose for nicer imports
from safe.metadata.property.base_property import BaseProperty
from safe.metadata.property.character_string_property import (
    CharacterStringProperty)
from safe.metadata.property.date_property import DateProperty
from safe.metadata.property.url_property import UrlProperty
from safe.metadata.property.dictionary_property import DictionaryProperty
from safe.metadata.property.integer_property import IntegerProperty
from safe.metadata.property.boolean_property import BooleanProperty
from safe.metadata.property.float_property import FloatProperty
from safe.metadata.property.list_property import ListProperty
from safe.metadata.property.tuple_property import TupleProperty
from safe.metadata.property.float_tuple_property import FloatTupleProperty
