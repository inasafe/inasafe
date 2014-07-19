# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Base Configuration for the SFTP.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__version__ = '2.1'
__date__ = '13/01/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# The Server IP and its port where the shake data is being served
# The default sftp port is 22
BASE_URL = ''
PORT = 22

# Username and password to login to the server
USERNAME = ''
PASSWORD = ''

# The base path in the server
BASE_PATH = '/shakemaps'

# The default source of the grid.xml that will also be used for keywords file
GRID_SOURCE = 'BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) Indonesia'
