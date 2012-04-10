import unittest
import sys
import os
import tempfile

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from utilities_test import (getQgisTestApp, loadLayer)
from is_keyword_io import ISKeywordIO
from is_exceptions import HashNotFoundException
from is_utilities import getTempDir

from storage.utilities_test import TESTDATA
from qgis.core import (QgsDataSourceURI,
                       QgsVectorLayer)
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
#Dont change this, not even formatting, you will break tests!
PG_URI = """'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
         type=MULTIPOLYGON table="valuations_parcel" (geometry) sql='"""


class ISKeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        self.keywordIO = ISKeywordIO()
        myUri = QgsDataSourceURI()
        myUri.setDatabase(os.path.join(TESTDATA, 'js.sqlite'))
        myUri.setDataSource('', 'osm_buildings', 'Geometry')
        self.sqliteLayer = QgsVectorLayer(myUri.uri(), 'OSM Buildings',
                                       'spatialite')
        self.fileRasterLayer, myType = loadLayer('Shakemap_Padang_2009.asc')
        del myType
        self.fileVectorLayer, myType = loadLayer('Padang_WGS84.shp')
        del myType

    def tearDown(self):
        pass

    def test_getHashForDatasource(self):
        """Test we can reliably get a hash for a uri"""
        myHash = self.keywordIO.getHashForDatasource(PG_URI)
        myExpectedHash = '7cc153e1b119ca54a91ddb98a56ea95e'
        myMessage = "Got: %s\nExpected: %s" % (myHash, myExpectedHash)
        assert myHash == myExpectedHash, myMessage

    def test_writeReadKeywordFromUri(self):
        """Test we can set and get keywords for a non local datasource"""
        myHandle, myFilename = tempfile.mkstemp('.db', 'keywords_',
                                            getTempDir())

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
        self.keywordIO.writeKeywordsForUri(PG_URI,
                                           myExpectedKeywords, myFilename)
        # SQL Update test
        # On second write schema is populated and we update matching hash
        myExpectedKeywords = {'category': 'exposure',
                              'datatype': 'OSM',  # <--note the change here!
                              'subcategory': 'building'}
        self.keywordIO.writeKeywordsForUri(PG_URI,
                                           myExpectedKeywords, myFilename)
        # Test getting all keywords
        myKeywords = self.keywordIO.readKeywordFromUri(PG_URI,
                                            theDatabasePath=myFilename)
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeywords, myExpectedKeywords, myFilename)
        assert myKeywords == myExpectedKeywords, myMessage
        # Test getting just a single keyword
        myKeyword = self.keywordIO.readKeywordFromUri(PG_URI, 'datatype',
                                        theDatabasePath=myFilename)
        myExpectedKeyword = 'OSM'
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeyword, myExpectedKeyword, myFilename)
        assert myKeyword == myExpectedKeyword, myMessage
        # Test deleting keywords actually does delete
        self.keywordIO.deleteKeywordsForUri(PG_URI, myFilename)
        try:
            myKeyword = self.keywordIO.readKeywordFromUri(PG_URI, 'datatype',
                                        theDatabasePath=myFilename)
            #if the above didnt cause an exception then bad
            myMessage = 'Expected a HashNotFoundException to be raised'
            assert myMessage
        except HashNotFoundException:
            #we expect this outcome so good!
            pass

    def test_areKeywordsFileBased(self):
        """Can we correctly determine if keywords should be written to file or
        to database?"""
        assert not self.keywordIO.areKeywordsFileBased(self.sqliteLayer)
        assert self.keywordIO.areKeywordsFileBased(self.fileRasterLayer)
        assert self.keywordIO.areKeywordsFileBased(self.fileVectorLayer)

    def test_readKeywords(self):
        """Test we can read keywords using the generic readKeywords method"""
        pass

if __name__ == '__main__':
    suite = unittest.makeSuite(ISKeywordIOTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
