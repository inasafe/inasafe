import os
from PyQt4.QtCore import QCoreApplication, QSettings, QLocale, QTranslator
from safe import TranslationLoadError

__author__ = 'timlinux'


def tr(text):
    """We define a tr() alias here since the utilities implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('@default', text)


def locale():
    """Find out the two letter locale for the current session.

    See if QGIS wants to override the system locale
    and then see if we can get a valid translation file
    for whatever locale is effectively being used.

    :returns: ISO two letter code for the users's preferred locale.
    :rtype: str
    """
    override_flag = QSettings().value(
        'locale/overrideFlag', True, type=bool)
    if override_flag:
        locale_name = QSettings().value('locale/userLocale', 'en_US', type=str)
    else:
        locale_name = QLocale.system().name()
        # NOTES: we split the locale name because we need the first two
        # character i.e. 'id', 'af, etc
        locale_name = str(locale_name).split('_')[0]
    return locale_name


def translation_file():
    """Get the path to the translation file.

    :returns: Path to the translation.
    """
    locale_name = locale()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    translation_path = os.path.abspath(os.path.join(
        root, os.path.pardir, 'i18n', 'inasafe_' + str(locale_name) + '.qm'))
    return translation_path


def load_translation():
    """Load the translation file preferred by the user."""
    path = translation_file()
    if os.path.exists(path):
        translator = QTranslator()
        result = translator.load(path)
        if not result:
            message = 'Failed to load translation for %s' % path
            raise TranslationLoadError(message)
        # noinspection PyTypeChecker,PyCallByClass
        QCoreApplication.installTranslator(translator)
