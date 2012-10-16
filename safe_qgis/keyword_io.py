"""**Keyword IO implementation.**

.. tip:: Provides functionality for reading and writing keywords from within
   QGIS. It is an abstration for the keywords system used by the underlying
   library.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import sqlite3 as sqlite
import cPickle as pickle

from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSettings
from qgis.core import QgsMapLayer

from safe_qgis.exceptions import (HashNotFoundException,
                                  KeywordNotFoundException)
from safe_qgis.safe_interface import (verify,
                                      readKeywordsFromFile,
                                      writeKeywordsToFile)
from safe_qgis.utilities import qgisVersion

LOGGER = logging.getLogger('InaSAFE')


class KeywordIO(QObject):
    """Class for doing keyword read/write operations.

    It abstracts away differences between using SAFE to get keywords from a
    .keywords file and this plugins implemenation of keyword caching in a local
    sqlite db used for supporting keywords for remote datasources."""

    def __init__(self):
        """Constructor for the KeywordIO object.

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        QObject.__init__(self)
        # path to sqlite db path
        self.keywordDbPath = None
        self.setupKeywordDbPath()
        self.connection = None

    def setKeywordDbPath(self, thePath):
        """Set the path for the keyword database (sqlite).

        The file will be used to search for keywords for non local datasets.

        Args:
            thePath - a valid path to a sqlite database. The database does
            not need to exist already, but the user should be able to write
            to the path provided.
        Returns:
            None
        Raises:
            None
        """
        self.keywordDbPath = str(thePath)

    def readKeywords(self, theLayer, theKeyword=None):
        """Read keywords for a datasource and return them as a dictionary.
        This is a wrapper method that will 'do the right thing' to fetch
        keywords for the given datasource. In particular, if the datasource
        is remote (e.g. a database connection) it will fetch the keywords from
        the keywords store.

        Args:
            * theLayer - A QGIS QgsMapLayer instance.
            * theKeyword - optional - will extract only the specified keyword
              from the keywords dict.
        Returns:
            A dict if theKeyword is omitted, otherwise the value for the
            given key if it is present.
        Raises:
            Propogates any exception from the underlying reader delegate.
        """
        mySource = str(theLayer.source())
        myFlag = self.areKeywordsFileBased(theLayer)
        myKeywords = None

        try:
            if myFlag:
                myKeywords = readKeywordsFromFile(mySource, theKeyword)
            else:
                myKeywords = self.readKeywordFromUri(mySource, theKeyword)
            return myKeywords
        except (HashNotFoundException, Exception):
            raise

    def writeKeywords(self, theLayer, theKeywords):
        """Write keywords for a datasource.
        This is a wrapper method that will 'do the right thing' to store
        keywords for the given datasource. In particular, if the datasource
        is remote (e.g. a database connection) it will write the keywords from
        the keywords store.

        Args:
            * theLayer - A QGIS QgsMapLayer instance.
            * theKeywords - a dict containing all the keywords to be written
              for the layer.
        Returns:
            None.
        Raises:
            None
        """
        mySource = str(theLayer.source())
        myFlag = self.areKeywordsFileBased(theLayer)
        try:
            if myFlag:
                writeKeywordsToFile(mySource, theKeywords)
            else:
                self.writeKeywordsForUri(mySource, theKeywords)
            return
        except:
            raise

    def appendKeywords(self, theLayer, theKeywords):
        """Write keywords for a datasource.

        Args:
            * theLayer - A QGIS QgsMapLayer instance.
            * theKeywords - a dict containing all the keywords to be added
              for the layer.
        Returns:
            None.
        Raises:
            None
        """
        myKeywords = self.readKeywords(theLayer)
        myKeywords.update(theKeywords)
        self.writeKeywords(theLayer, myKeywords)

    def copyKeywords(self, theSourceLayer,
                     theDestinationFile, theExtraKeywords=None):
        """Helper to copy the keywords file from a source dataset
        to a destination dataset.

        e.g.::

            copyKeywords('foo.shp', 'bar.shp')

        Will result in the foo.keywords file being copied to bar.keyword.

        Optional argument extraKeywords is a dictionary with additional
        keywords that will be added to the destination file
        e.g::

            copyKeywords('foo.shp', 'bar.shp', {'resolution': 0.01})

        Args:
            * theSourceLayer - A QGIS QgsMapLayer instance.
            * theDestinationFile - the output filename that should be used
              to store the keywords in. It can be a .shp or a .keywords for
              exampled since the suffix will always be replaced with .keywords.
            * theExtraKeywords - a dict containing all the extra keywords to be
              written for the layer. The written keywords will consist of any
              original keywords from the source layer's keywords file and
              and the extra keywords (which will replace the source layers
              keywords if the key is identical).
        Returns:
            None.
        Raises:
            None
        """
        myKeywords = self.readKeywords(theSourceLayer)
        if theExtraKeywords is None:
            theExtraKeywords = {}
        myMessage = self.tr('Expected extraKeywords to be a dictionary. Got %s'
               % str(type(theExtraKeywords))[1:-1])
        verify(isinstance(theExtraKeywords, dict), myMessage)
        # compute the output keywords file name
        myDestinationBase = os.path.splitext(theDestinationFile)[0]
        myNewDestination = myDestinationBase + '.keywords'
        # write the extra keywords into the source dict
        try:
            for key in theExtraKeywords:
                myKeywords[key] = theExtraKeywords[key]
            writeKeywordsToFile(myNewDestination, myKeywords)
        except Exception, e:
            myMessage = self.tr('Failed to copy keywords file from :'
                           '\n%s\nto\%s: %s' %
                   (theSourceLayer.source(), myNewDestination, str(e)))
            raise Exception(myMessage)
        return
# methods below here should be considered private

    def defaultKeywordDbPath(self):
        """Helper to get the default path for the keywords file (which is
        <plugin dir>/keywords.db)

        Args:
            None
        Returns:
            A string representing the path to where the keywords file is to be.
        Raises:
            None
        """
        myParentDir = os.path.abspath(
                                    os.path.join(
                                        os.path.dirname(__file__), '..'))
        return os.path.join(myParentDir, 'keywords.db')

    def setupKeywordDbPath(self):
        """Helper to set the active path for the keywords. Called at init time,
        you can override this path by calling setKeywordDbPath.

        Args:
            None
        Returns:
            A string representing the path to where the keywords file is to be.
            If the user has never specified what this path is, the
            defaultKeywordDbPath is returned.
        Raises:
            None
        """
        mySettings = QSettings()
        myPath = mySettings.value(
                                'inasafe/keywordCachePath',
                                self.defaultKeywordDbPath()).toString()
        self.keywordDbPath = str(myPath)

    def openConnection(self):
        """Open an sqlite connection to the keywords database.
        By default the keywords database will be used in the plugin dir,
        unless an explicit path has been set using setKeywordDbPath, or
        overridden in QSettings. If the db does not exist it will
        be created.

        Args:
            thePath - path to the desired sqlite db to use.
        Returns:
            None
        Raises:
            An sqlite.Error is raised if anything goes wrong
        """
        self.connection = None
        try:
            self.connection = sqlite.connect(self.keywordDbPath)
        except sqlite.Error, e:
            print "Error %s:" % e.args[0]
            raise

    def closeConnection(self):
        """Given an sqlite3 connection, close it.

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def getCursor(self):
        """Get a cursor for the active connection. The cursor can be used to
        execute arbitrary queries against the database. This method also checks
        that the keywords table exists in the schema, and if not, it creates
        it.

        Args:
            theConnection - a valid, open sqlite3 database connection.
        Returns:
            a valid cursor opened against the connection.
        Raises:
            An sqlite.Error will be raised if anything goes wrong
        """
        if self.connection is None:
            self.openConnection()
        try:
            myCursor = self.connection.cursor()
            myCursor.execute('SELECT SQLITE_VERSION()')
            myData = myCursor.fetchone()
            #print "SQLite version: %s" % myData
            # Check if we have some tables, if not create them
            mySQL = 'select sql from sqlite_master where type = \'table\';'
            myCursor.execute(mySQL)
            myData = myCursor.fetchone()
            #print "Tables: %s" % myData
            if myData is None:
                #print 'No tables found'
                mySQL = ('create table keyword (hash varchar(32) primary key,'
                         'dict text);')
                print mySQL
                myCursor.execute(mySQL)
                myData = myCursor.fetchone()
            else:
                #print 'Keywords table already exists'
                pass
            return myCursor
        except sqlite.Error, e:
            print "Error %s:" % e.args[0]
            raise

    def areKeywordsFileBased(self, theLayer):
        """Find out if keywords should be read/written to file or our keywords
          db.

        Args:
            * theLayer - A QGIS QgsMapLayer instance.

        Returns:
            True if keywords are storedin a file next to the dataset,
            else False if the dataset is remove e.g. a database.
        Raises:
            None
        """
        # determine which keyword lookup system to use (file base or cache db)
        # based on the layer's provider type. True indicates we should use the
        # datasource as a file and look for a keywords file, false and we look
        # in the keywords db.
        myProviderType = None
        myVersion = qgisVersion()
        # check for old raster api with qgis < 1.8
        # ..todo:: Add test for plugin layers too
        if (myVersion < 10800 and
                theLayer.type() == QgsMapLayer.RasterLayer):
            myProviderType = str(theLayer.providerKey())
        else:
            myProviderType = str(theLayer.providerType())

        myProviderDict = {'ogr': True,
                          'gdal': True,
                          'gpx': False,
                          'wms': False,
                          'spatialite': False,
                          'delimitedtext': True,
                          'postgres': False}
        myFileBasedKeywords = False
        if myProviderType in myProviderDict:
            myFileBasedKeywords = myProviderDict[myProviderType]
        return myFileBasedKeywords

    def getHashForDatasource(self, theDataSource):
        """Given a datasource, return its hash.

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        import hashlib
        myHash = hashlib.md5()
        myHash.update(theDataSource)
        myHash = myHash.hexdigest()
        return myHash

    def deleteKeywordsForUri(self, theUri):
        """Delete keywords for a URI in the keywords database.
        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the keywords. If there is an existing
        record for the hash, the entire record will be erased.

        .. seealso:: writeKeywordsForUri, readKeywordsForUri

        Args:

           * theUri -  a str representing a layer uri as parameter.
             .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
             password=\'bar\' sslmode=disable key=\'id\' srid=4326

        Returns:
           None

        Raises:
           None
        """
        myHash = self.getHashForDatasource(theUri)
        try:
            myCursor = self.getCursor()
            #now see if we have any data for our hash
            mySQL = 'delete from keyword where hash = \'' + myHash + '\';'
            myCursor.execute(mySQL)
            self.connection.commit()
        except sqlite.Error, e:
            print "SQLITE Error %s:" % e.args[0]
            self.connection.rollback()
        except Exception, e:
            print "Error %s:" % e.args[0]
            self.connection.rollback()
            raise
        finally:
            self.closeConnection()

    def writeKeywordsForUri(self, theUri, theKeywords):
        """Write keywords for a URI into the keywords database. All the
        keywords for the uri should be written in a single operation.
        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the keywords. If there is an existing
        record it will be updated, if not, a new one will be created.

        .. seealso:: readKeywordFromUri, deleteKeywordsForUri

        Args:

           * theUri -  a str representing a layer uri as parameter.
             .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
             password=\'bar\' sslmode=disable key=\'id\' srid=4326
           * keywords - mandatory - the metadata keyword to retrieve e.g.
             'title'

        Returns:
           A string containing the retrieved value for the keyword if
           the keyword argument is specified, otherwise the
           complete keywords dictionary is returned.

        Raises:
           KeywordNotFoundException if the keyword is not recognised.
        """
        myHash = self.getHashForDatasource(theUri)
        try:
            myCursor = self.getCursor()
            #now see if we have any data for our hash
            mySQL = 'select dict from keyword where hash = \'' + myHash + '\';'
            myCursor.execute(mySQL)
            myData = myCursor.fetchone()
            myPickle = pickle.dumps(theKeywords, pickle.HIGHEST_PROTOCOL)
            if myData is None:
                #insert a new rec
                #myCursor.execute('insert into keyword(hash) values(:hash);',
                #             {'hash': myHash})
                myCursor.execute('insert into keyword(hash, dict) values('
                                 ':hash, :dict);',
                             {'hash': myHash, 'dict': sqlite.Binary(myPickle)})
                self.connection.commit()
            else:
                #update existing rec
                myCursor.execute('update keyword set dict=? where hash = ?;',
                             (sqlite.Binary(myPickle), myHash))
                self.connection.commit()
        except sqlite.Error, e:
            print "SQLITE Error %s:" % e.args[0]
            self.connection.rollback()
        except Exception, e:
            print "Error %s:" % e.args[0]
            self.connection.rollback()
            raise
        finally:
            self.closeConnection()

    def readKeywordFromUri(self, theUri, theKeyword=None):
        """Get metadata from the keywords file associated with a
        non local layer (e.g. postgresql connection).

        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the keywords. If there is an existing
        record it will be returned, if not and error will be thrown.

        .. seealso:: writeKeywordsForUri,deleteKeywordsForUri

        Args:

           * theUri -  a str representing a layer uri as parameter.
             .e.g. 'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
             password=\'bar\' sslmode=disable key=\'id\' srid=4326
           * keyword - optional - the metadata keyword to retrieve e.g. 'title'

        Returns:
           A string containing the retrieved value for the keyword if
           the keyword argument is specified, otherwise the
           complete keywords dictionary is returned.

        Raises:
           KeywordNotFoundException if the keyword is not found.
        """
        myHash = self.getHashForDatasource(theUri)
        self.openConnection()
        try:
            myCursor = self.getCursor()
            #now see if we have any data for our hash
            mySQL = 'select dict from keyword where hash = \'' + myHash + '\';'
            myCursor.execute(mySQL)
            myData = myCursor.fetchone()
            #unpickle it to get our dict back
            if myData is None:
                raise HashNotFoundException('No hash found for %s' % myHash)
            myData = myData[0]  # first field
            myDict = pickle.loads(str(myData))
            if theKeyword is None:
                return myDict
            if theKeyword in myDict:
                return myDict[theKeyword]
            else:
                raise KeywordNotFoundException('No hash found for %s' % myHash)

        except sqlite.Error, e:
            print "Error %s:" % e.args[0]
        except Exception, e:
            print "Error %s:" % e.args[0]
            raise
        finally:
            self.closeConnection()
