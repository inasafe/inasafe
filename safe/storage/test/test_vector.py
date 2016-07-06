# coding=utf-8
"""**Tests for safe vector layer class**"""

__author__ = 'Tim Sutton <tim@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '21/08/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import unittest

from safe.common.utilities import temp_dir, unique_filename
from safe.storage.vector import Vector, QGIS_IS_AVAILABLE
from safe.test.utilities import standard_data_path, get_qgis_app

if QGIS_IS_AVAILABLE:   # Import QgsVectorLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from qgis.core import QgsVectorLayer


LOGGER = logging.getLogger('InaSAFE')
KEYWORD_PATH = standard_data_path('exposure', 'exposure.xml')
SQLITE_PATH = standard_data_path('exposure', 'exposure.sqlite')
SHP_BASE = standard_data_path('exposure', 'buildings_osm_4326')
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
        keywords = {}
        layer = Vector(data=SQLITE_PATH, keywords=keywords,
                       sublayer=EXPOSURE_SUBLAYER_NAME)
        msg = ('Expected layer to be a polygon layer, got a %s' %
               layer.geometry_type)
        self.assertTrue(layer.is_polygon_data, msg)
        count = len(layer)
        self.assertEqual(count, 250, 'Expected 250 features, got %s' % count)

    def test_shapefile_loading(self):
        """Test that loading a dataset with no sublayers works."""
        keywords = {}
        layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)
        msg = ('Expected layer to be a polygon layer, got a %s' %
               layer.geometry_type)
        self.assertTrue(layer.is_polygon_data, msg)
        count = len(layer)
        self.assertEqual(count, 250, 'Expected 250 features, got %s' % count)

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False), 'Slow test, skipped on travis')
    def test_sqlite_writing(self):
        """Test that writing a dataset to sqlite works."""
        keywords = {}
        layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)
        test_dir = temp_dir(sub_dir='test')
        test_file = unique_filename(suffix='.sqlite', dir=test_dir)
        layer.write_to_file(test_file, sublayer='foo')
        self.assertTrue(os.path.exists(test_file))

    def test_qgis_vector_layer_loading(self):
        """Test that reading from QgsVectorLayer works."""
        keywords = {}
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
            keywords = {}
            layer = Vector(data=SHP_BASE + '.shp', keywords=keywords)

            # Convert to QgsVectorLayer
            qgis_layer = layer.as_qgis_native()
            provider = qgis_layer.dataProvider()
            count = provider.featureCount()
            self.assertEqual(
                count, 250, 'Expected 250 features, got %s' % count)
