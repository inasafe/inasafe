# coding=utf-8

"""Property init file."""

# expose for nicer imports
# pylint: disable=unused-import
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
# pylint: enable=unused-import

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'
