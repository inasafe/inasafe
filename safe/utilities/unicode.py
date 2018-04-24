# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**Unicode Utilities.**

The module provides utilities function to convert between unicode and byte
string for Python 2.x. When we move to Python 3, this module and its usage
should be removed as string in Python 3 is already stored in unicode.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '02/24/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


def __if_not_basestring(text_object):
    """Convert to str"""
    converted_str = text_object
    if not isinstance(text_object, str):
        converted_str = str(text_object)
    return converted_str


def get_unicode(input_text, encoding='utf-8'):
    """Get the unicode (str) representation of an object.

    :param input_text: The input text.
    :type input_text: unicode, str, float, int

    :param encoding: The encoding used to do the conversion, default to utf-8.
    :type encoding: str

    :returns: Unicode representation of the input.
    :rtype: str
    """
    if isinstance(input_text, str):
        return input_text
    return str(input_text, encoding, errors='ignore')


def get_string(input_text, encoding='utf-8'):
    """Get byte string representation of an object.

    :param input_text:  The input text.
    :type input_text: unicode, str, float, int

    :param encoding: The encoding used to do the conversion, default to utf-8.
    :type encoding: str

    :returns: Byte string representation of the input.
    :rtype: bytes
    """
    if isinstance(input_text, str):
        return input_text.encode(encoding)
    return input_text


def byteify(input_object):
    """Recursive function to transform an object to byte.

    :param input_object: A python object such as unicode, dictionary or list.
    :type: unicode, list, dict

    :return: The object with byte only.
    """
    if isinstance(input_object, dict):
        return {byteify(key): byteify(value)
                for key, value in list(input_object.items())}
    elif isinstance(input_object, list):
        return [byteify(element) for element in input_object]
    elif isinstance(input_object, str):
        return input_object.encode('utf-8')
    else:
        return input_object
