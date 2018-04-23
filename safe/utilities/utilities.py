# coding=utf-8

"""Utilities module."""


import codecs
import json
import logging
import platform
import re
import sys
import traceback
import unicodedata
import webbrowser
from os.path import join, isdir

from qgis.core import QgsApplication

import safe  # noqa
from safe import messaging as m
from safe.common.exceptions import NoKeywordsFoundError, MetadataReadError
from safe.common.utilities import unique_filename
from safe.definitions.versions import (
    inasafe_keyword_version,
    keyword_version_compatibilities)
from safe.messaging import styles, Message
from safe.messaging.error_message import ErrorMessage
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE

LOGGER = logging.getLogger('InaSAFE')


def basestring_to_message(text):
    """Convert a basestring to a Message object if needed.

    Avoid using this function, better to create the Message object yourself.
    This one is very generic.

    This function exists ust in case we get a basestring and we really need a
    Message object.

    :param text: The text.
    :type text: basestring, Message

    :return: The message object.
    :rtype: message
    """
    if isinstance(text, Message):
        return text
    elif text is None:
        return ''
    else:
        report = m.Message()
        report.add(text)
        return report


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


def generate_expression_help(description, examples, extra_information=None):
    """Generate the help message for QGIS Expressions.

    It will format nicely the help string with some examples.

    :param description: A description of the expression.
    :type description: basestring

    :param examples: A dictionary of examples
    :type examples: dict

    :param extra_information: A dictionary of extra information.
    :type extra_information: dict

    :return: A message object.
    :rtype: message
    """
    def populate_bullet_list(message, information):
        """Populate a message object with bullet list.

        :param message: The message object.
        :type message: Message

        :param information: A dictionary of information.
        :type information: dict

        :return: A message object that has been updated.
        :rtype: Message
        """
        bullets = m.BulletedList()
        for key, item in list(information.items()):
            if item:
                bullets.add(
                    m.Text(m.ImportantText(key), m.Text('→'), m.Text(item)))
            else:
                bullets.add(m.Text(m.ImportantText(key)))
        message.add(bullets)
        return message

    help = m.Message()
    help.add(m.Paragraph(description))
    help.add(m.Paragraph(tr('Examples:')))
    help = populate_bullet_list(help, examples)

    if extra_information:
        help.add(m.Paragraph(extra_information['title']))
        help = populate_bullet_list(help, extra_information['detail'])

    return help


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
    html = html
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

    if inasafe_version in list(keyword_version_compatibilities.keys()):
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
        if obj is None:
            return ''
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

    if not layer.keywords.get('inasafe_fields'):
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


def reload_inasafe_modules(module_name=None):
    """Reload python modules.

    :param module_name: Specific module name.
    :type module_name: str
    """

    if not module_name:
        module_name = 'safe'
    list_modules = list(sys.modules.keys())
    for module in list_modules:
        if not sys.modules[module]:
            continue
        if module.startswith(module_name):
            del sys.modules[module]
