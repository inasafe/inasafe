# -*- coding: utf8 -*-
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QCoreApplication, QSettings, QLocale


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
    # Ensure that the text is a string
    if type(text) == 'str':
        text = text.decode('utf-8')
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('@default', text)


def locale():
    """Get the name of the currently active locale.

    :returns: Name of hte locale e.g. 'id'
    :rtype: stre
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
