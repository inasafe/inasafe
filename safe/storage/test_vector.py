# coding=utf-8
"""**Tests for safe vector layer class**"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '21/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import unittest

from safe.common.testing import UNITDATA, get_qgis_app
from safe.common.utilities import temp_dir, unique_filename
from safe.storage.utilities import read_keywords
from safe.storage.vector import Vector, QGIS_IS_AVAILABLE

if QGIS_IS_AVAILABLE:   # Import QgsVectorLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from qgis.core import QgsVectorLayer


LOGGER = logging.getLogger('InaSAFE')
KEYWORD_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'exposure.keywords'))
SQLITE_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'exposure', 'exposure.sqlite'))
#noinspection PyUnresolvedReferences
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

    def test_sublayer_loading(self):
        """Test if we can load sublayers."""
        keywords = read_keywords(KEYWORD_PATH, EXPOSURE_SUBLAYER_NAME)
        layer = Vector(data=SQLITE_PATH, keywords=keywords,
                       sublayer=EXPOSURE_SUBLAYER_NAME)
        msg = ('Expected layer to be a polygon layer, got a %s' %
               layer.geometry_type)
        self.assertTrue(layer.is_polygon_data, msg)
        count = len(layer)
        self.assertEqual(count, 250, 'Expected 250 features, got %s' % count)

    def test_shapefile_loading(self):
        """Test that loading a dataset with no sublayers works."""
        keywords = read_keywords(SHP_BASE + '.keywords')
        layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)
        msg = ('Expected layer to be a polygon layer, got a %s' %
               layer.geometry_type)
        self.assertTrue(layer.is_polygon_data, msg)
        count = len(layer)
        self.assertEqual(count, 250, 'Expected 250 features, got %s' % count)

    def test_sqlite_writing(self):
        """Test that writing a dataset to sqlite works."""
        keywords = read_keywords(SHP_BASE + '.keywords')
        layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)
        test_dir = temp_dir(sub_dir='test')
        test_file = unique_filename(suffix='.sqlite', dir=test_dir)
        layer.write_to_file(test_file, sublayer='foo')
        self.assertTrue(os.path.exists(test_file))
    test_sqlite_writing.slow = True

    def test_qgis_vector_layer_loading(self):
        """Test that reading from QgsVectorLayer works."""
        keywords = read_keywords(KEYWORD_PATH, EXPOSURE_SUBLAYER_NAME)
        if QGIS_IS_AVAILABLE:
            qgis_layer = QgsVectorLayer(SHP_BASE + '.shp', 'test', 'ogr')

            layer = Vector(data=qgis_layer, keywords=keywords)
            msg = ('Expected layer to be a polygon layer, got a %s' %
                   layer.geometry_type)
            self.assertTrue(layer.is_polygon_data, msg)
            count = len(layer)
            self.assertEqual(
                count, 250, 'Expected 250 features, got %s' % count)

    def test_convert_to_qgis_vector_layer(self):
        """Test that converting to QgsVectorLayer works."""
        if QGIS_IS_AVAILABLE:
            # Create vector layer
            keywords = read_keywords(SHP_BASE + '.keywords')
            layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)

            # Convert to QgsVectorLayer
            qgis_layer = layer.as_qgis_native()
            provider = qgis_layer.dataProvider()
            count = provider.featureCount()
            self.assertEqual(
                count, 250, 'Expected 250 features, got %s' % count)
