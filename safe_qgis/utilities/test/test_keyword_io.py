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

from qgis.core import QgsDataSourceURI, QgsVectorLayer

# For testing and demoing
from safe_qgis.utilities.utilities_for_testing import get_qgis_app, load_layer
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.exceptions import HashNotFoundError
from safe_qgis.tools.test.test_keywords_dialog import makePadangLayerClone
from safe_qgis.safe_interface import temp_dir, HAZDATA, TESTDATA

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Don't change this, not even formatting, you will break tests!
PG_URI = """'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
         type=MULTIPOLYGON table="valuations_parcel" (geometry) sql='"""


class KeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        self.keywordIO = KeywordIO()
        myUri = QgsDataSourceURI()
        myUri.setDatabase(os.path.join(TESTDATA, 'jk.sqlite'))
        myUri.setDataSource('', 'osm_buildings', 'Geometry')
        self.sqliteLayer = QgsVectorLayer(myUri.uri(), 'OSM Buildings',
                                          'spatialite')
        myHazardPath = os.path.join(HAZDATA, 'Shakemap_Padang_2009.asc')
        self.fileRasterLayer, myType = load_layer(
            myHazardPath, directory=None)
        del myType
        self.fileVectorLayer, myType = load_layer('Padang_WGS84.shp')
        del myType
        self.expectedSqliteKeywords = {
            'category': 'exposure',
            'datatype': 'OSM',
            'subcategory': 'building'}
        self.expectedVectorKeywords = {
            'category': 'exposure',
            'datatype': 'itb',
            'subcategory': 'structure',
            'title': 'Padang WGS84'}
        self.expectedRasterKeywords = {
            'category': 'hazard',
            'source': 'USGS',
            'subcategory': 'earthquake',
            'unit': 'MMI',
            'title': ('An earthquake in Padang '
            'like in 2009')}

    def tearDown(self):
        pass

    def test_getHashForDatasource(self):
        """Test we can reliably get a hash for a uri"""
        myHash = self.keywordIO.hash_for_datasource(PG_URI)
        myExpectedHash = '7cc153e1b119ca54a91ddb98a56ea95e'
        myMessage = "Got: %s\nExpected: %s" % (myHash, myExpectedHash)
        assert myHash == myExpectedHash, myMessage

    def test_writeReadKeywordFromUri(self):
        """Test we can set and get keywords for a non local datasource"""
        myHandle, myFilename = tempfile.mkstemp('.db', 'keywords_',
                                                temp_dir())

        # Ensure the file is deleted before we try to write to it
        # fixes windows specific issue where you get a message like this
        # ERROR 1: c:\temp\inasafe\clip_jpxjnt.shp is not a directory.
        # This is because mkstemp creates the file handle and leaves
        # the file open.
        os.close(myHandle)
        os.remove(myFilename)
        myExpectedKeywords = {'category': 'exposure',
                              'datatype': 'itb',
                              'subcategory': 'building'}
        # SQL insert test
        # On first write schema is empty and there is no matching hash
        self.keywordIO.set_keyword_db_path(myFilename)
        self.keywordIO.write_keywords_for_uri(PG_URI, myExpectedKeywords)
        # SQL Update test
        # On second write schema is populated and we update matching hash
        myExpectedKeywords = {'category': 'exposure',
                              'datatype': 'OSM',  # <--note the change here!
                              'subcategory': 'building'}
        self.keywordIO.write_keywords_for_uri(PG_URI, myExpectedKeywords)
        # Test getting all keywords
        myKeywords = self.keywordIO.read_keyword_from_uri(PG_URI)
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeywords, myExpectedKeywords, myFilename)
        assert myKeywords == myExpectedKeywords, myMessage
        # Test getting just a single keyword
        myKeyword = self.keywordIO.read_keyword_from_uri(PG_URI, 'datatype')
        myExpectedKeyword = 'OSM'
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeyword, myExpectedKeyword, myFilename)
        assert myKeyword == myExpectedKeyword, myMessage
        # Test deleting keywords actually does delete
        self.keywordIO.delete_keywords_for_uri(PG_URI)
        try:
            myKeyword = self.keywordIO.read_keyword_from_uri(PG_URI,
                                                             'datatype')
            #if the above didnt cause an exception then bad
            myMessage = 'Expected a HashNotFoundError to be raised'
            assert myMessage
        except HashNotFoundError:
            #we expect this outcome so good!
            pass

    def test_areKeywordsFileBased(self):
        """Can we correctly determine if keywords should be written to file or
        to database?"""
        assert not self.keywordIO.are_keywords_file_based(self.sqliteLayer)
        assert self.keywordIO.are_keywords_file_based(self.fileRasterLayer)
        assert self.keywordIO.are_keywords_file_based(self.fileVectorLayer)

    def test_readRasterFileKeywords(self):
        """Can we read raster file keywords using generic readKeywords method
        """
        myKeywords = self.keywordIO.read_keywords(self.fileRasterLayer)
        myExpectedKeywords = self.expectedRasterKeywords
        mySource = self.fileRasterLayer.source()
        myMessage = 'Got:\n%s\nExpected:\n%s\nSource:\n%s' % (
                    myKeywords, myExpectedKeywords, mySource)
        assert myKeywords == myExpectedKeywords, myMessage

    def test_readVectorFileKeywords(self):
        """Test read vector file keywords with the generic readKeywords method.
         """
        myKeywords = self.keywordIO.read_keywords(self.fileVectorLayer)
        myExpectedKeywords = self.expectedVectorKeywords
        mySource = self.fileVectorLayer.source()
        myMessage = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
                    myKeywords, myExpectedKeywords, mySource)
        assert myKeywords == myExpectedKeywords, myMessage

    def test_appendKeywords(self):
        """Can we append file keywords with the generic readKeywords method."""
        myLayer, _ = makePadangLayerClone()
        myNewKeywords = {'category': 'exposure', 'test': 'TEST'}
        self.keywordIO.update_keywords(myLayer, myNewKeywords)
        myKeywords = self.keywordIO.read_keywords(myLayer)

        for myKey, myValue in myNewKeywords.iteritems():
            myMessage = (
                'Layer keywords misses appended key: %s\n'
                'Layer keywords:\n%s\n'
                'Appended keywords:\n%s\n' %
                (myKey,
                myKeywords,
                myNewKeywords))
            assert myKey in myKeywords, myMessage
            myMessage = (
                'Layer keywords misses appended value: %s\n'
                'Layer keywords:\n%s\n'
                'Appended keywords:\n%s\n' %
                (myValue,
                myKeywords,
                myNewKeywords))
            assert myKeywords[myKey] == myValue, myMessage

    def test_readDBKeywords(self):
        """Can we read sqlite keywords with the generic readKeywords method
        """
        myLocalPath = os.path.join(os.path.dirname(__file__),
                                   '../../..///', 'jk.sqlite')
        myPath = os.path.join(TESTDATA, 'test_keywords.db')
        self.keywordIO.set_keyword_db_path(myPath)
        # We need to make a local copy of the dataset so
        # that we can use a local path that will hash properly on the
        # database to return us the correct / valid keywords record.
        shutil.copy2(os.path.join(TESTDATA, 'jk.sqlite'), myLocalPath)
        myUri = QgsDataSourceURI()
        # always use relative path!
        myUri.setDatabase('../jk.sqlite')
        myUri.setDataSource('', 'osm_buildings', 'Geometry')
        # create a local version that has the relative url
        mySqliteLayer = QgsVectorLayer(myUri.uri(), 'OSM Buildings',
                                       'spatialite')
        myExpectedSource = ('dbname=\'../jk.sqlite\' table="osm_buildings"'
                            ' (Geometry) sql=')
        myMessage = 'Got source: %s\n\nExpected %s\n' % (
                    mySqliteLayer.source, myExpectedSource)
        assert mySqliteLayer.source() == myExpectedSource, myMessage
        myKeywords = self.keywordIO.read_keywords(mySqliteLayer)
        myExpectedKeywords = self.expectedSqliteKeywords
        assert myKeywords == myExpectedKeywords, myMessage
        mySource = self.sqliteLayer.source()
        # delete mySqliteLayer so that we can delete the file
        del mySqliteLayer
        os.remove(myLocalPath)
        myMessage = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
                    myKeywords, myExpectedKeywords, mySource)
        assert myKeywords == myExpectedKeywords, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
