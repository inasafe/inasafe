
from PyQt4.QtCore import QCoreApplication


__author__ = 'timlinux'


def tr(text):
    """Convenience QObject.tr wrapper for use by non QObject derived classes.

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


def locale_name():
    """Figure out the locale name.

    :returns: Locale name e.g. 'id'.
    :rtype: str
    """
    # Setup internationalisation for the plugin.
    #
    # See if QGIS wants to override the system locale
    # and then see if we can get a valid translation file
    # for whatever locale is effectively being used.

    override_flag = QSettings().value(
        'locale/overrideFlag', True, type=bool)
    if override_flag:
        name = QSettings().value('locale/userLocale', 'en_US', type=str)
    else:
        name = QLocale.system().name()
        # NOTES: we split the locale name because we need the first two
        # character i.e. 'id', 'af, etc
        name = str(name).split('_')[0]
    return name
