# coding=utf-8
"""Keyword IO implementation."""


import logging
from ast import literal_eval
from datetime import datetime

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtCore import QUrl, QDateTime
from qgis.core import QgsMapLayer

from safe import messaging as m
from safe.definitions.keyword_properties import property_extra_keywords
from safe.definitions.utilities import definition
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.metadata import (
    write_iso19115_metadata, read_iso19115_metadata)
from safe.utilities.str import get_string

__copyright__ = "Copyright 2011, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


# Notes(IS): This class can be replaced by safe.utilities.metadata
# Some methods for viewing the keywords should be put in the other class
class KeywordIO(QObject):

    """Class for doing keyword read/write operations.

    It abstracts away differences between using SAFE to get keywords from a
    .keywords file and this plugins implementation of keyword caching in a
    local sqlite db used for supporting keywords for remote datasources.
    """

    def __init__(self, layer=None):
        """Constructor for the KeywordIO object.

        .. versionchanged:: 3.3 added optional layer parameter.
        """
        QObject.__init__(self)
        self.layer = layer

    @staticmethod
    def read_keywords(layer, keyword=None):
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

    @staticmethod
    def write_keywords(layer, keywords):
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
        if not isinstance(layer, QgsMapLayer):
            raise Exception(
                tr('The layer is not a QgsMapLayer : {type}').format(
                    type=type(layer)))

        source = layer.source()
        write_iso19115_metadata(source, keywords)

    # methods below here should be considered private

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
        :rtype: safe.messaging.Message
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
            'classification',
            'exposure_unit',
            'continuous_hazard_unit',
            'value_map',  # attribute values
            'thresholds',  # attribute values
            'value_maps',  # attribute values
            'inasafe_fields',
            'inasafe_default_values',
            'resample',
            'source',
            'url',
            'scale',
            'license',
            'date',
            'extra_keywords',
            'keyword_version'
        ]  # everything else in arbitrary order
        report = m.Message()
        if show_header:
            logo_element = m.Brand()
            report.add(logo_element)
            report.add(m.Heading(tr(
                'Layer keywords:'), **styles.BLUE_LEVEL_4_STYLE))
            report.add(m.Text(tr(
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
            keyword = tr('Reference system')
            value = self.layer.crs().authid()
            row = self._keyword_to_row(keyword, value)
            table.add(row)
            # Next the data source
            keyword = tr('Layer source')
            value = self.layer.publicSource()  # Hide password
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
            value = tr(value)
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
            keyword_definition = tr(keyword.capitalize().replace(
                '_', ' '))
        else:
            try:
                keyword_definition = keyword_definition['name']
            except KeyError:
                # Handling if name is not exist.
                keyword_definition = keyword_definition['key'].capitalize()
                keyword_definition = keyword_definition.replace('_', ' ')

        # We deal with some special cases first:

        # In this case the value contains a DICT that we want to present nicely
        if keyword in [
                'value_map',
                'inasafe_fields',
                'inasafe_default_values']:
            value = self._dict_to_row(value)
        elif keyword == 'extra_keywords':
            value = self._dict_to_row(value, property_extra_keywords)
        elif keyword == 'value_maps':
            value = self._value_maps_row(value)
        elif keyword == 'thresholds':
            value = self._threshold_to_row(value)
        # In these KEYWORD cases we show the DESCRIPTION for
        # the VALUE keyword_definition
        elif keyword in ['classification']:
            # get the keyword_definition for this class from definitions
            value = definition(value)
            value = value['description']
        # In these VALUE cases we show the DESCRIPTION for
        # the VALUE keyword_definition
        elif value in []:
            # get the keyword_definition for this class from definitions
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
            # get the name for this class from definitions
            value = definition(value)
            value = value['name']
        # otherwise just treat the keyword as literal text
        else:
            # Otherwise just directly read the value
            pretty_value = None

            value_definition = definition(value)

            if value_definition:
                pretty_value = value_definition.get('name')

            if not pretty_value:
                pretty_value = get_string(value)
            value = pretty_value

        key = m.ImportantText(keyword_definition)
        row.add(m.Cell(key))
        row.add(m.Cell(value, wrap_slash=wrap_slash))
        return row

    @staticmethod
    def _threshold_to_row(thresholds_keyword):
        """Helper to make a message row from a threshold

        We are expecting something like this:

        {
            'thresholds': {
                'structure': {
                    'ina_structure_flood_hazard_classification': {
                        'classes': {
                            'low': [1, 2],
                            'medium': [3, 4],
                            'high': [5, 6]
                        },
                        'active': True
                    },
                    'ina_structure_flood_hazard_4_class_classification':
                    {
                        'classes': {
                            'low': [1, 2],
                            'medium': [3, 4],
                            'high': [5, 6],
                            'very_high': [7, 8]
                        },
                        'active': False

                    }
                },
                'population': {
                    'ina_population_flood_hazard_classification': {
                        'classes': {
                            'low': [1, 2.5],
                            'medium': [2.5, 4.5],
                            'high': [4.5, 6]
                        },
                        'active': False
                    },
                    'ina_population_flood_hazard_4_class_classification':
                    {
                        'classes': {
                            'low': [1, 2.5],
                            'medium': [2.5, 4],
                            'high': [4, 6],
                            'very_high': [6, 8]
                        },
                        'active': True
                    }
                },
            },

        Each value is a list with exactly two element [a, b], where a <= b.

        :param thresholds_keyword: Value of the keyword to be rendered. This
            must be a string representation of a dict, or a dict.
        :type thresholds_keyword: basestring, dict

        :returns: A table to be added into a cell in the keywords table.
        :rtype: safe.messaging.items.table
        """
        if isinstance(thresholds_keyword, str):
            thresholds_keyword = literal_eval(thresholds_keyword)

        for k, v in list(thresholds_keyword.items()):
            # If the v is not dictionary, it should be the old value maps.
            # To handle thresholds in the Impact Function.
            if not isinstance(v, dict):
                table = m.Table(style_class='table table-condensed')

                for key, value in list(thresholds_keyword.items()):
                    row = m.Row()
                    name = definition(key)['name'] if definition(key) else key
                    row.add(m.Cell(m.ImportantText(name)))
                    pretty_value = tr('%s to %s' % (value[0], value[1]))
                    row.add(m.Cell(pretty_value))

                    table.add(row)
                return table

        table = m.Table(style_class='table table-condensed table-striped')

        i = 0
        for exposure_key, classifications in list(thresholds_keyword.items()):
            i += 1
            exposure = definition(exposure_key)
            exposure_row = m.Row()
            exposure_row.add(m.Cell(m.ImportantText(tr('Exposure'))))
            exposure_row.add(m.Cell(m.Text(exposure['name'])))
            exposure_row.add(m.Cell(''))
            table.add(exposure_row)

            active_classification = None
            classification_row = m.Row()
            classification_row.add(m.Cell(m.ImportantText(tr(
                'Classification'))))
            for classification, value in list(classifications.items()):
                if value.get('active'):
                    active_classification = definition(classification)
                    classification_row.add(
                        m.Cell(active_classification['name']))
                    classification_row.add(m.Cell(''))
                    break

            if not active_classification:
                classification_row.add(m.Cell(tr('No classifications set.')))
                classification_row.add(m.Cell(''))
                continue

            table.add(classification_row)

            header = m.Row()
            header.add(m.Cell(tr('Class name')))
            header.add(m.Cell(tr('Minimum')))
            header.add(m.Cell(tr('Maximum')))
            table.add(header)
            classes = active_classification.get('classes')
            # Sort by value, put the lowest first
            classes = sorted(classes, key=lambda the_key: the_key['value'])
            for the_class in classes:
                threshold = classifications[active_classification['key']][
                    'classes'][the_class['key']]
                row = m.Row()
                row.add(m.Cell(the_class['name']))
                row.add(m.Cell(threshold[0]))
                row.add(m.Cell(threshold[1]))
                table.add(row)

            if i < len(thresholds_keyword):
                # Empty row
                empty_row = m.Row()
                empty_row.add(m.Cell(''))
                empty_row.add(m.Cell(''))
                table.add(empty_row)

        return table

    @staticmethod
    def _dict_to_row(keyword_value, keyword_property=None):
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

        :param keyword_property: The definition of the keyword property.
        :type keyword_property: dict, None

        :returns: A table to be added into a cell in the keywords table.
        :rtype: safe.messaging.items.table
        """
        if isinstance(keyword_value, str):
            keyword_value = literal_eval(keyword_value)
        table = m.Table(style_class='table table-condensed')
        # Sorting the key
        for key in sorted(keyword_value.keys()):
            value = keyword_value[key]
            row = m.Row()
            # First the heading
            if keyword_property is None:
                if definition(key):
                    name = definition(key)['name']
                else:
                    name = tr(key.replace('_', ' ').capitalize())
            else:
                default_name = tr(key.replace('_', ' ').capitalize())
                name = keyword_property.get('member_names', {}).get(
                    key, default_name)

            row.add(m.Cell(m.ImportantText(name)))
            # Then the value. If it contains more than one element we
            # present it as a bullet list, otherwise just as simple text
            if isinstance(value, (tuple, list, dict, set)):
                if len(value) > 1:
                    bullets = m.BulletedList()
                    for item in value:
                        bullets.add(item)
                    row.add(m.Cell(bullets))
                elif len(value) == 0:
                    row.add(m.Cell(""))
                else:
                    row.add(m.Cell(value[0]))
            else:
                if keyword_property == property_extra_keywords:
                    key_definition = definition(key)
                    if key_definition and key_definition.get('options'):
                        value_definition = definition(value)
                        if value_definition:
                            value = value_definition.get('name', value)
                    elif key_definition and key_definition.get(
                            'type') == datetime:
                        try:
                            value = datetime.strptime(value, key_definition[
                                'store_format'])
                            value = value.strftime(
                                key_definition['show_format'])
                        except ValueError:
                            try:
                                value = datetime.strptime(
                                    value, key_definition['store_format2'])
                                value = value.strftime(
                                    key_definition['show_format'])
                            except ValueError:
                                pass
                row.add(m.Cell(value))

            table.add(row)
        return table

    @staticmethod
    def _value_maps_row(value_maps_keyword):
        """Helper to make a message row from a value maps.

        Expected keywords:
        'value_maps': {
            'structure': {
                'ina_structure_flood_hazard_classification': {
                    'classes': {
                        'low': [1, 2, 3],
                        'medium': [4],
                        'high': [5, 6]
                    },
                    'active': True
                },
                'ina_structure_flood_hazard_4_class_classification':
                {
                    'classes': {
                        'low': [1],
                        'medium': [2, 3, 4],
                        'high': [5, 6, 7],
                        'very_high': [8]
                    },
                    'active': False

                }
            },
            'population': {
                'ina_population_flood_hazard_classification': {
                    'classes': {
                        'low': [1],
                        'medium': [2, 3],
                        'high': [4, 5, 6]
                    },
                    'active': False
                },
                'ina_population_flood_hazard_4_class_classification':
                {
                    'classes': {
                        'low': [1, 2],
                        'medium': [3, 4],
                        'high': [4, 5, 6],
                        'very_high': [6, 7, 8]
                    },
                    'active': True
                }
            },
        }

        :param value_maps_keyword: Value of the keyword to be rendered. This
            must be a string representation of a dict, or a dict.
        :type value_maps_keyword: basestring, dict

        :returns: A table to be added into a cell in the keywords table.
        :rtype: safe.messaging.items.table
        """
        if isinstance(value_maps_keyword, str):
            value_maps_keyword = literal_eval(value_maps_keyword)

        table = m.Table(style_class='table table-condensed table-striped')

        i = 0
        for exposure_key, classifications in list(value_maps_keyword.items()):
            i += 1
            exposure = definition(exposure_key)
            exposure_row = m.Row()
            exposure_row.add(m.Cell(m.ImportantText(tr('Exposure'))))
            exposure_row.add(m.Cell(exposure['name']))
            table.add(exposure_row)

            classification_row = m.Row()
            classification_row.add(m.Cell(m.ImportantText(tr(
                'Classification'))))
            active_classification = None
            for classification, value in list(classifications.items()):
                if value.get('active'):
                    active_classification = definition(classification)
                    if active_classification.get('name'):
                        classification_row.add(
                            m.Cell(active_classification['name']))
                    break

            if not active_classification:
                classification_row.add(m.Cell(tr('No classifications set.')))
                continue
            table.add(classification_row)

            header = m.Row()
            header.add(m.Cell(tr('Class name')))
            header.add(m.Cell(tr('Values')))
            table.add(header)
            classes = active_classification.get('classes')
            # Sort by value, put the lowest first
            classes = sorted(classes, key=lambda k: k['value'])
            for the_class in classes:
                value_map = classifications[active_classification['key']][
                    'classes'].get(the_class['key'], [])
                row = m.Row()
                row.add(m.Cell(the_class['name']))
                row.add(m.Cell(', '.join([str(v) for v in value_map])))
                table.add(row)

            if i < len(value_maps_keyword):
                # Empty row
                empty_row = m.Row()
                empty_row.add(m.Cell(''))
                empty_row.add(m.Cell(''))
                table.add(empty_row)

        return table
