# coding=utf-8
"""Package safe_qgis."""

import os
import sys

# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QCoreApplication,
    QSettings)
from PyQt4.QtGui import QMessageBox

try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    # noinspection PyUnresolvedReferences
    from exceptions import TranslationLoadError
except ImportError:
    # Note we use translate directly but the string may still not translate
    # at this early stage since the i18n setup routines have not been called
    # yet.
    # noinspection PyTypeChecker,PyArgumentList
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin.')
    # noinspection PyTypeChecker,PyArgumentList
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)

# Add parent directory to path to make test aware of other modules
myDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if myDir not in sys.path:
    sys.path.append(myDir)


# Setup internationalisation for the plugin.
#
# See if QGIS wants to override the system locale
# and then see if we can get a valid translation file
# for whatever locale is effectively being used.

override_flag = QSettings().value(
    'locale/overrideFlag', True, type=bool)

if override_flag:
    locale_name = QSettings().value('locale/userLocale', 'en_US', type=str)
else:
    locale_name = QLocale.system().name()
    # NOTES: we split the locale name because we need the first two
    # character i.e. 'id', 'af, etc
    locale_name = str(locale_name).split('_')[0]

# Also set the system locale to the user overridden local
# so that the inasafe library functions gettext will work
# .. see:: :py:func:`common.utilities`
os.environ['LANG'] = str(locale_name)

# LOGGER.debug('%s %s %s %s' % (
#     preferred_locale,
#     override_flag,
#     QLocale.system().name(),
#     os.environ['LANG']))

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
translation_path = os.path.join(
    root, 'safe_qgis', 'i18n',
    'inasafe_' + str(locale_name) + '.qm')

if os.path.exists(translation_path):
    translator = QTranslator()
    result = translator.load(translation_path)
    if not result:
        message = 'Failed to load translation for %s' % locale_name
        raise TranslationLoadError(message)
    # noinspection PyTypeChecker,PyCallByClass
    QCoreApplication.installTranslator(translator)

# LOGGER.debug('%s %s' % (
#     translation_path,
#     os.path.exists(translation_path)))

# MONKEYPATCHING safe.defaults.get_defaults to use breakdown_defaults
# see safe_qgis.utilities.defaults for more details
import safe.defaults
from safe_qgis.utilities.defaults import breakdown_defaults
safe.defaults.get_defaults = lambda the_default=None: breakdown_defaults(
    the_default)

try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    from safe_qgis.utilities.custom_logging import setup_logger
    setup_logger()
except ImportError:
    # Note we use translate directly but the string may still not translate
    # at this early stage since the i18n setup routines have not been called
    # yet.
    import traceback

    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
    # Note that we do a late import here to avoid QPaintDevice before
    # QApplication errors when running tests of safe package. TS
    from PyQt4.QtCore import QCoreApplication
    from PyQt4.QtGui import QMessageBox
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin. If you experience '
                  'further problems after restarting please report the issue '
                  'to the InaSAFE team.')
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)
        #None, 'InaSAFE', myWarning + ' ' + e.message + ' ' + trace)
    raise
