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

# Please import module in safe from the safe root, e.g:
# from safe.x.y import z

# If you let the import qgis below here, that will be the end of it. I will not
#  look for you, I will not pursue you. But if you don't, I will look for
# you, I will find you, and I will kill you - Liam Neeson
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
import logging

from safe.common.custom_logging import setup_logger

setup_logger('InaSAFE')