"""
Disaster risk assessment tool developed by AusAid - **QGIS plugin test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or 
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import sys
#todo - softcode in a configuration file
sys.path.append("/usr/local/share/qgis/python/")
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.utils import iface

QgsApplication.initQgis()


