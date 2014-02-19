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

# This module is used for testing only.
# It is not a part of InaSAFE workflow.


from safe.common.testing import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# Note this is the QGIS processing (aka Sextante) lib being imported.
# Make sure ${QGIS_PREFIX_PATH}/share/qgis/python/plugins is in your
# PYTHONPATH so that the import below can be found!
import processing
#from safe import postprocessors

# initalise processing plugin with dummy iface object
# plugin = postprocessors.classFactory(IFACE)
plugin = processing.classFactory(IFACE)
