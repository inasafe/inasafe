# coding=utf-8
"""Metadata DB IO implementation."""
from builtins import str

import logging
import os
import sqlite3 as sqlite
from sqlite3 import OperationalError

# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QObject

from safe.common.exceptions import (
    HashNotFoundError, UnsupportedProviderError)
from safe.definitions.default_settings import inasafe_default_settings
from safe.utilities.settings import setting

__copyright__ = "Copyright 2015, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class MetadataDbIO(QObject):

    """Class for doing metadata read/write operations on the local DB

    The local sqlite db is used for supporting metadata for remote
    datasources.

    .. versionadded:: 3.2
    """

    def __init__(self):
        """Constructor for the metadataDbIO object."""
        QObject.__init__(self)
        # path to sqlite db path
        self.metadata_db_path = None
        self.setup_metadata_db_path()
        self.connection = None

    def set_metadata_db_path(self, path):
        """Set the path for the metadata database (sqlite).

        The file will be used to search for metadata for non local datasets.

        :param path: A valid path to a sqlite database. The database does
            not need to exist already, but the user should be able to write
            to the path provided.
        :type path: str
        """
        self.metadata_db_path = str(path)

# methods below here should be considered private

    @staticmethod
    def default_metadata_db_path():
        """Helper to get the default path for the metadata file.

        :returns: The path to where the default location of the metadata
            database is. It get from the default setting
        :rtype: str
        """
        return inasafe_default_settings['keywordCachePath']

    def setup_metadata_db_path(self):
        """Helper to set the active path for the metadata.

        Called at init time, you can override this path by calling
        set_metadata_db_path.setmetadataDbPath.

        :returns: The path to where the metadata file is. If the user has
            never specified what this path is, the defaultmetadataDbPath is
            returned.
        :rtype: str
        """
        self.metadata_db_path = str(
            setting('keywordCachePath', expected_type=str))

    def open_connection(self):
        """Open an sqlite connection to the metadata database.

        By default the metadata database will be used in the plugin dir,
        unless an explicit path has been set using setmetadataDbPath, or
        overridden in QSettings. If the db does not exist it will
        be created.

        :raises: An sqlite.Error is raised if anything goes wrong
        """
        self.connection = None
        base_directory = os.path.dirname(self.metadata_db_path)
        if not os.path.exists(base_directory):
            try:
                os.mkdir(base_directory)
            except IOError:
                LOGGER.exception(
                    'Could not create directory for metadata cache.')
                raise

        try:
            self.connection = sqlite.connect(self.metadata_db_path)
        except (OperationalError, sqlite.Error):
            LOGGER.exception('Failed to open metadata cache database.')
            raise

    def close_connection(self):
        """Close the active sqlite3 connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def get_cursor(self):
        """Get a cursor for the active connection.

        The cursor can be used to execute arbitrary queries against the
        database. This method also checks that the metadata table exists in
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
                    'create table metadata (hash varchar(32) primary key,'
                    'json text, xml text);')
                LOGGER.debug(sql)
                cursor.execute(sql)
                # data = cursor.fetchone()
                cursor.fetchone()
            else:
                LOGGER.debug('metadata table already exists')

            return cursor
        except sqlite.Error as e:
            LOGGER.debug("Error %s:" % e.args[0])
            raise

    @staticmethod
    def are_metadata_file_based(layer):
        """Check if metadata should be read/written to file or our metadata db.

        Determine which metadata lookup system to use (file base or cache db)
        based on the layer's provider type. True indicates we should use the
        datasource as a file and look for a metadata file, False and we look
        in the metadata db.

        :param layer: The layer which want to know how the metadata are stored.
        :type layer: QgsMapLayer

        :returns: True if metadata are stored in a file next to the dataset,
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
            'delimitedtext': False,
            'postgres': False}
        file_based_metadata = False
        if provider_type in provider_dict:
            file_based_metadata = provider_dict[provider_type]
        return file_based_metadata

    @staticmethod
    def hash_for_datasource(data_source):
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

    def delete_metadata_for_uri(self, uri):
        """Delete metadata for a URI in the metadata database.

        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the metadata. If there is an existing
        record for the hash, the entire record will be erased.

        .. seealso:: write_metadata_for_uri, read_metadata_for_uri

        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
            port=5432 user=\'foo\'password=\'bar\' sslmode=disable key=\'id\'
            srid=4326```

        :type uri: str
        """
        hash_value = self.hash_for_datasource(uri)
        try:
            cursor = self.get_cursor()
            # now see if we have any data for our hash
            sql = 'delete from metadata where hash = \'' + hash_value + '\';'
            cursor.execute(sql)
            self.connection.commit()
        except sqlite.Error as e:
            LOGGER.debug("SQLITE Error %s:" % e.args[0])
            self.connection.rollback()
        except Exception as e:
            LOGGER.debug("Error %s:" % e.args[0])
            self.connection.rollback()
            raise
        finally:
            self.close_connection()

    def write_metadata_for_uri(self, uri, json=None, xml=None):
        """Write metadata for a URI into the metadata database. All the
        metadata for the uri should be written in a single operation.
        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLite database for the metadata. If there is an existing
        record it will be updated, if not, a new one will be created.

        .. seealso:: read_metadata_from_uri, delete_metadata_for_uri

        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
            port=5432 user=\'foo\' password=\'bar\' sslmode=disable
            key=\'id\' srid=4326```
        :type uri: str

        :param json: The metadata to write (which should be provided as a
        JSON str).
        :type json: str

        :param xml: The metadata to write (which should be provided as a
        XML str).
        :type xml: str

        """
        hash_value = self.hash_for_datasource(uri)
        try:
            cursor = self.get_cursor()
            # now see if we have any data for our hash
            sql = (
                'select json, xml from metadata where hash = \'%s\';' %
                hash_value)
            cursor.execute(sql)
            data = cursor.fetchone()
            if data is None:
                # insert a new rec
                # cursor.execute('insert into metadata(hash) values(:hash);',
                #             {'hash': hash_value})
                cursor.execute(
                    'insert into metadata(hash, json, xml ) '
                    'values(:hash, :json, :xml);',
                    {'hash': hash_value, 'json': json, 'xml': xml})
                self.connection.commit()
            else:
                # update existing rec
                cursor.execute(
                    'update metadata set json=?, xml=? where hash = ?;',
                    (json, xml, hash_value))
                self.connection.commit()
        except sqlite.Error:
            LOGGER.exception('Error writing metadata to SQLite db %s' %
                             self.metadata_db_path)
            # See if we can roll back.
            if self.connection is not None:
                self.connection.rollback()
            raise
        finally:
            self.close_connection()

    def read_metadata_from_uri(self, uri, metadata_format):
        """Try to get metadata from the DB entry associated with a URI.

        This is used for layers that are non local layer (e.g. postgresql
        connection) and so we need to retrieve the metadata from the sqlite
        metadata db.

        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the metadata. If there is an existing
        record it will be returned, if not and error will be thrown.

        .. seealso:: write_metadata_for_uri, delete_metadata_for_uri

        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
            port=5432 user=\'foo\' password=\'bar\' sslmode=disable
            key=\'id\' srid=4326```
        :type uri: str

        :param metadata_format: The format of the metadata to retrieve.
            Valid types are: 'json', 'xml'
        :type metadata_format: str

        :returns: A string containing the retrieved metadata

        :raises: metadataNotFoundError if the metadata is not found.
        """

        allowed_formats = ['json', 'xml']
        if metadata_format not in allowed_formats:
            message = 'Metadata format %s is not valid. Valid types: %s' % (
                metadata_format, allowed_formats)
            raise RuntimeError('%s' % message)

        hash_value = self.hash_for_datasource(uri)
        try:
            self.open_connection()
        except OperationalError:
            raise
        try:
            cursor = self.get_cursor()
            # now see if we have any data for our hash
            sql = (
                'select %s from metadata where hash = \'%s\';' % (
                    metadata_format, hash_value))
            cursor.execute(sql)
            data = cursor.fetchone()
            if data is None:
                raise HashNotFoundError('No hash found for %s' % hash_value)
            data = data[0]  # first field

            # get the ISO out of the DB
            metadata = str(data)
            return metadata

        except sqlite.Error as e:
            LOGGER.debug("Error %s:" % e.args[0])
        except Exception as e:
            LOGGER.debug("Error %s:" % e.args[0])
            raise
        finally:
            self.close_connection()
