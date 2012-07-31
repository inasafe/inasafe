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
import logging

def baseDataDir():
    """Create (if needed) and return the path to the base realtime data dir"""
    # TODO: support env var setting here too
    myBaseDataDir='/tmp/inasafe/realtime'
    mkDir(myBaseDataDir)
    return myBaseDataDir

def gisDataDir():
    """Create (if needed) and return the path to the base GIS data dir"""
    myDir = os.path.join(baseDataDir(), 'gis')
    mkDir(myDir)
    return myDir

def shakemapDataDir():
    """Create (if needed) and return the path to the base shakemap data dir"""
    myDir = os.path.join(baseDataDir(), 'shakemaps')
    mkDir(myDir)
    return myDir

def reportDataDir():
    """Create (if needed) and return the path to the base report data dir"""
    myDir = os.path.join(baseDataDir(), 'reports')
    mkDir(myDir)
    return myDir

def logDir():
    """Create (if needed) and return the path to the log directory"""
    myDir = os.path.join(baseDataDir(), 'logs')
    mkDir(myDir)
    return myDir

def mkDir(thePath):
    """Make a directory, making sure it is world writable"""
    if not os.path.exists(thePath):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        myOldMask = os.umask(0000)
        os.makedirs(thePath, 0777)
        # Resinstate the old mask for tmp
        os.umask(myOldMask)

def setupLogger(theLogger):
    """Run once when the module is loaded and enable logging
    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html
    """
    theLogger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    myLogFile = os.path.join(logDir(), 'realtime.log')
    myFileHandler = logging.FileHandler(myLogFile)
    myFileHandler.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    myConsoleHandler = logging.StreamHandler()
    myConsoleHandler.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    myFormatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    myFileHandler.setFormatter(myFormatter)
    myConsoleHandler.setFormatter(myFormatter)
    # add the handlers to the logger
    theLogger.addHandler(myFileHandler)
    theLogger.addHandler(myConsoleHandler)
