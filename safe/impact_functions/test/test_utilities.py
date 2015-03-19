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

from safe.impact_functions.utilities import keywords_to_str


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


if __name__ == '__main__':
    unittest.main()
