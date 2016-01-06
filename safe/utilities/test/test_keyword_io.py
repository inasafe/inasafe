# coding=utf-8
"""Tests for keyword io class."""
import unittest
import os
import tempfile
import shutil

from qgis.core import QgsDataSourceURI, QgsVectorLayer

from safe.definitions import inasafe_keyword_version
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
from safe.utilities.unicode import get_unicode
from safe.utilities.metadata import read_iso19115_metadata

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
            'datatype': 'OSM'
        }

        # Raster Layer keywords
        hazard_path = test_data_path('hazard', 'tsunami_wgs84.tif')
        self.raster_layer, _ = load_layer(hazard_path)
        self.expected_raster_keywords = {
            'hazard_category': 'single_event',
            'title': 'Generic Continuous Flood',
            'hazard': 'flood',
            'continuous_hazard_unit': 'generic',
            'layer_geometry': 'raster',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'keyword_version': '3.2'
        }

        # Vector Layer keywords
        vector_path = test_data_path('exposure', 'buildings_osm_4326.shp')
        self.vector_layer, _ = load_layer(vector_path)
        self.expected_vector_keywords = {
            'keyword_version': '3.2',
            'structure_class_field': 'FLOODED',
            'title': 'buildings_osm_4326',
            'layer_geometry': 'polygon',
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
        layer = clone_raster_layer(
            name='generic_continuous_flood',
            extension='.asc',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        keywords = self.keyword_io.read_keywords(layer)
        expected_keywords = self.expected_raster_keywords

        self.assertDictEqual(keywords, expected_keywords)

    def test_read_vector_file_keywords(self):
        """Test read vector file keywords with the generic readKeywords method.
         """
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        expected_keywords = self.expected_vector_keywords

        self.assertDictEqual(keywords, expected_keywords)

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
        new_keywords = {
            'hazard_category': 'multiple_event'
        }
        self.keyword_io.update_keywords(layer, new_keywords)
        keywords = self.keyword_io.read_keywords(layer)
        expected_keywords = {
            'hazard_category': 'multiple_event',
            'title': 'Tsunami',
            'hazard': 'tsunami',
            'continuous_hazard_unit': 'metres',
            'layer_geometry': 'raster',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'keyword_version': inasafe_keyword_version
        }
        expected_keywords = {
            k: get_unicode(v) for k, v in expected_keywords.iteritems()
        }
        self.maxDiff = None
        self.assertDictEqual(keywords, expected_keywords)

    @unittest.skip('No longer used in the new metadata.')
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

        self.assertEqual(sqlite_layer.source(), expected_source)

        keywords = self.keyword_io.read_keywords(sqlite_layer)
        expected_keywords = self.expected_sqlite_keywords

        self.assertDictEqual(keywords, expected_keywords)

        # Delete SQL Layer so that we can delete the file
        del sqlite_layer
        os.remove(local_path)

    def test_copy_keywords(self):
        """Test we can copy the keywords."""
        out_path = unique_filename(
            prefix='test_copy_keywords', suffix='.shp')
        layer = clone_raster_layer(
            name='generic_continuous_flood',
            extension='.asc',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        self.keyword_io.copy_keywords(layer, out_path)
        # copied_keywords = read_file_keywords(out_path.split('.')[0] + 'xml')
        copied_keywords = read_iso19115_metadata(out_path)
        expected_keywords = self.expected_raster_keywords
        expected_keywords['keyword_version'] = inasafe_keyword_version


        self.maxDiff = None
        self.assertDictEqual(copied_keywords, expected_keywords)

    def test_definition(self):
        """Test we can get definitions for keywords.

        .. versionadded:: 3.2

        """
        keyword = 'hazards'
        definition = self.keyword_io.definition(keyword)
        self.assertTrue('description' in definition)

    def test_to_message(self):
        """Test we can convert keywords to a message object.

        .. versionadded:: 3.2

        """
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        message = self.keyword_io.to_message(keywords).to_text()
        self.assertIn('*Exposure*, structure------', message)

    def test_layer_to_message(self):
        """Test to show augmented keywords if KeywordsIO ctor passed a layer.

        .. versionadded:: 3.3
        """
        keywords = KeywordIO(self.vector_layer)
        message = keywords.to_message().to_text()
        self.assertIn('*Reference system*, ', message)

    def test_dict_to_row(self):
        """Test the dict to row helper works.

        .. versionadded:: 3.2
        """
        keyword_value = (
            "{'high': ['Kawasan Rawan Bencana III'], "
            "'medium': ['Kawasan Rawan Bencana II'], "
            "'low': ['Kawasan Rawan Bencana I']}")
        table = self.keyword_io._dict_to_row(keyword_value)
        self.assertIn(
            u'\n---\n*high*, Kawasan Rawan Bencana III------',
            table.to_text())
        # should also work passing a dict
        keyword_value = {
            'high': ['Kawasan Rawan Bencana III'],
            'medium': ['Kawasan Rawan Bencana II'],
            'low': ['Kawasan Rawan Bencana I']}
        table = self.keyword_io._dict_to_row(keyword_value)
        self.assertIn(
            u'\n---\n*high*, Kawasan Rawan Bencana III------',
            table.to_text())

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
