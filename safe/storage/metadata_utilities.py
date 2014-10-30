# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import os

from shutil import copy2
from xml.etree import ElementTree

from safe.common.exceptions import ReadMetadataError

currentPath = os.path.abspath(os.path.dirname(__file__))
ISO_METADATA_XML_TEMPLATE = os.path.join(currentPath,
                                         'iso_19115_template.xml')

# list of tags to get to the inasafe keywords.
# this is stored in a list so it can be easily used in a for loop
ISO_METADATA_KW_NESTING = [
    '{http://www.isotc211.org/2005/gmd}identificationInfo',
    '{http://www.isotc211.org/2005/gmd}MD_DataIdentification',
    '{http://www.isotc211.org/2005/gmd}supplementalInformation',
    'inasafe_keywords']

# flat xpath for the keyword container tag
ISO_METADATA_KW_TAG = '/'.join(ISO_METADATA_KW_NESTING)

ElementTree.register_namespace('gmi', 'http://www.isotc211.org/2005/gmi')
ElementTree.register_namespace('gco', 'http://www.isotc211.org/2005/gco')
ElementTree.register_namespace('gmd', 'http://www.isotc211.org/2005/gmd')
ElementTree.register_namespace('xsi',
                               'http://www.w3.org/2001/XMLSchema-instance')


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
        write("\n<%s%s]]>%s\n" % (elem.tag, elem.text, elem.tail))
        return
    return ElementTree._original_serialize_xml(
        write, elem, encoding, qnames, namespaces)
ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml
# END MONKEYPATCH CDATA


def write_iso_metadata(keyword_filename):
    basename, _ = os.path.splitext(keyword_filename)
    xml_filename = basename + '.xml'
    with open(keyword_filename) as keyword_file:
        keyword_str = keyword_file.read()

    tree = valid_iso_xml(xml_filename)
    root = tree.getroot()

    keyword_element = root.find(ISO_METADATA_KW_TAG)
    # by now we should have a valid container
    if keyword_element is None:
        raise ReadMetadataError
    keyword_element.append(CDATA(keyword_str))

    tree.write(xml_filename, encoding="UTF-8")
    return xml_filename


def valid_iso_xml(xml_filename):
    if os.path.isfile(xml_filename):
        #the file already has an xml file, we need to check it's structure
        tree = ElementTree.parse(xml_filename)
        root = tree.getroot()
        tag_str = '.'
        parent = root

        # Look for the correct nesting
        for tag in ISO_METADATA_KW_NESTING:
            tag_str += '/' + tag
            element = root.find(tag_str)
            if element is None:
                element = ElementTree.SubElement(parent, tag)
            parent = element
    else:
        # We create the XML from our template.
        # No more checks are needed since the template must be correct ;)
        copy2(ISO_METADATA_XML_TEMPLATE, xml_filename)
        tree = ElementTree.parse(xml_filename)

    return tree
