# coding=utf-8

"""Metadata Constants."""

import os

from safe.metadata.property import (
    CharacterStringProperty,
    DateProperty,
    UrlProperty,
    DictionaryProperty,
    IntegerProperty,
    BooleanProperty,
    FloatProperty,
    ListProperty,
)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# XML to python types conversions
TYPE_CONVERSIONS = {
    'gco:CharacterString': CharacterStringProperty,
    'gco:Date': DateProperty,
    'gmd:URL': UrlProperty,
    'gco:Dictionary': DictionaryProperty,
    'gco:Integer': IntegerProperty,
    'gco:Boolean': BooleanProperty,
    'gco:Float': FloatProperty,
    'gco:List': ListProperty,
}
# XML Namespaces
METADATA_XML_TEMPLATE = os.path.join(
    os.path.dirname(__file__),
    '..',
    'metadata',
    'iso_19115_template.xml')
