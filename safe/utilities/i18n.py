# coding=utf-8
"""Internationalisation related utilities."""
import os
from PyQt4.QtCore import QCoreApplication, QSettings, QLocale, QTranslator
from safe import TranslationLoadError

__author__ = 'timlinux'


def tr(text):
    """Convencience QObject.tr wrapper for use by non QObject derived classes.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str
    """
    # Ensure that the text is a string
    text = str(text)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('@default', text)


def locale():
    """Find out the two letter locale for the current session.

    See if QGIS wants to override the system locale
    and then see if we can get a valid translation file
    for whatever locale is effectively being used.

    **Local is set with this precedence:**
    - If the LANG environment variable is set, it is used as first preference
    - If the user has 'locale/userLocale' defined it will be used as second
      preference
    - If the QLocale.system().name() returns a locale other than the default
      (en), it will be used as third preference.
    - As final fallback - english is used

    :returns: ISO  code for the users's preferred locale e.g. en_US.
    :rtype: str
    """
    if 'INASAFE_LANG' in os.environ:
        return os.environ['INASAFE_LANG']

    override_flag = QSettings().value(
        'locale/overrideFlag', True, type=bool)
    if override_flag:
        locale_name = QSettings().value('locale/userLocale', 'en_US', type=str)
    else:
        locale_name = QLocale.system().name()
        # NOTES: we split the locale name because we need the first two
        # character i.e. 'id', 'af, etc
        locale_name = str(locale_name).split('_')[0]
    os.environ['INASAFE_LANG'] = locale_name
    return locale_name


def translation_file():
    """Get the path to the translation file.

    :returns: Path to the translation.
    """
    locale_name = locale()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    translation_path = os.path.abspath(os.path.join(
        root,
        os.path.pardir,
        os.path.pardir,
        'i18n',
        'inasafe_' + str(locale_name) + '.qm'))
    return translation_path


def load_translation():
    """Load the translation file preferred by the user.

    If the file does not exist, the currently loaded (eng) language
    will be left intact.
    """
    path = translation_file()
    if os.path.exists(path):
        translator = QTranslator()
        result = translator.load(path)
        if not result:
            message = 'Failed to load translation for %s' % path
            raise TranslationLoadError(message)
        # noinspection PyTypeChecker,PyCallByClass
        QCoreApplication.installTranslator(translator)
    else:
        raise TranslationLoadError(
            'There is no InaSAFE translation for locale: %s' % locale())
