# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. versionadded:: 3.2

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
from contextlib import contextmanager
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


def insert_xml_element(root, element_path):
    """insert an XML element in an other creating the needed parents.
    :param root: The container
    :type root: ElementTree.Element
    :param element_path: The path relative to root
    :type element_path: str
    :return: ElementTree.Element
    :rtype : ElementTree.Element
    """
    element_path = element_path.split('/')
    parent = root
    # iterate all parents of the missing element
    for level in range(len(element_path)):
        path = '/'.join(element_path[0:level + 1])
        tag = element_path[level]
        element = root.find(path, XML_NS)
        if element is None:
            # if a parent is missing insert it at the right place
            element = ElementTree.SubElement(parent, tag)
        parent = element
    return element

# MONKEYPATCH CDATA support into Element tree
def CDATA(text=None):
    """
    MONKEYPATCH CDATA support into Element tree.

    inspired by http://stackoverflow.com/questions/174890/#answer-8915039
    :param text: content of the element
    :return: cdata element
    :rtype: ElementTree.Element
    """
    element = ElementTree.Element('![CDATA[')
    element.text = text
    return element
ElementTree._original_serialize_xml = ElementTree._serialize_xml


def _serialize_xml(write, elem, encoding, qnames, namespaces):
    """
    serialize MONKEYPATCHED CDATA
    """

    if elem.tag == '![CDATA[':
        write("\n<%s%s]]>\n" % (elem.tag, elem.text))
        return
    return ElementTree._original_serialize_xml(
        write, elem, encoding, qnames, namespaces)

ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml
# END MONKEYPATCH CDATA


@contextmanager
def reading_ancillary_files(metadata):
    """
    context manager to be used when reading metadata so no errors are risen.

    This is useful because we want to be able to get as much as possible out
    of malformed input

    :param metadata: the metadata object
    :type metadata: BaseMetadata
    """
    metadata._reading_ancillary_file = True
    yield metadata
    metadata._reading_ancillary_file = False


def merge_dictionaries(base_dict, extra_dict):
    """
    merge two dictionaries.

    if both have a same key, the one from extra_dict is taken

    :param base_dict: first dictionary
    :type base_dict: dict
    :param extra_dict: second dictionary
    :type extra_dict: dict
    :return: a merge of the two dictionaries
    :rtype: dicts
    """
    new_dict = base_dict.copy()
    new_dict.update(extra_dict)
    return new_dict


def read_property_from_xml(root, path):
    """
    Get the text from an XML property.

    Whitespaces, tabs and new lines are trimmed

    :param root: container in which we search
    :type root: ElementTree.Element
    :param path: path to search in root
    :type path: str
    :return: the text of the element at the given path
    :rtype: str, None
    """
    element = root.find(path, XML_NS)
    try:
        return element.text.strip(' \t\n\r')
    except AttributeError:
        return None
