# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**QGIS plugin implementation.**

Contact : kolesov.dm@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. note:: This source code based on "QGIS Issue Tracking" discussion
     https://hub.qgis.org/issues/8955 with original author:
     Copyright (c) Joshua Arnott josh@snorfalorpagus.net

"""

# The module is used for testing only.
# It is not a part of inasafe workflow.

import sys

# configure paths for QGIS plugins
# (we need to set path for processing module)
# TS: Hard coded paths???? Very BAD! - lets get rid of / fix this!

# DK: Yes, it is very bad, I agree.
# (but I hope, it is not BAD: the prefixes are used in testing modules only,
#   they are not used when INASAFE is running as qgis plugin). I'll fix it.
# TS: Yes but for testing on windows / osx it will not work.

qgisprefix = '/usr'
sys.path.insert(0, qgisprefix + '/share/qgis/python')
sys.path.insert(1, qgisprefix + '/share/qgis/python/plugins')
sys.path.insert(2, qgisprefix + '/local/share/qgis/python')
sys.path.insert(3, qgisprefix + '/local/share/qgis/python/plugins')

# No this should come from the user environment rather as this is not
# portable to osx, win or my linux install

from safe.common.testing import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Note this is the QGIS processing (aka Sextante) lib being imported.
import processing
#from safe import postprocessors

# initalise processing plugin with dummy iface object
# plugin = postprocessors.classFactory(IFACE)
plugin = processing.classFactory(IFACE)
