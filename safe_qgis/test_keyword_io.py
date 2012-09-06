import unittest
import sys
import os
import tempfile
# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
from safe.common.utilities import temp_dir

pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from qgis.core import (QgsDataSourceURI, QgsVectorLayer)

# For testing and demoing
from safe.common.testing import HAZDATA, UNITDATA
from safe_qgis.utilities_test import (getQgisTestApp, loadLayer)
from safe_qgis.keyword_io import KeywordIO
from safe_qgis.exceptions import HashNotFoundException
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()

# Don't change this, not even formatting, you will break tests!
PG_URI = """'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
         type=MULTIPOLYGON table="valuations_parcel" (geometry) sql="""


class KeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        self.keywordIO = KeywordIO()
        myUri = QgsDataSourceURI()
        myUri.setDatabase(os.path.join(
            UNITDATA, 'exposure', 'exposure.sqlite'))
        myUri.setDataSource('', 'buildings_osm_4326', 'Geometry')
        self.sqliteBuildingsLayer = QgsVectorLayer(myUri.uri(),
                                                   'OSM Buildings',
                                                   'spatialite')
        assert self.sqliteBuildingsLayer.isValid(), myUri.database()

        myUri.setDataSource('', 'indonesia_highway', 'geom')
        self.sqliteRoadsLayer = QgsVectorLayer(myUri.uri(),
                                               'Indonesia Highways',
                                               'spatialite')

        myHazardPath = os.path.join(HAZDATA, 'Shakemap_Padang_2009.asc')
        # _ is syntactic sugar to ignore a var
        self.fileRasterLayer, _ = loadLayer(myHazardPath,
                                                 theDirectory=None)
        self.fileVectorLayer, _ = loadLayer('Padang_WGS84.shp')

        self.expectedBuildingsKeywords = {'category': 'exposure',
                                       'datatype': 'osm',
                                       'subcategory': 'building',
                                       'title': 'buildings_osm_4326'}
        self.expectedRoadsKeywords = {'category': 'exposure',
                                       'subcategory': 'roads'}
        self.expectedVectorKeywords = {'category': 'exposure',
                                       'datatype': 'itb',
                                       'subcategory': 'building'}
        self.expectedRasterKeywords = {'category': 'hazard',
                                       'subcategory': 'earthquake',
                                       'unit': 'MMI',
                                       'title': ('An earthquake in Padang '
                                                 'like in 2009')}

    def tearDown(self):
        pass

    def test_getHashForDatasource(self):
        """Test we can reliably get a hash for a uri"""
        myHash = self.keywordIO.getHashForDatasource(PG_URI)
        myExpectedHash = '5acf4de7324339af7f8143c0454b395a'
        myMessage = "Got: %s\nExpected: %s" % (myHash, myExpectedHash)
        assert myHash == myExpectedHash, myMessage

    def test_getSqliteSubLayer(self):
        """Test we can reliably get a sublayer name for a qgis sqlite layer"""
        mySubLayerName = self.keywordIO.subLayerName(self.sqliteBuildingsLayer)
        myExpectedName = 'exposure.buildings_osm_4326'
        myMessage = "\nGot:\n%s\nExpected:\n%s" % (
                      mySubLayerName, myExpectedName)
        assert mySubLayerName == myExpectedName, myMessage

    def test_getFileSubLayer(self):
        """Test we can reliably get a sublayer name for a qgis layer"""
        mySubLayerName = self.keywordIO.subLayerName(self.fileVectorLayer)
        myExpectedName = 'Padang_WGS84'
        myMessage = "\nGot:\n%s\nExpected:\n%s" % (
                      mySubLayerName, myExpectedName)
        assert mySubLayerName == myExpectedName, myMessage

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
        self.keywordIO.setKeywordDbPath(myFilename)
        self.keywordIO.writeKeywordsForUri(PG_URI, myExpectedKeywords)
        # SQL Update test
        # On second write schema is populated and we update matching hash
        myExpectedKeywords = {'category': 'exposure',
                              'datatype': 'OSM',  # <--note the change here!
                              'subcategory': 'building'}
        self.keywordIO.writeKeywordsForUri(PG_URI, myExpectedKeywords)
        # Test getting all keywords
        myKeywords = self.keywordIO.readKeywordFromUri(PG_URI)
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeywords, myExpectedKeywords, myFilename)
        assert myKeywords == myExpectedKeywords, myMessage
        # Test getting just a single keyword
        myKeyword = self.keywordIO.readKeywordFromUri(PG_URI, 'datatype')
        myExpectedKeyword = 'OSM'
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeyword, myExpectedKeyword, myFilename)
        assert myKeyword == myExpectedKeyword, myMessage
        # Test deleting keywords actually does delete
        self.keywordIO.deleteKeywordsForUri(PG_URI)
        try:
            myKeyword = self.keywordIO.readKeywordFromUri(PG_URI, 'datatype')
            #if the above didnt cause an exception then bad
            myMessage = 'Expected a HashNotFoundException to be raised'
            assert myMessage
        except HashNotFoundException:
            #we expect this outcome so good!
            pass

    def test_dataSourceIsFileBased(self):
        """Can we correctly determine if keywords should be written to file or
        to database?"""
        assert self.keywordIO.dataSourceIsFileBased(self.sqliteBuildingsLayer)
        assert self.keywordIO.dataSourceIsFileBased(self.fileRasterLayer)
        assert self.keywordIO.dataSourceIsFileBased(self.fileVectorLayer)

    def test_readRasterFileKeywords(self):
        """Can we read raster file keywords using generic readKeywords method
        """
        myKeywords = self.keywordIO.readKeywords(self.fileRasterLayer)
        myExpectedKeywords = self.expectedRasterKeywords
        mySource = self.fileRasterLayer.source()
        myMessage = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
                    myKeywords, myExpectedKeywords, mySource)
        assert myKeywords == myExpectedKeywords, myMessage

    def test_readVectorFileKeywords(self):
        """Can we read vector file keywords with the generic readKeywords
        method """
        myKeywords = self.keywordIO.readKeywords(self.fileVectorLayer)
        myExpectedKeywords = self.expectedVectorKeywords
        mySource = self.fileVectorLayer.source()
        myMessage = 'Got: %s\n\nExpected %s\n\nSource: %s' % (
                    myKeywords, myExpectedKeywords, mySource)
        assert myKeywords == myExpectedKeywords, myMessage

    def test_readSqliteBKeywords(self):
        """Can we read sqlite keywords with the generic readKeywords method
        """
        myKeywords = self.keywordIO.readKeywords(self.sqliteBuildingsLayer)
        myMessage = 'Got: %s\n\nExpected %s' % (
                    myKeywords, self.expectedBuildingsKeywords)
        assert myKeywords == self.expectedBuildingsKeywords, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
