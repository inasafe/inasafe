# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilities implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import traceback
import logging
import webbrowser
import unicodedata
import codecs
from collections import OrderedDict

# noinspection PyPackageRequirements

from safe.storage.utilities import read_keywords
from safe.common.exceptions import (
    InvalidParameterError,
    NoKeywordsFoundError,
    KeywordNotFoundError)
from safe.common.utilities import unique_filename
from safe.common.version import get_version
from safe.defaults import disclaimer
from safe import messaging as m
from safe.messaging import styles, Message
from safe.messaging.error_message import ErrorMessage
from safe.utilities.unicode import get_unicode, get_string
from safe.utilities.i18n import tr
from safe.definitions import inasafe_keyword_version


INFO_STYLE = styles.INFO_STYLE

LOGGER = logging.getLogger('InaSAFE')


def get_error_message(exception, context=None, suggestion=None):
    """Convert exception into an ErrorMessage containing a stack trace.


    :param exception: Exception object.
    :type exception: Exception

    :param context: Optional context message.
    :type context: str

    :param suggestion: Optional suggestion.
    :type suggestion: str

    .. see also:: https://github.com/AIFDR/inasafe/issues/577

    :returns: An error message with stack trace info suitable for display.
    :rtype: ErrorMessage
    """

    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))

    problem = m.Message(m.Text(exception.__class__.__name__))

    if exception is None or exception == '':
        problem.append = m.Text(tr('No details provided'))
    else:
        if isinstance(exception.message, Message):
            problem.append = m.Text(str(exception.message.message))
        else:
            problem.append = m.Text(exception.message)

    suggestion = suggestion
    if suggestion is None and hasattr(exception, 'suggestion'):
        suggestion = exception.message

    error_message = ErrorMessage(
        problem,
        detail=context,
        suggestion=suggestion,
        traceback=trace
    )

    args = exception.args
    for arg in args:
        error_message.details.append(arg)

    return error_message


def humanise_seconds(seconds):
    """Utility function to humanise seconds value into e.g. 10 seconds ago.

    The function will try to make a nice phrase of the seconds count
    provided.

    .. note:: Currently seconds that amount to days are not supported.

    :param seconds: Mandatory seconds value e.g. 1100.
    :type seconds: int

    :returns: A humanised version of the seconds count.
    :rtype: str
    """
    days = seconds / (3600 * 24)
    day_modulus = seconds % (3600 * 24)
    hours = day_modulus / 3600
    hour_modulus = day_modulus % 3600
    minutes = hour_modulus / 60

    if seconds < 60:
        return tr('%i seconds' % seconds)
    if seconds < 120:
        return tr('a minute')
    if seconds < 3600:
        return tr('%s minutes' % minutes)
    if seconds < 7200:
        return tr('over an hour')
    if seconds < 86400:
        return tr('%i hours and %i minutes' % (hours, minutes))
    else:
        # If all else fails...
        return tr('%i days, %i hours and %i minutes' % (
            days, hours, minutes))


def reorder_dictionary(unordered_dictionary, expected_key_order):
    """Reorder a dictionary according to a list of keys.

    .. versionadded: 3.4

    :param unordered_dictionary: The dictionary to reorder.
    :type unordered_dictionary: dict

    :param expected_key_order: The list of keys.
    :type expected_key_order: list

    :return: The new ordered dictionary.
    :type: OrderedDict
    """

    ordered_dictionary = OrderedDict()

    for item in expected_key_order:
        if item in unordered_dictionary:
            ordered_dictionary[item] = unordered_dictionary[item]

    return ordered_dictionary


def main_type(feature_type, value_mapping):
    """Return the the main class from a feature by reading the mapping.

    This function is used by buildings/roads IF.

    .. versionadded: 3.4

    :param feature_type: The type of the feature to test.
    :type feature_type: str

    :param value_mapping: The value mapping.
    :type value_mapping: dict

    :return: The main class name, if not found, it will return 'other'.
    :rtype: str
    """
    other = 'other'

    if feature_type in [None, 'NULL', 'null', 'Null', 0]:
        return other

    if feature_type.__class__.__name__ == 'QPyNullVariant':
        return other

    for key, values in value_mapping.iteritems():
        if feature_type in values:
            feature_class = key
            break
    else:
        feature_class = other

    return feature_class


def impact_attribution(keywords, inasafe_flag=False):
    """Make a little table for attribution of data sources used in impact.

    :param keywords: A keywords dict for an impact layer.
    :type keywords: dict

    :param inasafe_flag: bool - whether to show a little InaSAFE promotional
        text in the attribution output. Defaults to False.

    :returns: An html snippet containing attribution information for the impact
        layer. If no keywords are present or no appropriate keywords are
        present, None is returned.
    :rtype: safe.messaging.Message
    """
    if keywords is None:
        return None

    join_words = ' - %s ' % tr('sourced from')
    analysis_details = tr('Analysis details')
    hazard_details = tr('Hazard details')
    hazard_title_keywords = 'hazard_title'
    hazard_source_keywords = 'hazard_source'
    exposure_details = tr('Exposure details')
    exposure_title_keywords = 'exposure_title'
    exposure_source_keyword = 'exposure_source'

    if hazard_title_keywords in keywords:
        hazard_title = tr(keywords[hazard_title_keywords])
    else:
        hazard_title = tr('Hazard layer')

    if hazard_source_keywords in keywords:
        hazard_source = tr(keywords[hazard_source_keywords])
    else:
        hazard_source = tr('an unknown source')

    if exposure_title_keywords in keywords:
        exposure_title = keywords[exposure_title_keywords]
    else:
        exposure_title = tr('Exposure layer')

    if exposure_source_keyword in keywords:
        exposure_source = keywords[exposure_source_keyword]
    else:
        exposure_source = tr('an unknown source')

    report = m.Message()
    report.add(m.Heading(analysis_details, **INFO_STYLE))
    report.add(hazard_details)
    report.add(m.Paragraph(
        hazard_title,
        join_words,
        hazard_source))

    report.add(exposure_details)
    report.add(m.Paragraph(
        exposure_title,
        join_words,
        exposure_source))

    if inasafe_flag:
        report.add(m.Heading(tr('Software notes'), **INFO_STYLE))
        # noinspection PyUnresolvedReferences
        inasafe_phrase = tr(
            'This report was created using InaSAFE version %s. Visit '
            'http://inasafe.org to get your free copy of this software! %s'
            ) % (get_version(), disclaimer())

        report.add(m.Paragraph(m.Text(inasafe_phrase)))
    return report


def add_ordered_combo_item(combo, text, data=None):
    """Add a combo item ensuring that all items are listed alphabetically.

    Although QComboBox allows you to set an InsertAlphabetically enum
    this only has effect when a user interactively adds combo items to
    an editable combo. This we have this little function to ensure that
    combos are always sorted alphabetically.

    :param combo: Combo box receiving the new item.
    :type combo: QComboBox

    :param text: Display text for the combo.
    :type text: str

    :param data: Optional UserRole data to be associated with the item.
    :type data: QVariant, str
    """
    size = combo.count()
    for combo_index in range(0, size):
        item_text = combo.itemText(combo_index)
        # see if text alphabetically precedes item_text
        if cmp(text.lower(), item_text.lower()) < 0:
            combo.insertItem(combo_index, text, data)
            return
        # otherwise just add it to the end
    combo.insertItem(size, text, data)


def open_in_browser(file_path):
    """Open a file in the default web browser.

    :param file_path: Path to the file that should be opened.
    :type file_path: str
    """
    webbrowser.open('file://%s' % file_path)


def html_to_file(html, file_path=None, open_browser=False):
    """Save the html to an html file adapting the paths to the filesystem.

    if a file_path is passed, it is used, if not a unique_filename is
    generated.

    :param html: the html for the output file.
    :type html: str

    :param file_path: the path for the html output file.
    :type file_path: str

    :param open_browser: if true open the generated html in an external browser
    :type open_browser: bool
    """
    if file_path is None:
        file_path = unique_filename(suffix='.html')

    # Ensure html is in unicode for codecs module
    html = get_unicode(html)
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

    if open_browser:
        open_in_browser(file_path)


def ranges_according_thresholds(
        unaffected_max, very_low_max, low_max, medium_max, high_max):
    """Return an ordered dictionary with the ranges according to thresholds.

    This used to classify a raster according three thresholds.

    :param unaffected_max: Unaffected threshold
    :type unaffected_max: float

    :param very_low_max: The very low threshold
    :type very_low_max: float

    :param low_max: The low threshold.
    :type low_max: float

    :param medium_max: The medium threshold.
    :type medium_max: float

    :param high_max: The high threshold.
    :type high_max: float

    :return The ranges.
    :rtype OrderedDict
    """
    ranges = OrderedDict()
    ranges[0] = [unaffected_max, very_low_max]
    ranges[1] = [very_low_max, low_max]
    ranges[2] = [low_max, medium_max]
    ranges[3] = [medium_max, high_max]
    ranges[4] = [high_max, None]
    return ranges


def read_file_keywords(layer_path, keyword=None):
    """Get metadata from the keywords file associated with a local
     file in the file system.

    .. note:: Requires a str representing a file path instance
              as parameter As opposed to read_keywords_from_layer which
              takes a inasafe file object as parameter.

    .. seealso:: read_keywords_from_layer

    :param: layer_path: a string representing a path to a layer
           (e.g. '/tmp/foo.shp', '/tmp/foo.tif')
    :type layer_path: str

    :param keyword: optional - the metadata keyword to retrieve e.g. 'title'
    :type keyword: str

    :return: A string containing the retrieved value for the keyword if
             the keyword argument is specified, otherwise the
             complete keywords dictionary is returned.

    :raises: KeywordNotFoundError, NoKeywordsFoundError, InvalidParameterError

    Note:
        * KeywordNotFoundError - occurs when the keyword is not recognised.
        * NoKeywordsFoundError - occurs when no keyword file exists.
        * InvalidParameterError - occurs when the layer does not exist.
    """
    # check the source layer path is valid
    if not os.path.isfile(layer_path):
        message = tr('Cannot get keywords from a non-existent file. File '
                     '%s does not exist.' % layer_path)
        raise InvalidParameterError(message)

    # check there really is a keywords file for this layer
    # priority for iso path first
    keyword_file_path = os.path.splitext(layer_path)[0]
    keyword_file_path += '.keywords'
    if not os.path.isfile(keyword_file_path):
        message = tr('No keywords file found for %s' % keyword_file_path)
        raise NoKeywordsFoundError(message)
    # now get the requested keyword using the inasafe library
    try:
        dictionary = read_keywords(keyword_file_path)
    except Exception, e:
        message = tr(
            'Keyword retrieval failed for %s (%s) \n %s' % (
                keyword_file_path, keyword, str(e)))
        raise KeywordNotFoundError(message)

    # if no keyword was supplied, just return the dict
    if keyword is None:
        if 'keyword_version' in dictionary.keys():
            dictionary['keyword_version'] = get_string(
                    dictionary['keyword_version'])
        return dictionary
    if keyword not in dictionary:
        message = tr('No value was found in file %s for keyword %s' % (
            keyword_file_path, keyword))
        raise KeywordNotFoundError(message)

    try:
        value = dictionary[keyword]
    except:
        raise
    if 'keyword_version' == keyword:
        value = get_string(value)
    return value


def replace_accentuated_characters(message):
    """Normalize unicode data in Python to remove umlauts, accents etc.

    :param message: The string where to delete accentuated characters.
    :type message: str, unicode

    :return: A string without umlauts, accents etc.
    :rtype: str
    """

    message = unicodedata.normalize('NFKD', message).encode('ASCII', 'ignore')
    return message.decode('utf-8')


def is_keyword_version_supported(
        keyword_version, inasafe_version=inasafe_keyword_version):
    """Check if the keyword version is supported by this InaSAFE version.

    .. versionadded: 3.3

    :param keyword_version: String representation of the keyword version.
    :type keyword_version: str

    :param inasafe_version: String representation of InaSAFE's version.
    :type inasafe_version: str

    :returns: True if supported, otherwise False.
    :rtype: bool
    """
    def minor_version(version):
        """Obtain minor version of a version (x.y)
        :param version: Version string.
        :type version: str

        :returns: Minor version.
        :rtype: str
        """
        version_split = version.split('.')
        return version_split[0] + '.' + version_split[1]

    version_compatibilities = {
        '3.3': ['3.2']
    }

    # Convert to minor version.
    keyword_version = minor_version(keyword_version)
    inasafe_version = minor_version(inasafe_version)

    if inasafe_version == keyword_version:
        return True

    if inasafe_version in version_compatibilities.keys():
        if keyword_version in version_compatibilities[inasafe_version]:
            return True
        else:
            return False
    else:
        return False
