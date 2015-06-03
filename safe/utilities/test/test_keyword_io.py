# coding=utf-8
"""Tests for keyword io class."""
import unittest
import os
import tempfile
import shutil

from qgis.core import QgsDataSourceURI, QgsVectorLayer

from safe.common.utilities import unique_filename
from safe.utilities.utilities import read_file_keywords
from safe.test.utilities import (
    load_layer,
    get_qgis_app,
    test_data_path,
    clone_raster_layer)
from safe.utilities.keyword_io import KeywordIO
from safe.common.exceptions import HashNotFoundError
from safe.common.utilities import temp_dir
from safe.common.exceptions import NoKeywordsFoundError

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Don't change this, not even formatting, you will break tests!
PG_URI = """'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
         type=MULTIPOLYGON table="valuations_parcel" (geometry) sql='"""


class KeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        self.keyword_io = KeywordIO()

        # SQLite Layer
        uri = QgsDataSourceURI()
        sqlite_building_path = test_data_path('exposure', 'exposure.sqlite')
        uri.setDatabase(sqlite_building_path)
        uri.setDataSource('', 'buildings_osm_4326', 'Geometry')
        self.sqlite_layer = QgsVectorLayer(
            uri.uri(), 'OSM Buildings', 'spatialite')
        self.expected_sqlite_keywords = {
            'category': 'exposure',
            'datatype': 'OSM',
            'subcategory': 'building'}

        # Raster Layer keywords
        hazard_path = test_data_path('hazard', 'tsunami_wgs84.tif')
        self.raster_layer, _ = load_layer(hazard_path)
        self.expected_raster_keywords = {
            'hazard_category': 'single_event',
            'title': 'Tsunami',
            'hazard': 'tsunami',
            'hazard_continuous_unit': 'metres',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous'
        }

        # Vector Layer keywords
        vector_path = test_data_path('exposure', 'buildings_osm_4326.shp')
        self.vector_layer, _ = load_layer(vector_path)
        self.expected_vector_keywords = {
            'title': 'buildings_osm_4326',
            'datatype': 'osm',
            'purpose': 'dki',
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'exposure': 'structure'
        }
        # Keyword less layer
        keywordless_path = test_data_path('other', 'keywordless_layer.shp')
        self.keywordless_layer, _ = load_layer(keywordless_path)

    def tearDown(self):
        pass

    def test_get_hash_for_datasource(self):
        """Test we can reliably get a hash for a uri"""
        hash_value = self.keyword_io.hash_for_datasource(PG_URI)
        expected_hash = '7cc153e1b119ca54a91ddb98a56ea95e'
        message = "Got: %s\nExpected: %s" % (hash_value, expected_hash)
        self.assertEqual(hash_value, expected_hash, message)

    def test_write_read_keyword_from_uri(self):
        """Test we can set and get keywords for a non local datasource"""
        handle, filename = tempfile.mkstemp(
            '.db', 'keywords_', temp_dir())

        # Ensure the file is deleted before we try to write to it
        # fixes windows specific issue where you get a message like this
        # ERROR 1: c:\temp\inasafe\clip_jpxjnt.shp is not a directory.
        # This is because mkstemp creates the file handle and leaves
        # the file open.

        os.close(handle)
        os.remove(filename)
        expected_keywords = {
            'category': 'exposure',
            'datatype': 'itb',
            'subcategory': 'building'}
        # SQL insert test
        # On first write schema is empty and there is no matching hash
        self.keyword_io.set_keyword_db_path(filename)
        self.keyword_io.write_keywords_for_uri(PG_URI, expected_keywords)
        # SQL Update test
        # On second write schema is populated and we update matching hash
        expected_keywords = {
            'category': 'exposure',
            'datatype': 'OSM',  # <--note the change here!
            'subcategory': 'building'}
        self.keyword_io.write_keywords_for_uri(PG_URI, expected_keywords)
        # Test getting all keywords
        keywords = self.keyword_io.read_keyword_from_uri(PG_URI)
        message = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
            keywords, expected_keywords, filename)
        self.assertDictEqual(keywords, expected_keywords, message)
        # Test getting just a single keyword
        keyword = self.keyword_io.read_keyword_from_uri(PG_URI, 'datatype')
        expected_keyword = 'OSM'
        message = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
            keyword, expected_keyword, filename)
        self.assertDictEqual(keywords, expected_keywords, message)
        # Test deleting keywords actually does delete
        self.keyword_io.delete_keywords_for_uri(PG_URI)
        try:
            _ = self.keyword_io.read_keyword_from_uri(PG_URI, 'datatype')
            # if the above didn't cause an exception then bad
            message = 'Expected a HashNotFoundError to be raised'
            assert message
        except HashNotFoundError:
            # we expect this outcome so good!
            pass

    def test_are_keywords_file_based(self):
        """Can we correctly determine if keywords should be written to file or
        to database?"""
        assert not self.keyword_io.are_keywords_file_based(self.sqlite_layer)
        assert self.keyword_io.are_keywords_file_based(self.raster_layer)
        assert self.keyword_io.are_keywords_file_based(self.vector_layer)

    def test_read_raster_file_keywords(self):
        """Can we read raster file keywords using generic readKeywords method
        """
        keywords = self.keyword_io.read_keywords(self.raster_layer)
        expected_keywords = self.expected_raster_keywords
        source = self.raster_layer.source()
        message = 'Got:\n%s\nExpected:\n%s\nSource:\n%s' % (
            keywords, expected_keywords, source)
        self.assertDictEqual(keywords, expected_keywords, message)

    def test_read_vector_file_keywords(self):
        """Test read vector file keywords with the generic readKeywords method.
         """
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        expected_keywords = self.expected_vector_keywords
        source = self.vector_layer.source()
        message = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
            keywords, expected_keywords, source)
        self.assertDictEqual(keywords, expected_keywords, message)

    def test_read_keywordless_layer(self):
        """Test read 'keyword' file from keywordless layer.
        """
        self.assertRaises(
            NoKeywordsFoundError,
            self.keyword_io.read_keywords,
            self.keywordless_layer,
            )

    def test_update_keywords(self):
        """Test append file keywords with update_keywords method."""
        layer = clone_raster_layer(
            name='tsunami_wgs84',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        new_keywords = {'category': 'exposure', 'test': 'TEST'}
        self.keyword_io.update_keywords(layer, new_keywords)
        keywords = self.keyword_io.read_keywords(layer)
        expected_keywords = {
            'category': 'exposure',
            'hazard_category': 'single_event',
            'title': 'Tsunami',
            'hazard': 'tsunami',
            'hazard_continuous_unit': 'metres',
            'test': 'TEST',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous'
        }
        message = 'Got:\n%s\nExpected:\n%s' % (keywords, expected_keywords)
        self.assertDictEqual(keywords, expected_keywords, message)

    def test_read_db_keywords(self):
        """Can we read sqlite kw with the generic read_keywords method
        """
        db_path = test_data_path('other', 'test_keywords.db')
        self.read_db_keywords(db_path)

    def read_db_keywords(self, db_path):
        """Can we read sqlite keywords with the generic readKeywords method
        """
        self.keyword_io.set_keyword_db_path(db_path)

        # We need to use relative path so that the hash from URI will match
        local_path = os.path.join(
            os.path.dirname(__file__), 'exposure.sqlite')
        sqlite_building_path = test_data_path('exposure', 'exposure.sqlite')
        shutil.copy2(sqlite_building_path, local_path)
        uri = QgsDataSourceURI()
        uri.setDatabase('exposure.sqlite')
        uri.setDataSource('', 'buildings_osm_4326', 'Geometry')
        sqlite_layer = QgsVectorLayer(uri.uri(), 'OSM Buildings', 'spatialite')

        expected_source = (
            'dbname=\'exposure.sqlite\' table="buildings_osm_4326" ('
            'Geometry) sql=')
        message = 'Got source: %s\n\nExpected %s\n' % (
            sqlite_layer.source(), expected_source)
        self.assertEqual(sqlite_layer.source(), expected_source, message)

        keywords = self.keyword_io.read_keywords(sqlite_layer)
        expected_keywords = self.expected_sqlite_keywords
        message = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
            keywords, expected_keywords, self.sqlite_layer.source())
        self.assertDictEqual(keywords, expected_keywords, message)

        # Delete SQL Layer so that we can delete the file
        del sqlite_layer
        os.remove(local_path)

    def test_copy_keywords(self):
        """Test we can copy the keywords."""
        out_path = unique_filename(
            prefix='test_copy_keywords', suffix='.keywords')
        self.keyword_io.copy_keywords(self.raster_layer, out_path)
        copied_keywords = read_file_keywords(out_path)
        expected_keywords = self.expected_raster_keywords
        message = 'Got:\n%s\nExpected:\n%s\nSource:\n%s' % (
            copied_keywords, expected_keywords, out_path)
        self.assertDictEqual(copied_keywords, expected_keywords, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
