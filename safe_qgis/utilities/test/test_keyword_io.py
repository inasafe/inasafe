# coding=utf-8
"""Tests for keyword io class."""
# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import sys
import os
import tempfile
import shutil
# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

# For testing and demoing

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.common.utilities import unique_filename
from safe_qgis.safe_interface import read_file_keywords
from safe_qgis.utilities.utilities_for_testing import load_layer
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.exceptions import HashNotFoundError
from safe_qgis.tools.test.test_keywords_dialog import clone_padang_layer
from safe_qgis.safe_interface import temp_dir, HAZDATA, TESTDATA

from qgis.core import QgsDataSourceURI, QgsVectorLayer

# Don't change this, not even formatting, you will break tests!
PG_URI = """'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
         type=MULTIPOLYGON table="valuations_parcel" (geometry) sql='"""


class KeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        self.keyword_io = KeywordIO()
        uri = QgsDataSourceURI()
        uri.setDatabase(os.path.join(TESTDATA, 'jk.sqlite'))
        uri.setDataSource('', 'osm_buildings', 'Geometry')
        self.sqlite_layer = QgsVectorLayer(
            uri.uri(), 'OSM Buildings', 'spatialite')
        hazard_path = os.path.join(HAZDATA, 'Shakemap_Padang_2009.asc')
        self.raster_layer, layer_type = load_layer(
            hazard_path, directory=None)
        del layer_type
        self.vector_layer, layer_type = load_layer('Padang_WGS84.shp')
        del layer_type
        self.expected_sqlite_keywords = {
            'category': 'exposure',
            'datatype': 'OSM',
            'subcategory': 'building'}
        self.expected_vector_keywords = {
            'category': 'exposure',
            'datatype': 'itb',
            'subcategory': 'structure',
            'title': 'Padang WGS84'}
        self.expected_raster_keywords = {
            'category': 'hazard',
            'source': 'USGS',
            'subcategory': 'earthquake',
            'unit': 'MMI',
            'title': ('An earthquake in Padang '
            'like in 2009')}

    def tearDown(self):
        pass

    def test_get_hash_for_datasource(self):
        """Test we can reliably get a hash for a uri"""
        hash_value = self.keyword_io.hash_for_datasource(PG_URI)
        expected_hash = '7cc153e1b119ca54a91ddb98a56ea95e'
        message = "Got: %s\nExpected: %s" % (hash_value, expected_hash)
        assert hash_value == expected_hash, message

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
        assert keywords == expected_keywords, message
        # Test getting just a single keyword
        keyword = self.keyword_io.read_keyword_from_uri(PG_URI, 'datatype')
        expected_keyword = 'OSM'
        message = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
            keyword, expected_keyword, filename)
        assert keyword == expected_keyword, message
        # Test deleting keywords actually does delete
        self.keyword_io.delete_keywords_for_uri(PG_URI)
        try:
            _ = self.keyword_io.read_keyword_from_uri(PG_URI, 'datatype')
            #if the above didnt cause an exception then bad
            message = 'Expected a HashNotFoundError to be raised'
            assert message
        except HashNotFoundError:
            #we expect this outcome so good!
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
        self.assertEquals(keywords, expected_keywords, message)

    def test_read_vector_file_keywords(self):
        """Test read vector file keywords with the generic readKeywords method.
         """
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        expected_keywords = self.expected_vector_keywords
        source = self.vector_layer.source()
        message = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
            keywords, expected_keywords, source)
        assert keywords == expected_keywords, message

    def test_append_keywords(self):
        """Can we append file keywords with the generic readKeywords method."""
        layer, _ = clone_padang_layer()
        new_keywords = {'category': 'exposure', 'test': 'TEST'}
        self.keyword_io.update_keywords(layer, new_keywords)
        keywords = self.keyword_io.read_keywords(layer)

        for key, value in new_keywords.iteritems():
            message = (
                'Layer keywords misses appended key: %s\n'
                'Layer keywords:\n%s\n'
                'Appended keywords:\n%s\n' %
                (key,
                keywords,
                new_keywords))
            assert key in keywords, message
            message = (
                'Layer keywords misses appended value: %s\n'
                'Layer keywords:\n%s\n'
                'Appended keywords:\n%s\n' %
                (value,
                keywords,
                new_keywords))
            assert keywords[key] == value, message

    def test_read_db_keywords(self):
        """Can we read sqlite keywords with the generic readKeywords method
        """
        # noinspection PyUnresolvedReferences
        local_path = os.path.join(
            os.path.dirname(__file__), '../../..///', 'jk.sqlite')
        path = os.path.join(TESTDATA, 'test_keywords.db')
        self.keyword_io.set_keyword_db_path(path)
        # We need to make a local copy of the dataset so
        # that we can use a local path that will hash properly on the
        # database to return us the correct / valid keywords record.
        shutil.copy2(os.path.join(TESTDATA, 'jk.sqlite'), local_path)
        uri = QgsDataSourceURI()
        # always use relative path!
        uri.setDatabase('../jk.sqlite')
        uri.setDataSource('', 'osm_buildings', 'Geometry')
        # create a local version that has the relative url
        sqlite_layer = QgsVectorLayer(uri.uri(), 'OSM Buildings', 'spatialite')
        expected_source = (
            'dbname=\'../jk.sqlite\' table="osm_buildings" (Geometry) sql=')
        message = 'Got source: %s\n\nExpected %s\n' % (
            sqlite_layer.source, expected_source)
        assert sqlite_layer.source() == expected_source, message
        keywords = self.keyword_io.read_keywords(sqlite_layer)
        expected_keywords = self.expected_sqlite_keywords
        assert keywords == expected_keywords, message
        source = self.sqlite_layer.source()
        # delete sqlite_layer so that we can delete the file
        del sqlite_layer
        os.remove(local_path)
        message = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
            keywords, expected_keywords, source)
        assert keywords == expected_keywords, message

    def test_copy_keywords(self):
        """Test we can copy the keywords."""
        out_path = unique_filename(
            prefix='test_copy_keywords', suffix='.keywords')
        self.keyword_io.copy_keywords(self.raster_layer, out_path)
        copied_keywords = read_file_keywords(out_path)
        expected_keywords = self.expected_raster_keywords
        message = 'Got:\n%s\nExpected:\n%s\nSource:\n%s' % (
            copied_keywords, expected_keywords, out_path)
        self.assertEquals(copied_keywords, expected_keywords, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
