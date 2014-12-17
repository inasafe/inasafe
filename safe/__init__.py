"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
 - **Module inasafe.**

This script initializes the plugin, making it known to QGIS.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os

# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QCoreApplication,
    QSettings)
from safe.common.exceptions import TranslationLoadError


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

load_translation()
