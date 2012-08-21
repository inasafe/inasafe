"""**Tests for safe vector layer class**
"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '21/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import unittest

from safe.common.testing import UNITDATA
from safe.storage.utilities import read_keywords
from safe.storage.vector import Vector

LOGGER = logging.getLogger('InaSAFE')
KEYWORD_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'exposure.keywords'))
SQLITE_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'exposure.sqlite'))


class VectorTest(unittest.TestCase):

    def setUp(self):
        msg = 'Sqlite file does not exist at %s' % SQLITE_PATH
        assert os.path.exists(SQLITE_PATH), msg
        msg = 'Keyword file does not exist at %s' % KEYWORD_PATH
        assert os.path.exists(KEYWORD_PATH), msg

    def testSublayerLoading(self):
        keywords = read_keywords(KEYWORD_PATH, 'osm_jk')
        layer = Vector(data=SQLITE_PATH, keywords=keywords)
