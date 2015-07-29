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

import os
from xml.etree import ElementTree
from safe.metadata.property import (
    CharacterStringProperty,
    DateProperty,
    UrlProperty)


# XML to python types conversions
TYPE_CONVERSIONS = {
    'gco:CharacterString': CharacterStringProperty,
    'gco:Date': DateProperty,
    'gmd:URL': UrlProperty
}

# XML Namespaces
XML_NS = {
    'gmi': 'http://www.isotc211.org/2005/gmi',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

METADATA_XML_TEMPLATE = os.path.join(
    os.path.dirname(__file__), 'iso_19115_template.xml')


ElementTree.register_namespace('gmi', XML_NS['gmi'])
ElementTree.register_namespace('gco', XML_NS['gco'])
ElementTree.register_namespace('gmd', XML_NS['gmd'])
ElementTree.register_namespace('xsi', XML_NS['xsi'])


def insert_xml_element(root, path_arr):
        path_arr = path_arr.split('/')
        parent = root
        # iterate all parents of the missing element
        for level in range(len(path_arr)):
            path = '/'.join(path_arr[0:level+1])
            tag = path_arr[level]
            element = root.find(path, XML_NS)
            if element is None:
                # if a parent is missing insert it at the right place
                element = ElementTree.SubElement(parent, tag)
            parent = element
        return element


# MONKEYPATCH CDATA support into Element tree
# inspired by http://stackoverflow.com/questions/174890/#answer-8915039
def CDATA(text=None):
    element = ElementTree.Element('![CDATA[')
    element.text = text
    return element
ElementTree._original_serialize_xml = ElementTree._serialize_xml


def _serialize_xml(write, elem, encoding, qnames, namespaces):
    # print "MONKEYPATCHED CDATA support into Element tree called"
    if elem.tag == '![CDATA[':
        write("\n<%s%s]]>\n" % (elem.tag, elem.text))
        return
    return ElementTree._original_serialize_xml(
        write, elem, encoding, qnames, namespaces)
ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml
# END MONKEYPATCH CDATA
