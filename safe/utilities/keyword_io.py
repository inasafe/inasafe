# coding=utf-8
"""**Keyword IO implementation.**

.. tip:: Provides functionality for reading and writing keywords from within
   QGIS. It is an abstraction for the keywords system used by the underlying
   library.

"""
__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import json
import os
from os.path import expanduser
from xml.etree import ElementTree
from urlparse import urlparse
import logging
import sqlite3 as sqlite
from sqlite3 import OperationalError
from cPickle import loads, dumps, HIGHEST_PROTOCOL
from ast import literal_eval

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsDataSourceURI
# noinspection PyPackageRequirements
from PyQt4.QtCore import QObject, QSettings
from safe.utilities.utilities import (
    read_file_keywords,
    write_keywords_to_file)
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.unicode import get_string
from safe.common.exceptions import (
    HashNotFoundError,
    KeywordNotFoundError,
    KeywordDbError,
    InvalidParameterError,
    NoKeywordsFoundError,
    UnsupportedProviderError)
from safe.storage.metadata_utilities import (
    generate_iso_metadata,
    ISO_METADATA_KEYWORD_TAG)
from safe.common.utilities import verify
import safe.definitions
from safe.definitions import (
    inasafe_keyword_version, inasafe_keyword_version_key)


LOGGER = logging.getLogger('InaSAFE')


class KeywordIO(QObject):
    """Class for doing keyword read/write operations.

    It abstracts away differences between using SAFE to get keywords from a
    .keywords file and this plugins implementation of keyword caching in a
    local sqlite db used for supporting keywords for remote datasources."""

    def __init__(self, layer=None):
        """Constructor for the KeywordIO object.

        .. versionchanged:: 3.3 added optional layer parameter.

        """
        QObject.__init__(self)
        # path to sqlite db path
        self.keyword_db_path = None
        self.setup_keyword_db_path()
        self.connection = None
        self.layer = layer

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
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer,
            QgsPluginLayer

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
        source = layer.source()
        try:
            flag = self.are_keywords_file_based(layer)
        except UnsupportedProviderError:
            raise

        try:
            if flag:
                keywords = read_file_keywords(source, keyword)
            else:
                uri = self.normalize_uri(layer)
                keywords = self.read_keyword_from_uri(uri, keyword)
            return keywords
        except (HashNotFoundError,
                Exception,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError) as e:
            raise e

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

        source = layer.source()
        try:
            keywords[inasafe_keyword_version_key] = inasafe_keyword_version
            if flag:
                write_keywords_to_file(source, keywords)
            else:
                uri = self.normalize_uri(layer)
                self.write_keywords_for_uri(uri, keywords)
            return
        except:
            raise

    def update_keywords(self, layer, keywords):
        """Update keywords for a datasource.

        :param layer: A QGIS QgsMapLayer instance.
        :type layer: qgis.core.QgsMapLayer

        :param keywords: A dict containing all the keywords to be updated
              for the layer.
        :type keywords: dict
        """
        try:
            existing_keywords = self.read_keywords(layer)
        except (
            HashNotFoundError,
            OperationalError,
            InvalidParameterError,
            KeywordNotFoundError):

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
            'Expected extra keywords to be a dictionary. Got '
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
                # data = cursor.fetchone()
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
            'delimitedtext': False,
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

    def normalize_uri(self, layer):
        """Normalize URI from layer source. URI can be in a form
        of QgsDataSourceURI which is related to RDBMS source or
        general URI like CSV URI

        :param layer : A layer
        :type layer : QgsMapLayer

        :return: normalized URI to be hashed
        :raise: AttributeError if providerType not recognized
        """
        # there are different method to extract unique uri based on
        # layer type
        try:
            provider_type = str(layer.providerType())
        except AttributeError:
            raise UnsupportedProviderError(
                'Could not determine type for provider: %s' %
                layer.__class__.__name__)
        source = layer.source()
        if provider_type == 'postgres':
            # Use QgsDataSourceURI to parse RDBMS datasource
            # create unique uri based on host, schema, and tablename
            datasource_uri = QgsDataSourceURI(source)
            normalized_uri = ':'.join([
                datasource_uri.host(),
                datasource_uri.schema(),
                datasource_uri.table()])
        elif provider_type == 'delimitedtext':
            # Use urlparse to parse delimitedtext uri
            # create unique uri based on protocol, host, and path
            general_uri = urlparse(source)
            normalized_uri = ':'.join([
                general_uri.scheme,
                general_uri.netloc,
                general_uri.path])
        else:
            normalized_uri = source
        return normalized_uri

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

        :returns: The XML written to the DB

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
            metadata_xml = generate_iso_metadata(keywords)
            pickle_dump = dumps(metadata_xml, HIGHEST_PROTOCOL)
            if data is None:
                # insert a new rec
                # cursor.execute('insert into keyword(hash) values(:hash);',
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

        return metadata_xml

    def read_keyword_from_uri(self, uri, keyword=None):
        """Get metadata from the keywords file associated with a URI.

        This is used for layers that are non local layer (e.g. postgresql
        connection) and so we need to retrieve the keywords from the sqlite
        keywords db.

        A hash will be constructed from the supplied uri and a lookup made
        in a local SQLITE database for the keywords. If there is an existing
        record it will be returned, if not and error will be thrown.

        If the record is a dictionary, it means that it was inserted into the
        DB in a pre 2.2 version which had no ISO metadata. In this case, we use
        that dictionary to update the entry to the new ISO based metadata

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

            # get the ISO XML out of the DB
            metadata = loads(str(data))

            # the uri already had a KW entry in the DB using the old KW system
            # we use that dictionary to update the entry to the new ISO based
            # metadata system
            if isinstance(metadata, dict):
                metadata = self.write_keywords_for_uri(uri, metadata)

            root = ElementTree.fromstring(metadata)
            keyword_element = root.find(ISO_METADATA_KEYWORD_TAG)
            dict_str = keyword_element.text
            picked_dict = json.loads(dict_str)

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

    @staticmethod
    def definition(keyword):
        """Given a keyword, try to get a definition dict for it.

        .. versionadded:: 3.2

        Definition dicts are defined in keywords.py. We try to return
        one if present, otherwise we return none. Using this method you
        can present rich metadata to the user e.g.

        keyword = 'layer_purpose'
        kio = safe.utilities.keyword_io.Keyword_IO()
        definition = kio.definition(keyword)
        print definition

        :param keyword: A keyword key.
        :type keyword: str

        :returns: A dictionary containing the matched key definition
            from definitions.py, otherwise None if no match was found.
        :rtype: dict, None
        """
        for item in dir(safe.definitions):
            if not item.startswith("__"):
                var = getattr(safe.definitions, item)
                if isinstance(var, dict):
                    if var.get('key') == keyword:
                        return var
        return None

    def to_message(self, keywords=None, show_header=True):
        """Format keywords as a message object.

        .. versionadded:: 3.2

        .. versionchanged:: 3.3 - default keywords to None

        The message object can then be rendered to html, plain text etc.

        :param keywords: Keywords to be converted to a message. Optional. If
            not passed then we will attempt to get keywords from self.layer
            if it is not None.
        :type keywords: dict

        :param show_header: Flag indicating if InaSAFE logo etc. should be
            added above the keywords table. Default is True.
        :type show_header: bool

        :returns: A safe message object containing a table.
        :rtype: safe.messaging.message
        """
        if keywords is None and self.layer is not None:
            keywords = self.read_keywords(self.layer)
        # This order was determined in issue #2313
        preferred_order = [
            'title',
            'layer_purpose',
            'exposure',
            'hazard',
            'hazard_category',
            'layer_geometry',
            'layer_mode',
            'vector_hazard_classification',
            'exposure_unit',
            'continuous_hazard_unit',
            'volcano_name_field',
            'road_class_field',
            'structure_class_field',
            'field',
            'value_map',  # attribute values
            'resample',
            'source',
            'url',
            'scale',
            'license',
            'date',
            'keyword_version'
        ]  # everything else in arbitrary order
        report = m.Message()
        if show_header:
            logo_element = m.Brand()
            report.add(logo_element)
            report.add(m.Heading(self.tr(
                'Layer keywords:'), **styles.INFO_STYLE))
            report.add(m.Text(self.tr(
                'The following keywords are defined for the active layer:')))

        table = m.Table(style_class='table table-condensed table-striped')
        # First render out the preferred order keywords
        for keyword in preferred_order:
            if keyword in keywords:
                value = keywords[keyword]
                row = self._keyword_to_row(keyword, value)
                keywords.pop(keyword)
                table.add(row)

        # now render out any remaining keywords in arbitrary order
        for keyword in keywords:
            value = keywords[keyword]
            row = self._keyword_to_row(keyword, value)
            table.add(row)

        # If the keywords class was instantiated with a layer object
        # we can add some context info not stored in the keywords themselves
        # but that is still useful to see...
        if self.layer:
            # First the CRS
            keyword = self.tr('Reference system')
            value = self.layer.crs().authid()
            row = self._keyword_to_row(keyword, value)
            table.add(row)
            # Next the data source
            keyword = self.tr('Layer source')
            value = self.layer.source()
            row = self._keyword_to_row(keyword, value, wrap_slash=True)
            table.add(row)

        # Finalise the report
        report.add(table)
        return report

    def _keyword_to_row(self, keyword, value, wrap_slash=False):
        """Helper to make a message row from a keyword.

        .. versionadded:: 3.2

        Use this when constructing a table from keywords to display as
        part of a message object.

        :param keyword: The keyword to be rendered.
        :type keyword: str

        :param value: Value of the keyword to be rendered.
        :type value: basestring

        :param wrap_slash: Whether to replace slashes with the slash plus the
            html <wbr> tag which will help to e.g. wrap html in small cells if
            it contains a long filename. Disabled by default as it may cause
            side effects if the text contains html markup.
        :type wrap_slash: bool

        :returns: A row to be added to a messaging table.
        :rtype: safe.messaging.items.row.Row
        """
        row = m.Row()
        # Translate titles explicitly if possible
        if keyword == 'title':
            value = self.tr(value)
        # we want to show the user the concept name rather than its key
        # if possible. TS
        definition = self.definition(keyword)
        if definition is None:
            definition = self.tr(keyword.capitalize().replace('_', ' '))
        else:
            definition = definition['name']

        # We deal with some special cases first:

        # In this case the value contains a DICT that we want to present nicely
        if keyword == 'value_map':
            value = self._dict_to_row(value)
        # In these KEYWORD cases we show the DESCRIPTION for
        # the VALUE definition
        elif keyword in [
                'vector_hazard_classification',
                'raster_hazard_classification']:
            # get the definition for this class from definitions.py
            value = self.definition(value)
            value = value['description']
        # In these VALUE cases we show the DESCRIPTION for
        # the VALUE definition
        elif value in []:
            # get the definition for this class from definitions.py
            value = self.definition(value)
            value = value['description']
        # In these VALUE cases we show the NAME for the VALUE definition
        elif value in [
                'multiple_event',
                'single_event',
                'point',
                'line',
                'polygon'
                'field']:
            # get the name for this class from definitions.py
            value = self.definition(value)
            value = value['name']
        # otherwise just treat the keyword as literal text
        else:
            # Otherwise just directly read the value
            value = get_string(value)

        key = m.ImportantText(definition)
        row.add(m.Cell(key))
        row.add(m.Cell(value, wrap_slash=wrap_slash))
        return row

    def _dict_to_row(self, keyword_value):
        """Helper to make a message row from a keyword where value is a dict.

        .. versionadded:: 3.2

        Use this when constructing a table from keywords to display as
        part of a message object. This variant will unpack the dict and
        present it nicely in the keyword value area as a nested table in the
        cell.

        We are expecting keyword value would be something like this:

            "{'high': ['Kawasan Rawan Bencana III'], "
            "'medium': ['Kawasan Rawan Bencana II'], "
            "'low': ['Kawasan Rawan Bencana I']}"

        Or by passing a python dict object with similar layout to above.

        i.e. A string representation of a dict where the values are lists.

        :param keyword_value: Value of the keyword to be rendered. This must
            be a string representation of a dict, or a dict.
        :type keyword_value: basestring, dict

        :returns: A table to be added into a cell in the keywords table.
        :rtype: safe.messaging.items.table
        """
        LOGGER.info('Converting to dict: %s' % keyword_value)
        if isinstance(keyword_value, basestring):
            keyword_value = literal_eval(keyword_value)
        table = m.Table(style_class='table table-condensed')
        for key, value_list in keyword_value.iteritems():
            row = m.Row()
            # Firs the heading
            key = m.ImportantText(key)
            row.add(m.Cell(key))
            # Then the value. If it contains more than one element we
            # present it as a bullet list, otherwise just as simple text
            if len(value_list) > 1:
                bullets = m.BulletedList()
                for item in value_list:
                    bullets.add(item)
                row.add(m.Cell(bullets))
            else:
                row.add(m.Cell(value_list[0]))
            table.add(row)
        return table
