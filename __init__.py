# coding=utf-8
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

import sys
import os
import logging

#
# Please do not put any application logic in the global space
# it will break the plugin reloader because QGIS will load stuff
# in our package tree whenever it scans for plugins.
#
# Also do not import anything from our package tree here!
#

sys.path.extend([os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir))])

from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QCoreApplication,
    QSettings)

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

root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
translation_path = os.path.join(
    root, 'i18n',
    'inasafe_' + str(locale_name) + '.qm')

if os.path.exists(translation_path):
    translator = QTranslator()
    result = translator.load(translation_path)
    if not result:
        message = 'Failed to load translation for %s' % locale_name
        raise Exception(message)
    # noinspection PyTypeChecker,PyCallByClass
    QCoreApplication.installTranslator(translator)

# noinspection PyDocstring,PyPep8Naming
def classFactory(iface):
    """Load Plugin class from file Plugin.

    Note that we do all the path manipulation and imports inside the factor
    so that when QGIS is just scanning plugin folders it does not trigger
    all modules being loaded.
    """
    sys.path.append(os.path.dirname(__file__))
    from safe.utilities.i18n import load_translation
    from safe.utilities.custom_logging import setup_logger
    from safe.common.exceptions import TranslationLoadError
    setup_logger()
    LOGGER = logging.getLogger('InaSAFE')
    parameter_package = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'safe_extras', 'parameters'))
    if parameter_package not in sys.path:
        sys.path.append(parameter_package)

    try:
        load_translation()
    except TranslationLoadError, e:
        LOGGER.info(e.message)
    from safe.plugin import Plugin
    return Plugin(iface)
