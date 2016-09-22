# coding=utf-8
"""**Keyword IO implementation.**

.. tip:: Provides functionality for reading and writing keywords from within
   QGIS. It is an abstraction for the keywords system used by the underlying
   library.

"""

import logging
import os
from ast import literal_eval
from datetime import datetime
from os.path import expanduser
from sqlite3 import OperationalError

import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QObject, QSettings
from PyQt4.QtCore import QUrl, QDateTime

import safe.definitionsv4.definitions_v3
from safe import messaging as m
from safe.common.exceptions import (
    HashNotFoundError,
    KeywordNotFoundError,
    KeywordDbError,
    InvalidParameterError,
    NoKeywordsFoundError,
    MetadataReadError
)
from safe.common.utilities import verify
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.metadata import (
    write_iso19115_metadata,
    read_iso19115_metadata,
)
from safe.utilities.unicode import get_string

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

LOGGER = logging.getLogger('InaSAFE')


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
        from definitions_v3.py, otherwise None if no match was found.
    :rtype: dict, None
    """
    for item in dir(safe.definitionsv4.definitions_v3):
        if not item.startswith("__"):
            var = getattr(safe.definitionsv4.definitions_v3, item)
            if isinstance(var, dict):
                if var.get('key') == keyword:
                    return var
    return None


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

    # TODO(IS) can be removed
    @classmethod
    def read_keywords_file(cls, filename, keyword=None):
        """Read keywords from a keywords file and return as dictionary

        This serves as a wrapper function that should be provided by Keyword
        IO. Use this if you are sure that the filename is a keyword file.

        :param filename: The filename of the keyword, typically with .xml or
            .keywords extension. If not, will raise exceptions
        :type filename: str

        :param keyword: If set, will extract only the specified keyword
              from the keywords dict.
        :type keyword: str

        :returns: A dict if keyword is omitted, otherwise the value for the
            given key if it is present.
        :rtype: dict, str

        :raises: KeywordNotFoundError, InvalidParameterError
        """

        # Try to read from ISO metadata first.
        _, ext = os.path.splitext(filename)

        dictionary = {}
        if ext == '.xml':
            try:
                dictionary = read_iso19115_metadata(filename)
            except (MetadataReadError, NoKeywordsFoundError):
                pass
        else:
            raise InvalidParameterError(
                'Keywords file have .xml or extension')

        # if no keyword was supplied, just return the dict
        if keyword is None:
            return dictionary
        if keyword not in dictionary:
            message = tr('No value was found in file %s for keyword %s' % (
                filename, keyword))
            raise KeywordNotFoundError(message)

        return dictionary[keyword]

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

        # Try to read from ISO metadata first.
        return read_iso19115_metadata(source, keyword)

    def write_keywords(self, layer, keywords):
        """Write keywords for a datasource.

        This is a wrapper method that will 'do the right thing' to store
        keywords for the given datasource. In particular, if the datasource
        is remote (e.g. a database connection) it will write the keywords from
        the keywords store.

        :param layer: A QGIS QgsMapLayer instance.
        :type layer: qgis.core.QgsMapLayer

        :param keywords: A dict containing all the keywords to be written
              for the layer.
        :type keywords: dict

        :raises: UnsupportedProviderError
        """
        source = layer.source()
        write_iso19115_metadata(source, keywords)

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
        :type source_layer: qgis.core.QgsMapLayer

        :param destination_file: The output filename that should be used
            to store the keywords in. It's a path to a layer file.
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
        new_destination = destination_base + '.xml'
        # write the extra keywords into the source dict
        try:
            for key in extra_keywords:
                keywords[key] = extra_keywords[key]
            write_iso19115_metadata(destination_file, keywords)
            # write_keywords_to_file(new_destination, keywords)
        except Exception, e:
            message = self.tr(
                'Failed to copy keywords file from : \n%s\nto\n%s: %s' % (
                    source_layer.source(), new_destination, str(e)))
            raise Exception(message)
        return

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
            'population_field',
            'name_field',
            'structure_class_field',
            'field',
            'value_map',  # attribute values
            'value_mapping',  # attribute values
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
        # # See #2569
        if keyword == 'url':
            if isinstance(value, QUrl):
                value = value.toString()
        if keyword == 'date':
            if isinstance(value, QDateTime):
                value = value.toString('d MMM yyyy')
            elif isinstance(value, datetime):
                value = value.strftime('%d %b %Y')
        # we want to show the user the concept name rather than its key
        # if possible. TS
        keyword_definition = definition(keyword)
        if keyword_definition is None:
            keyword_definition = self.tr(keyword.capitalize().replace(
                '_', ' '))
        else:
            keyword_definition = keyword_definition['name']

        # We deal with some special cases first:

        # In this case the value contains a DICT that we want to present nicely
        if keyword in ['value_map',
                       'value_mapping']:
            value = self._dict_to_row(value)
        # In these KEYWORD cases we show the DESCRIPTION for
        # the VALUE keyword_definition
        elif keyword in [
                'vector_hazard_classification',
                'raster_hazard_classification']:
            # get the keyword_definition for this class from definitions_v3.py
            value = definition(value)
            value = value['description']
        # In these VALUE cases we show the DESCRIPTION for
        # the VALUE keyword_definition
        elif value in []:
            # get the keyword_definition for this class from definitions_v3.py
            value = definition(value)
            value = value['description']
        # In these VALUE cases we show the NAME for the VALUE
        # keyword_definition
        elif value in [
                'multiple_event',
                'single_event',
                'point',
                'line',
                'polygon'
                'field']:
            # get the name for this class from definitions_v3.py
            value = definition(value)
            value = value['name']
        # otherwise just treat the keyword as literal text
        else:
            # Otherwise just directly read the value
            value = get_string(value)

        key = m.ImportantText(keyword_definition)
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
        # LOGGER.info('Converting to dict: %s' % keyword_value)
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
