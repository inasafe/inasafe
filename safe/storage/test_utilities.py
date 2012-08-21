"""**Tests for safe common utilire**

This module:

* provides piecewise constant (nearest neighbour) and bilinear interpolation
* is fast (based on numpy vector operations)
* depends only on numpy
* guarantees that interpolated values never exceed the four nearest neighbours
* handles missing values in domain sensibly using NaN
* is unit tested with a range of common and corner cases

See end of this file for documentation of the mathematical derivation used.
"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '21/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import logging
import unittest

from safe.common.testing import UNITDATA
from safe.storage.utilities import read_keywords

LOGGER = logging.getLogger('InaSAFE')
PATH = os.path.abspath(
    os.path.join(UNITDATA, 'other', 'multilayer.keywords'))
SIMPLE_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'other', 'multilayer.keywords'))


class CommonUtilitiesTest(unittest.TestCase):

    def setUp(self):
        msg = 'Multifile keywords do not exist at %s' % PATH
        assert os.path.exists(PATH), msg

    def test_read_keywords(self):
        """Test reading keywords"""
        keywords = read_keywords(PATH)
        expected_keywords = {'datatype': 'osm',
                             'category': 'exposure',
                             'title': 'buildings_osm_4326',
                             'subcategory': 'building',
                             'purpose': 'dki'}
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

    def test_read_keywords_for_sublayer(self):
        """Test reading keywords for sublayer"""
        keywords = read_keywords(PATH, 'osm_flood')
        expected_keywords = {'datatype': 'flood',
                             'category': 'hazard',
                             'subcategory': 'building',
                             'title': 'flood_osm_4326'}
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

    def test_read_keywords_simple(self):
        """Test reading keywords from keywords file with no sublayers"""
        keywords = read_keywords(SIMPLE_PATH)
        expected_keywords = {'datatype': 'osm',
                             'category': 'exposure',
                             'title': 'buildings_osm_4326',
                             'subcategory': 'building',
                             'purpose': 'dki'}
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

if __name__ == '__main__':
    unittest.main()
