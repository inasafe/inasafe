# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**Internationalisation
utilities.**

The module provides utilities function to convert between unicode and byte
string for Python 2.x. When we move to Python 3, this module and its usage
should be removed as string in Python 3 is already stored in unicode.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '02/24/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QCoreApplication, QSettings, QLocale

from safe.utilities.unicode import get_unicode


def tr(text):
    """We define a tr() alias here since the utilities implementation below
    is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str, unicode

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str, unicode
    """
    # Ensure it's in unicode
    text = get_unicode(text)
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
