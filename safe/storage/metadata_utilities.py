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


import copy
import json
import os
import time

from xml.etree import ElementTree

from safe.common.exceptions import MetadataReadError
from safe.defaults import get_defaults
from safe.storage.iso_19115_template import ISO_METADATA_XML_TEMPLATE


# list of tags to get to the InaSAFE keywords.
# this is stored in a list so it can be easily used in a for loop
ISO_METADATA_KEYWORD_NESTING = [
    '{http://www.isotc211.org/2005/gmd}identificationInfo',
    '{http://www.isotc211.org/2005/gmd}MD_DataIdentification',
    '{http://www.isotc211.org/2005/gmd}supplementalInformation',
    'inasafe_keywords']

# flat xpath for the keyword container tag
ISO_METADATA_KEYWORD_TAG = '/'.join(ISO_METADATA_KEYWORD_NESTING)

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
        write("\n<%s%s]]>\n" % (elem.tag, elem.text))
        return
    return ElementTree._original_serialize_xml(
        write, elem, encoding, qnames, namespaces)
ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml
# END MONKEYPATCH CDATA


def write_keyword_in_iso_metadata(keyword_filename):
    """Write keywords in an xml file at the same location as the keyword  file

    :param keyword_filename: Name of keywords file.
    :type keyword_filename: str

    :returns: xml_filename: the path of the xml file

    :raises: ReadMetadataError
    """

    basename, _ = os.path.splitext(keyword_filename)
    xml_filename = basename + '.xml'
    with open(keyword_filename) as keyword_file:
        keyword_str = keyword_file.read()

    tree = valid_iso_xml(xml_filename)
    root = tree.getroot()

    keyword_element = root.find(ISO_METADATA_KEYWORD_TAG)
    # by now we should have a valid container
    if keyword_element is None:
        raise MetadataReadError
    keyword_element.append(CDATA(keyword_str))
    # next line fixes issue #1380 - do not remove before testing! TS
    keyword_element.text = CDATA(keyword_str)

    tree.write(xml_filename, encoding="UTF-8")
    return xml_filename


def generate_iso_metadata(keywords=None):
    """Make a valid ISO 19115 XML using the values of safe.get_defaults

    This method will create XML based on the iso_19115_template.py template
    The $placeholders there will be replaced by the values returned from
    safe.defaults.get_defaults. Note that get_defaults takes care of using the
    values set in QGIS settings if available.

    :param keywords: The metadata keywords to write (which should be
            provided as a dict of key value pairs).
    :type keywords: dict

    :return: str valid XML
    """

    # get defaults from settings
    template_replacements = copy.copy(get_defaults())

    # create runtime based replacement values
    template_replacements['ISO19115_TODAY_DATE'] = time.strftime("%Y-%m-%d")
    if keywords is not None:
        template_replacements['INASAFE_KEYWORDS'] = '<![CDATA[%s]]>' % \
                                                    json.dumps(keywords)
        try:
            template_replacements['ISO19115_TITLE'] = keywords['title']
        except KeyError:
            pass
        try:
            template_replacements['ISO19115_LINEAGE'] = keywords['source']
        except KeyError:
            template_replacements['ISO19115_LINEAGE'] = ''

    else:
        template_replacements['INASAFE_KEYWORDS'] = ''

    return ISO_METADATA_XML_TEMPLATE.safe_substitute(template_replacements)


def write_iso_metadata_file(xml_filename, keywords=None):
    """Make a valid ISO 19115 XML file using the values of safe.get_defaults

    This method will create a file based on the iso_19115_template.py template
    The $placeholders there will be replaced by the values returned from
    safe.defaults.get_defaults. Note that get_defaults takes care of using the
    values set in QGIS settings if available.

    :param xml_filename: full path to the file to be generated
    :return:
    """
    xml = generate_iso_metadata(keywords)
    with open(xml_filename, 'w') as f:
        f.write(xml)
    return xml


def valid_iso_xml(xml_filename):
    """add the necessary tags into an existing xml file or create a new one

    :param xml_filename: name of the xml file
    :return: tree the parsed ElementTree
    """

    if os.path.isfile(xml_filename):
        # the file already has an xml file, we need to check it's structure
        tree = ElementTree.parse(xml_filename)
        root = tree.getroot()
        tag_str = '.'
        parent = root

        # Look for the correct nesting
        for tag in ISO_METADATA_KEYWORD_NESTING:
            tag_str += '/' + tag
            element = root.find(tag_str)
            if element is None:
                element = ElementTree.SubElement(parent, tag)
            parent = element
    else:
        # We create the XML from our template.
        # No more checks are needed since the template must be correct ;)
        write_iso_metadata_file(xml_filename)
        tree = ElementTree.parse(xml_filename)

    return tree


def read_iso_metadata(keyword_filename):
    """Try to extract keywords from an xml file

    :param keyword_filename: Name of keywords file.
    :type keyword_filename: str

    :returns: metadata: a dictionary containing the metadata.
        the keywords element contains the content of the ISO_METADATA_KW_TAG
        as list so that it can be read line per line as if it was a file.

    :raises: ReadMetadataError, IOError
    """

    basename, _ = os.path.splitext(keyword_filename)
    xml_filename = basename + '.xml'

    # this raises a IOError if the file doesn't exist
    tree = ElementTree.parse(xml_filename)
    root = tree.getroot()

    keyword_element = root.find(ISO_METADATA_KEYWORD_TAG)
    # we have an xml file but it has no valid container
    if keyword_element is None:
        raise MetadataReadError

    if keyword_element.text:
        metadata = {'keywords': keyword_element.text.split('\n')}

        return metadata
    else:
        return {
            'keywords' : []
        }
