# coding=utf-8

"""Utilities module."""

import re
import codecs
import json
import logging
import platform
import sys
import traceback
import unicodedata
import webbrowser

from PyQt4.QtCore import QPyNullVariant
from qgis.core import QgsApplication
from os.path import join, isdir

from safe.common.exceptions import NoKeywordsFoundError, MetadataReadError
from safe.definitions.versions import (
    inasafe_keyword_version,
    keyword_version_compatibilities)
from safe.definitions.messages import disclaimer
from safe import messaging as m
from safe.common.utilities import unique_filename
from safe.common.version import get_version
from safe.messaging import styles, Message
from safe.messaging.error_message import ErrorMessage
from safe.utilities.i18n import tr
from safe.utilities.unicode import get_unicode
from safe.utilities.keyword_io import KeywordIO

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE

LOGGER = logging.getLogger('InaSAFE')


def get_error_message(exception, context=None, suggestion=None):
    """Convert exception into an ErrorMessage containing a stack trace.

    :param exception: Exception object.
    :type exception: Exception

    :param context: Optional context message.
    :type context: str

    :param suggestion: Optional suggestion.
    :type suggestion: str

    .. see also:: https://github.com/inasafe/inasafe/issues/577

    :returns: An error message with stack trace info suitable for display.
    :rtype: ErrorMessage
    """

    name, trace = humanise_exception(exception)

    problem = m.Message(name)

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


def humanise_exception(exception):
    """Humanise a python exception by giving the class name and traceback.

    The function will return a tuple with the exception name and the traceback.

    :param exception: Exception object.
    :type exception: Exception

    :return: A tuple with the exception name and the traceback.
    :rtype: (str, str)
    """
    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
    name = exception.__class__.__name__
    return name, trace


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


def generate_expression_help(description, examples):
    """Generate the help message for QGIS Expressions.

    It will format nicely the help string with some examples.

    :param description: A description of the expression.
    :type description: basestring

    :param examples: A dictionnary of examples
    :type examples: dict

    :return: A message object.
    :rtype: message
    """
    help = m.Message()
    help.add(m.Paragraph(description))
    help.add(m.Paragraph(tr('Examples:')))
    bullets = m.BulletedList()
    for expression, result in examples.iteritems():
        if result:
            bullets.add(
                m.Text(
                    m.ImportantText(expression), m.Text('→'), m.Text(result)))
        else:
            bullets.add(m.Text(m.ImportantText(expression)))
    help.add(bullets)
    return help


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

    # Convert to minor version.
    keyword_version = minor_version(keyword_version)
    inasafe_version = minor_version(inasafe_version)

    if inasafe_version == keyword_version:
        return True

    if inasafe_version in keyword_version_compatibilities.keys():
        if keyword_version in keyword_version_compatibilities[inasafe_version]:
            return True
        else:
            return False
    else:
        return False


def write_json(data, filename):
    """Custom handler for writing json file in InaSAFE.

    Criteria:
    - use indent = 2
    - Handle NULL from QGIS

    :param data: The data that will be written.
    :type data: dict

    :param filename: The file name.
    :type filename: str
    """

    def custom_default(obj):
        if isinstance(obj, QPyNullVariant):
            return 'Null'
        raise TypeError

    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2, default=custom_default)


def human_sorting(the_list):
    """Sort the given list in the way that humans expect.

    From http://stackoverflow.com/a/4623518

    :param the_list: The list to sort.
    :type the_list: list

    :return: The new sorted list.
    :rtype: list
    """
    def try_int(s):
        try:
            return int(s)
        except ValueError:
            return s

    def alphanum_key(s):
        """Turn a string into a list of string and number chunks.

        For instance : "z23a" -> ["z", 23, "a"]
        """
        return [try_int(c) for c in re.split('([0-9]+)', s)]

    the_list.sort(key=alphanum_key)
    return the_list


def monkey_patch_keywords(layer):
    """In InaSAFE V4, we do monkey patching for keywords.

    :param layer: The layer to monkey patch keywords.
    :type layer: QgsMapLayer
    """
    keyword_io = KeywordIO()
    try:
        layer.keywords = keyword_io.read_keywords(layer)
    except (NoKeywordsFoundError, MetadataReadError):
        layer.keywords = {}

    try:
        layer.keywords['inasafe_fields']
    except KeyError:
        layer.keywords['inasafe_fields'] = {}


def readable_os_version():
    """Give a proper name for OS version

    :return: Proper OS version
    :rtype: str
    """
    if platform.system() == 'Linux':
        return ' '.join(platform.dist())
    elif platform.system() == 'Darwin':
        return ' {version}'.format(version=platform.mac_ver()[0])
    elif platform.system() == 'Windows':
        return platform.platform()


def is_plugin_installed(name):
    """Check if a plugin is installed, even if it's not enabled.

    :param name: Name of the plugin to check.
    :type name: string

    :return: If the plugin is installed.
    :rtype: bool
    """
    directory = QgsApplication.qgisSettingsDirPath()
    return isdir(join(directory, 'python', 'plugins', name))
