# coding=utf-8
"""Tests for core.py

InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Utilities**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Akbar Gumbira (akbargumbira@gmail.com)'
__revision__ = '$Format:%H$'
__date__ = '11/12/14'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os

from safe.impact_functions.utilities import (
    keywords_to_str,
    add_to_list,
    get_python_file)


class TestUtilities(unittest.TestCase):
    def test_keywords_to_str(self):
        """String representation of keywords works."""

        keywords = {
            'category': 'hazard', 'subcategory': 'tsunami', 'unit': 'm'}
        string_keywords = keywords_to_str(keywords)
        for key in keywords:
            message = (
                'Expected key %s to appear in %s' % (key, string_keywords))
            assert key in string_keywords, message

            val = keywords[key]
            message = (
                'Expected value %s to appear in %s' % (val, string_keywords))
            assert val in string_keywords, message

    def test_add_to_list(self):
        """Test for add_to_list function
        """
        list_original = ['a', 'b', ['a'], {'a': 'b'}]
        list_a = ['a', 'b', ['a'], {'a': 'b'}]
        # add same immutable element
        list_b = add_to_list(list_a, 'b')
        assert list_b == list_original
        # add list
        list_b = add_to_list(list_a, ['a'])
        assert list_b == list_original
        # add same mutable element
        list_b = add_to_list(list_a, {'a': 'b'})
        assert list_b == list_original
        # add new mutable element
        list_b = add_to_list(list_a, 'c')
        assert len(list_b) == (len(list_original) + 1)
        assert list_b[-1] == 'c'

    def test_get_python_file(self):
        """Test get_python_file"""
        path = get_python_file(TestUtilities)
        expected_path = os.path.realpath(__file__)
        expected_paths = [
            expected_path,
            expected_path + 'c',
            expected_path[:-1]]

        message = 'Expecting %s in %s' % (path, expected_paths)

        self.assertIn(path, expected_paths, message)

if __name__ == '__main__':
    unittest.main()
