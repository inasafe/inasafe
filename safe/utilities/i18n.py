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


# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtCore import QCoreApplication, QSettings, QLocale
import logging

from safe.utilities.unicode import get_unicode

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '02/24/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

LOGGER = logging.getLogger('InaSAFE')


def tr(text, context='@default'):
    """We define a tr() alias here since the utilities implementation below
    is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str, unicode

    :param context: A context for the translation. Since a same can be
        translated to different text depends on the context.
    :type context: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str, unicode
    """
    # Ensure it's in unicode
    text = get_unicode(text)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    translated_text = QCoreApplication.translate(context, text)
    # Check if there is missing container. If so, return the original text.
    # See #3164
    if text.count('%') == translated_text.count('%'):
        return translated_text
    else:
        content = (
            'There is a problem in the translation text.\n'
            'The original text: "%s".\n'
            'The translation: "%s".\n'
            'The number of %% character does not match (%s and %s).'
            'Please check the translation in transifex for %s.' % (
            text,
            translated_text,
            text.count('%'),
            translated_text.count('%s'),
            locale()
        ))
        LOGGER.warning(content)
        return text


def locale():
    """Get the name of the currently active locale.

    :returns: Name of hte locale e.g. 'id'
    :rtype: str
    """
    override_flag = QSettings().value(
        'locale/overrideFlag', True, type=bool)

    if override_flag:
        locale_name = QSettings().value('locale/userLocale', 'en_US', type=str)
    else:
        # noinspection PyArgumentList
        locale_name = QLocale.system().name()
        # NOTES: we split the locale name because we need the first two
        # character i.e. 'id', 'af, etc
        locale_name = str(locale_name).split('_')[0]
    return locale_name
