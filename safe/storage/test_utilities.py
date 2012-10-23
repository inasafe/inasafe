"""**Tests for safe common utilities**
"""
from safe.common.utilities import temp_dir, unique_filename

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '21/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import unittest

from safe.common.testing import UNITDATA
from safe.storage.utilities import (read_keywords,
                                    write_keywords)

LOGGER = logging.getLogger('InaSAFE')
KEYWORD_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'other', 'multilayer.keywords'))
SIMPLE_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'other', 'simple.keywords'))

DKI_KEYWORDS = {'datatype': 'osm',
                'category': 'exposure',
                'title': 'buildings_osm_4326',
                'subcategory': 'structure',
                'purpose': 'dki'}
OSM_KEYWORDS = {'datatype': 'flood',
                'category': 'hazard',
                'subcategory': 'structure',
                'title': 'flood_osm_4326'}


class CommonUtilitiesTest(unittest.TestCase):

    def setUp(self):
        msg = 'Multifile keywords do not exist at %s' % KEYWORD_PATH
        assert os.path.exists(KEYWORD_PATH), msg
        msg = 'Simple keywords do not exist at %s' % SIMPLE_PATH
        assert os.path.exists(SIMPLE_PATH), msg

    def make_temp_file(self):
        """Helper to make a keywords file path"""
        tempdir = temp_dir(sub_dir='test')
        filename = unique_filename(suffix='.keywords', dir=tempdir)
        LOGGER.debug(filename)
        return filename

    def test_read_keywords(self):
        """Test reading keywords - get first block from kwds as default."""
        keywords = read_keywords(KEYWORD_PATH)
        expected_keywords = DKI_KEYWORDS
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

    def test_write_keywords(self):
        """Test writing keywords with no sublayer, no existing file."""
        keywords = DKI_KEYWORDS
        filename = self.make_temp_file()
        write_keywords(keywords, filename)
        # Read back contents and check against control dataset
        control_keywords = read_keywords(SIMPLE_PATH, all_blocks=True)
        actual_keywords = read_keywords(filename, all_blocks=True)
        msg = 'Expected:\n%s\nGot:\n%s\n' % (control_keywords, actual_keywords)
        assert control_keywords == actual_keywords, msg

    def test_write_keywords_multisublayer(self):
        """Test writing keywords for named sublayer, no existing file."""

        filename = self.make_temp_file()
        write_keywords(DKI_KEYWORDS, filename=filename, sublayer='dki')
        write_keywords(OSM_KEYWORDS, filename=filename, sublayer='osm')
        # Read back contents and check against control dataset
        control_path = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'expected_multilayer.keywords'))
        control_keywords = read_keywords(control_path, all_blocks=True)
        actual_keywords = read_keywords(filename, all_blocks=True)
        msg = 'Expected:\n%s\nGot:\n%s\n' % (control_keywords, actual_keywords)
        assert control_keywords == actual_keywords, msg

    def test_write_keywords_singlesublayer(self):
        """Test writing keywords for single sublayer, no existing file."""

        filename = self.make_temp_file()
        write_keywords(OSM_KEYWORDS, filename=filename, sublayer='osm')
        #read back contents and check against control dataset
        control_path = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'expected_singlelayer.keywords'))
        control_keywords = read_keywords(control_path, all_blocks=True)
        actual_keywords = read_keywords(filename, all_blocks=True)
        msg = 'Expected:\n%s\nGot:\n%s\n' % (control_keywords, actual_keywords)
        assert control_keywords == actual_keywords, msg

    def test_read_all_keywords(self):
        """Test reading all keywords for all layers"""
        keywords = read_keywords(KEYWORD_PATH, all_blocks=True)
        expected_keywords = {'osm_buildings': DKI_KEYWORDS,
                             'osm_flood': OSM_KEYWORDS}
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

    def test_read_keywords_for_sublayer(self):
        """Test reading keywords for specific sublayer."""
        keywords = read_keywords(KEYWORD_PATH, sublayer='osm_flood')
        expected_keywords = OSM_KEYWORDS
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

    def test_read_keywords_simple(self):
        """Test reading keywords from keywords file with no sublayers"""
        keywords = read_keywords(SIMPLE_PATH)
        expected_keywords = DKI_KEYWORDS
        msg = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEquals(keywords, expected_keywords, msg)
        LOGGER.debug(keywords)

if __name__ == '__main__':
    unittest.main()
