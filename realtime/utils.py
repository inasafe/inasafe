"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Helpers, globals and general utilities for the realtime package**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '19/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os

def baseDataDir():
    """Create (if needed) and return the path to the base realtime data dir"""
    # TODO: support env var setting here too
    myBaseDataDir='/tmp/realtime'
    mkDir(myBaseDataDir)
    return myBaseDataDir

def gisDataDir():
    """Create (if needed) and return the path to the base GIS data dir"""
    myDir = os.path.join(REALTIME_DATA_DIR, 'gis')
    mkDir(myDir)
    return myDir

def shakemapDataDir():
    """Create (if needed) and return the path to the base shakemap data dir"""
    myDir = os.path.join(REALTIME_DATA_DIR, 'shakemaps')
    mkDir(myDir)
    return myDir

def reportDataDir():
    """Create (if needed) and return the path to the base report data dir"""
    myDir = os.path.join(REALTIME_DATA_DIR, 'reports')
    mkDir(myDir)
    return myDir

def mkDir(thePath):
    """Make a directory, making sure it is world writable"""
    if not os.path.exists(thePath):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        myOldMask = os.umask(0000)
        os.makedirs(myPath, 0777)
        # Resinstate the old mask for tmp
        os.umask(myOldMask)
