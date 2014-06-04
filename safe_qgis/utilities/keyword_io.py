# coding=utf-8
"""**Keyword IO implementation.**

.. tip:: Provides functionality for reading and writing keywords from within
   QGIS. It is an abstraction for the keywords system used by the underlying
   library.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
from os.path import expanduser
import logging
import sqlite3 as sqlite
from sqlite3 import OperationalError
import cPickle as pickle

from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSettings

from safe_qgis.exceptions import (
    HashNotFoundError,
    KeywordNotFoundError,
    KeywordDbError,
    InvalidParameterError,
    NoKeywordsFoundError,
    UnsupportedProviderError)
from safe_qgis.safe_interface import (
    verify,
    read_file_keywords,
    write_keywords_to_file)

LOGGER = logging.getLogger('InaSAFE')


class KeywordIO(QObject):
    """Class for doing keyword read/write operations.

    It abstracts away differences between using SAFE to get keywords from a
    .keywords file and this plugins implementation of keyword caching in a
    local sqlite db used for supporting keywords for remote datasources."""

    def __init__(self):
        """Constructor for the KeywordIO object."""
        QObject.__init__(self)
        # path to sqlite db path
        self.keyword_db_path = None
        self.setup_keyword_db_path()
        self.connection = None

    def set_keyword_db_path(self, path):
        """Set the path for the keyword database (sqlite).

        The file will be used to search for keywords for non local datasets.

        :param path: A valid path to a sqlite database. The database does
            not need to exist already, but the user should be able to write
            to the path provided.
        :type path: str
        """
        self.keyword_db_path = str(path)

    def read_keywords(self, layer, keyword=None):
        """Read keywords for a datasource and return them as a dictionary.

        This is a wrapper method that will 'do the right thing' to fetch
        keywords for the given datasource. In particular, if the datasource
        is remote (e.g. a database connection) it will fetch the keywords from
        the keywords store.

        :param layer:  A QGIS QgsMapLayer instance that you want to obtain
            the keywords for.
        :type layer: QgsMapLayer

        :param keyword: If set, will extract only the specified keyword
              from the keywords dict.
        :type keyword: str

        :returns: A dict if keyword is omitted, otherwise the value for the
            given key if it is present.
        :rtype: dict, str

        TODO: Don't raise generic exceptions.

        :raises: HashNotFoundError, Exception, OperationalError,
            NoKeywordsFoundError, KeywordNotFoundError, InvalidParameterError,
            UnsupportedProviderError

        """
        source = str(layer.source())
        try:
            flag = self.are_keywords_file_based(layer)
        except UnsupportedProviderError:
            raise

        try:
            if flag:
                keywords = read_file_keywords(source, keyword)
            else:
                keywords = self.read_keyword_from_uri(source, keyword)
            return keywords
        except (HashNotFoundError,
                Exception,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            raise

    def write_keywords(self, layer, keywords):
        """Write keywords for a datasource.

        This is a wrapper method that will 'do the right thing' to store
        keywords for the given datasource. In particular, if the datasource
        is remote (e.g. a database connection) it will write the keywords from
        the keywords store.

        :param layer: A QGIS QgsMapLayer instance.
        :type layer: QgsMapLayer

        :param keywords: A dict containing all the keywords to be written
              for the layer.
        :type keywords: dict

        :raises: UnsupportedProviderError
        """
        try:
            flag = self.are_keywords_file_based(layer)
        except UnsupportedProviderError:
            raise

        source = str(layer.source())
        try:
            if flag:
                write_keywords_to_file(source, keywords)
            else:
                self.write_keywords_for_uri(source, keywords)
            return
        except:
            raise

    def update_keywords(self, layer, keywords):
        """Update keywords for a datasource.

        :param layer: A QGIS QgsMapLayer instance.
        :type layer: QgsMapLayer

        :param keywords: A dict containing all the keywords to be updated
              for the layer.
        :type keywords: dict
        """
        try:
            existing_keywords = self.read_keywords(layer)
        except (HashNotFoundError, OperationalError, InvalidParameterError):
            existing_keywords = {}
        existing_keywords.update(keywords)
        try:
            self.write_keywords(layer, existing_keywords)
        except OperationalError, e:
            message = (
                self.tr('Keyword database path: %s') %
                self.keyword_db_path)
            raise KeywordDbError(str(e) + '\n' + message)

    def copy_keywords(
            self,
            source_layer,
            destination_file,
            extra_keywords=None):
        """Helper to copy the keywords file from a source to a target dataset.

        e.g.::

            copyKeywords('foo.shp', 'bar.shp')

        Will result in the foo.keywords file being copied to bar.keyword.

        Optional argument extraKeywords is a dictionary with additional
        keywords that will be added to the destination file e.g::

            copyKeywords('foo.shp', 'bar.shp', {'resolution': 0.01})

        :param source_layer: A QGIS QgsMapLayer instance.
        :type source_layer: QgsMapLayer

        :param destination_file: The output filename that should be used
            to store the keywords in. It can be a .shp or a .keywords for
            example since the suffix will always be replaced with .keywords.
        :type destination_file: str

        :param extra_keywords: A dict containing all the extra keywords
            to be written for the layer. The written keywords will consist of
            any original keywords from the source layer's keywords file and
            and the extra keywords (which will replace the source layers
            keywords if the key is identical).
        :type extra_keywords: dict

        """
        keywords = self.read_keywords(source_layer)
        if extra_keywords is None:
            extra_keywords = {}
        message = self.tr(
            'Expected extraKeywords to be a dictionary. Got '
            '%s' % str(type(extra_keywords))[1:-1])
        verify(isinstance(extra_keywords, dict), message)
        # compute the output keywords file name
        destination_base = os.path.splitext(destination_file)[0]
        new_destination = destination_base + '.keywords'
        # write the extra keywords into the source dict
        try:
            for key in extra_keywords:
                keywords[key] = extra_keywords[key]
            write_keywords_to_file(new_destination, keywords)
        except Exception, e:
            message = self.tr(
                'Failed to copy keywords file from : \n%s\nto\n%s: %s' % (
                source_layer.source(), new_destination, str(e)))
            raise Exception(message)
        return

    def clear_keywords(self, layer):
        """Convenience method to clear a layer's keywords.

        :param layer: A QGIS QgsMapLayer instance.
        :type layer: QgsMapLayer
        """

        self.write_keywords(layer, dict())

    def delete_keywords(self, layer, keyword):
        """Delete the keyword for a given layer..

        This is a wrapper method that will 'do the right thing' to fetch
        keywords for the given datasource. In particular, if the datasource
        is remote (e.g. a database connection) it will fetch the keywords from
        the keywords store.

        :param layer: A QGIS QgsMapLayer instance.
        :type layer: QgsMapLayer

        :param keyword: The specified keyword will be deleted
              from the keywords dict.
        :type keyword: str

        :returns: True if the keyword was sucessfully delete. False otherwise.
        :rtype: bool
        """

        try:
            keywords = self.read_keywords(layer)
            keywords.pop(keyword)
            self.write_keywords(layer, keywords)
            return True
        except (HashNotFoundError, KeyError):
            return False

# methods below here should be considered private

    def default_keyword_db_path(self):
        """Helper to get the default path for the keywords file.

        :returns: The path to where the default location of the keywords
            database is. Maps to which is ~/.inasafe/keywords.db
        :rtype: str
        """

        home = expanduser("~")
        home = os.path.abspath(os.path.join(home, '.inasafe', 'keywords.db'))

        return home

    def setup_keyword_db_path(self):
        """Helper to set the active path for the keywords.

        Called at init time, you can override this path by calling
        set_keyword_db_path.setKeywordDbPath.

        :returns: The path to where the keywords file is. If the user has
            never specified what this path is, the defaultKeywordDbPath is
            returned.
        :rtype: str
        """
        settings = QSettings()
        path = settings.value(
            'inasafe/keywordCachePath',
            self.default_keyword_db_path(), type=str)
        self.keyword_db_path = str(path)

    def open_connection(self):
        """Open an sqlite connection to the keywords database.

        By default the keywords database will be used in the plugin dir,
        unless an explicit path has been set using setKeywordDbPath, or
        overridden in QSettings. If the db does not exist it will
        be created.

        :raises: An sqlite.Error is raised if anything goes wrong
        """
        self.connection = None
        base_directory = os.path.dirname(self.keyword_db_path)
        if not os.path.exists(base_directory):
            try:
                os.mkdir(base_directory)
            except IOError:
                LOGGER.exception(
                    'Could not create directory for keywords cache.')
                raise

        try:
            self.connection = sqlite.connect(self.keyword_db_path)
        except (OperationalError, sqlite.Error):
            LOGGER.exception('Failed to open keywords cache database.')
            raise

    def close_connection(self):
        """Close the active sqlite3 connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def get_cursor(self):
        """Get a cursor for the active connection.

        The cursor can be used to execute arbitrary queries against the
        database. This method also checks that the keywords table exists in
        the schema, and if not, it creates it.

        :returns: A valid cursor opened against the connection.
        :rtype: sqlite.

        :raises: An sqlite.Error will be raised if anything goes wrong.
        """
        if self.connection is None:
            try:
                self.open_connection()
            except OperationalError:
                raise
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT SQLITE_VERSION()')
            data = cursor.fetchone()
            LOGGER.debug("SQLite version: %s" % data)
            # Check if we have some tables, if not create them
            sql = 'select sql from sqlite_master where type = \'table\';'
            cursor.execute(sql)
            data = cursor.fetchone()
            LOGGER.debug("Tables: %s" % data)
            if data is None:
                LOGGER.debug('No tables found')
                sql = (
                    'create table keyword (hash varchar(32) primary key,'
                    'dict text);')
                LOGGER.debug(sql)
                cursor.execute(sql)
                #data = cursor.fetchone()
                cursor.fetchone()
            else:
                LOGGER.debug('Keywords table already exists')

            return cursor
        except sqlite.Error, e:
            LOGGER.debug("Error %s:" % e.args[0])
            raise

    def are_keywords_file_based(self, layer):
        """Check if keywords should be read/written to file or our keywords db.

        Determine which keyword lookup system to use (file base or cache db)
        based on the layer's provider type. True indicates we should use the
        datasource as a file and look for a keywords file, False and we look
        in the keywords db.

        :param layer: The layer which want to know how the keywords are stored.
        :type layer: QgsMapLayer

        :returns: True if keywords are stored in a file next to the dataset,
            else False if the dataset is remove e.g. a database.
        :rtype: bool

        :raises: UnsupportedProviderError
        """

        try:
            provider_type = str(layer.providerType())
        except AttributeError:
            raise UnsupportedProviderError(
                'Could not determine type for provider: %s' %
                layer.__class__.__name__)

        provider_dict = {
            'ogr': True,
            'gdal': True,
            'gpx': False,
            'wms': False,
            'spatialite': False,
            'delimitedtext': True,
            'postgres': False}
        file_based_keywords = False
        if provider_type in provider_dict:
            file_based_keywords = provider_dict[provider_type]
        return file_based_keywords

    def hash_for_datasource(self, data_source):
        """Given a data_source, return its hash.

        :param data_source: The data_source name from a layer.
        :type data_source: str

        :returns: An md5 hash for the data source name.
        :rtype: str
        """
        import hashlib
        hash_value = hashlib.md5()
        hash_value.update(data_source)
        hash_value = hash_value.hexdigest()
        return hash_value

    def delete_keywords_for_uri(self, uri):
        """Delete keywords for a URI in the keywords database.

        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the keywords. If there is an existing
        record for the hash, the entire record will be erased.

        .. seealso:: write_keywords_for_uri, read_keywords_for_uri

        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
            port=5432 user=\'foo\'password=\'bar\' sslmode=disable key=\'id\'
            srid=4326```

        :type uri: str
        """
        hash_value = self.hash_for_datasource(uri)
        try:
            cursor = self.get_cursor()
            # now see if we have any data for our hash
            sql = 'delete from keyword where hash = \'' + hash_value + '\';'
            cursor.execute(sql)
            self.connection.commit()
        except sqlite.Error, e:
            LOGGER.debug("SQLITE Error %s:" % e.args[0])
            self.connection.rollback()
        except Exception, e:
            LOGGER.debug("Error %s:" % e.args[0])
            self.connection.rollback()
            raise
        finally:
            self.close_connection()

    def write_keywords_for_uri(self, uri, keywords):
        """Write keywords for a URI into the keywords database. All the
        keywords for the uri should be written in a single operation.
        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLite database for the keywords. If there is an existing
        record it will be updated, if not, a new one will be created.

        .. seealso:: read_keyword_from_uri, delete_keywords_for_uri

        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
            port=5432 user=\'foo\' password=\'bar\' sslmode=disable
            key=\'id\' srid=4326```
        :type uri: str

        :param keywords: The metadata keywords to write (which should be
            provided as a dict of key value pairs).
        :type keywords: dict

        :returns: The retrieved value for the keyword if the keyword argument
            is specified, otherwise the complete keywords dictionary is
            returned.

        :raises: KeywordNotFoundError if the keyword is not recognised.
        """
        hash_value = self.hash_for_datasource(uri)
        try:
            cursor = self.get_cursor()
            # now see if we have any data for our hash
            sql = (
                'select dict from keyword where hash = \'%s\';' % hash_value)
            cursor.execute(sql)
            data = cursor.fetchone()
            pickle_dump = pickle.dumps(keywords, pickle.HIGHEST_PROTOCOL)
            if data is None:
                # insert a new rec
                #cursor.execute('insert into keyword(hash) values(:hash);',
                #             {'hash': hash_value})
                cursor.execute(
                    'insert into keyword(hash, dict) values(:hash, :dict);',
                    {'hash': hash_value, 'dict': sqlite.Binary(pickle_dump)})
                self.connection.commit()
            else:
                # update existing rec
                cursor.execute(
                    'update keyword set dict=? where hash = ?;',
                    (sqlite.Binary(pickle_dump), hash_value))
                self.connection.commit()
        except sqlite.Error:
            LOGGER.exception('Error writing keywords to SQLite db %s' %
                             self.keyword_db_path)
            # See if we can roll back.
            if self.connection is not None:
                self.connection.rollback()
            raise
        finally:
            self.close_connection()

    def read_keyword_from_uri(self, uri, keyword=None):
        """Get metadata from the keywords file associated with a URI.

        This is used for layers that are non local layer (e.g. postgresql
        connection) and so we need to retrieve the keywords from the sqlite
        keywords db.

        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the keywords. If there is an existing
        record it will be returned, if not and error will be thrown.

        .. seealso:: write_keywords_for_uri, delete_keywords_for_uri

        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
            port=5432 user=\'foo\' password=\'bar\' sslmode=disable
            key=\'id\' srid=4326```
        :type uri: str

        :param keyword: The metadata keyword to retrieve. If none,
            all keywords are returned.
        :type keyword: str

        :returns: A string containing the retrieved value for the keyword if
           the keyword argument is specified, otherwise the
           complete keywords dictionary is returned.

        :raises: KeywordNotFoundError if the keyword is not found.
        """
        hash_value = self.hash_for_datasource(uri)
        try:
            self.open_connection()
        except OperationalError:
            raise
        try:
            cursor = self.get_cursor()
            # now see if we have any data for our hash
            sql = (
                'select dict from keyword where hash = \'%s\';' % hash_value)
            cursor.execute(sql)
            data = cursor.fetchone()
            # unpickle it to get our dict back
            if data is None:
                raise HashNotFoundError('No hash found for %s' % hash_value)
            data = data[0]  # first field
            picked_dict = pickle.loads(str(data))
            if keyword is None:
                return picked_dict
            if keyword in picked_dict:
                return picked_dict[keyword]
            else:
                raise KeywordNotFoundError('Keyword "%s" not found in %s' % (
                    keyword, picked_dict))

        except sqlite.Error, e:
            LOGGER.debug("Error %s:" % e.args[0])
        except Exception, e:
            LOGGER.debug("Error %s:" % e.args[0])
            raise
        finally:
            self.close_connection()

    def get_statistics(self, layer):
        """Get the statistics related keywords from a layer.

        :param layer: A QGIS layer that represents an impact.
        :type layer: QgsMapLayer

        :returns: A two-tuple containing the values for the keywords
            'statistics_type' and 'statistics_classes'.
        :rtype: tuple(str, str)

        """
        # find needed statistics type
        try:
            statistics_type = self.read_keywords(
                layer, 'statistics_type')
            statistics_classes = self.read_keywords(
                layer, 'statistics_classes')

        except KeywordNotFoundError:
            # default to summing
            statistics_type = 'sum'
            statistics_classes = {}

        return statistics_type, statistics_classes
