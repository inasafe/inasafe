"""**Tests for safe vector layer class**
"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '21/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import unittest

from safe.common.testing import UNITDATA
from safe.common.utilities import temp_dir, unique_filename
from safe.storage.utilities import read_keywords
from safe.storage.vector import Vector

LOGGER = logging.getLogger('InaSAFE')
KEYWORD_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'exposure.keywords'))
SQLITE_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'exposure.sqlite'))
SHP_BASE = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'buildings_osm_4326'))
EXPOSURE_SUBLAYER_NAME = 'buildings_osm_4326'


class VectorTest(unittest.TestCase):

    def setUp(self):
        msg = 'Sqlite file does not exist at %s' % SQLITE_PATH
        assert os.path.exists(SQLITE_PATH), msg
        msg = 'Keyword file does not exist at %s' % KEYWORD_PATH
        assert os.path.exists(KEYWORD_PATH), msg
        msg = 'Shp file does not exist at %s.shp' % SHP_BASE
        assert os.path.exists(SHP_BASE + '.shp'), msg

    def testSublayerLoading(self):
        keywords = read_keywords(KEYWORD_PATH, EXPOSURE_SUBLAYER_NAME)
        layer = Vector(data=SQLITE_PATH, keywords=keywords,
                       sublayer=EXPOSURE_SUBLAYER_NAME)
        msg = ('Expected layer to be a polygon layer, got a %s' %
               layer.geometry_type)
        assert layer.is_polygon_data, msg
        count = len(layer)
        assert count == 250, 'Expected 250 features, got %s' % count

    def testShpLoading(self):
        """Test that loading a dataset with no sublayers works."""
        keywords = read_keywords(SHP_BASE + '.keywords')
        layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)
        msg = ('Expected layer to be a polygon layer, got a %s' %
               layer.geometry_type)
        assert layer.is_polygon_data, msg
        count = len(layer)
        assert count == 250, 'Expected 250 features, got %s' % count

    def testSqliteWriting(self):
        """Test that writing a dataset to sqlite works."""
        keywords = read_keywords(SHP_BASE + '.keywords')
        layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)
        test_dir = temp_dir(sub_dir='test')
        test_file = unique_filename(suffix='.sqlite', dir=test_dir)
        layer.write_to_file(test_file, sublayer='foo')
    testSqliteWriting.slow = True
