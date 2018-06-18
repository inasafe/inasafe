# coding=utf-8
"""
Test for Unicode helper.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '04/03/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from safe.utilities.unicode import get_string, get_unicode


class UnicodeTest(unittest.TestCase):
    """Test Unicode helper module."""

    # noinspection PyMethodMayBeStatic
    def test_get_unicode(self):
        """Test get_unicode function."""
        text = 'Test á, é, í, ó, ú, ü, ñ, ¿'
        unicode_repr = 'Test \xe1, \xe9, \xed, \xf3, \xfa, \xfc, \xf1, \xbf'
        message = 'It should return %s, but it returned %s' % (
            get_unicode(text), unicode_repr)
        self.assertEqual(get_unicode(text), unicode_repr, message)
        textbytes = 'Test á, é, í, ó, ú, ü, ñ, ¿'.encode('utf-8')
        self.assertEqual(get_unicode(textbytes), unicode_repr)

    def test_self(self):
        """Test get_unicode function."""
        text = 'Test á, é, í, ó, ú, ü, ñ, ¿'
        unicode_repr = 'Test \xe1, \xe9, \xed, \xf3, \xfa, \xfc, \xf1, \xbf'
        message = 'It should return %s, but it returned %s' % (
            text, unicode_repr)
        self.assertEqual(text, unicode_repr, message)

    def test_get_string(self):
        """Test get_string function."""
        text = 'Test \xe1, \xe9, \xed, \xf3, \xfa, \xfc, \xf1, \xbf'
        string_repr = b'Test \xc3\xa1, \xc3\xa9, \xc3\xad, \xc3\xb3, \xc3\xba, \xc3\xbc, \xc3\xb1, \xc2\xbf'
        message = 'It should return %s, but it returned %s' % (
            string_repr, get_string(text))
        self.assertEqual(get_string(text), string_repr, message)
        self.assertEqual(get_string(string_repr), string_repr)

    def test_str_unicode_str(self):
        """Test if str(unicode(str)) works correctly."""
        text = 'Test á, é, í, ó, ú, ü, ñ, ¿'.encode('utf-8')
        unicode_repr = get_unicode(text)
        str_repr = get_string(unicode_repr)
        message = 'It should return %s, but it returned %s' % (text, str_repr)
        self.assertEqual(text, str_repr, message)


if __name__ == '__main__':
    unittest.main()
