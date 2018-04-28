# coding=utf-8
"""Metadata utilities."""


from contextlib import contextmanager
from datetime import datetime, date
from xml.dom.minidom import parseString
from xml.etree import ElementTree
from safe.utilities.unicode import get_string
from qgis.PyQt.QtCore import QUrl, QDate, QDateTime, Qt

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

XML_NS = {
    'gmi': 'http://www.isotc211.org/2005/gmi',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}
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


@contextmanager
def reading_ancillary_files(metadata):
    """
    context manager to be used when reading metadata so no errors are risen.

    This is useful because we want to be able to get as much as possible out
    of malformed input

    :param metadata: the metadata object
    :type metadata: BaseMetadata
    """
    metadata.reading_ancillary_files = True
    yield metadata
    metadata.reading_ancillary_files = False


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


def prettify_xml(xml_str):
    """
    returns prettified XML without blank lines

    based on http://stackoverflow.com/questions/14479656/
    :param xml_str: the XML to be prettified
    :type xml_str: str
    :return: the prettified XML
    :rtype: str
    """
    parsed_xml = parseString(get_string(xml_str))
    pretty_xml = '\n'.join(
        [line for line in parsed_xml.toprettyxml(indent=' ' * 2)
         .split('\n') if line.strip()])
    if not pretty_xml.endswith('\n'):
        pretty_xml += '\n'
    return pretty_xml


def serialize_dictionary(dictionary):
    """Function to stringify a dictionary recursively.

    :param dictionary: The dictionary.
    :type dictionary: dict

    :return: The string.
    :rtype: basestring
    """
    string_value = {}
    for k, v in list(dictionary.items()):
        if isinstance(v, QUrl):
            string_value[k] = v.toString()
        elif isinstance(v, (QDate, QDateTime)):
            string_value[k] = v.toString(Qt.ISODate)
        elif isinstance(v, datetime):
            string_value[k] = v.isoformat()
        elif isinstance(v, date):
            string_value[k] = v.isoformat()
        elif isinstance(v, dict):
            # Recursive call
            string_value[k] = serialize_dictionary(v)
        else:
            string_value[k] = v
    return string_value
