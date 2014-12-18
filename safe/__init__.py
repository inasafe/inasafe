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

import logging
# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611
import logging
from safe.common.exceptions import TranslationLoadError
from safe.utilities.i18n import locale, translation_file, load_translation
from safe.utilities.custom_logging import setup_logger
LOGGER = logging.getLogger('InaSAFE')

setup_logger()
try:
    load_translation()
except TranslationLoadError, e:
    LOGGER.info(e.message)
