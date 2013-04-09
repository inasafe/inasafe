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
import shutil
from datetime import datetime
from safe_qgis.utilities import setupLogger as setupLoggerSQ


def baseDataDir():
    """Create (if needed) and return the path to the base realtime data dir"""
    if 'INASAFE_WORK_DIR' in os.environ:
        myBaseDataDir = os.environ['INASAFE_WORK_DIR']
    else:
        # TODO: support env var setting here too
        myBaseDataDir = '/tmp/inasafe/realtime'
    mkDir(myBaseDataDir)
    return myBaseDataDir


def dataDir():
    """Return the path to the standard data dir for e.g. geonames data"""
    myDir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'fixtures'))
    mkDir(myDir)
    return myDir


def shakemapZipDir():
    """Create (if needed) and return the path to the base shakemap zip dir"""
    myDir = os.path.join(baseDataDir(), 'shakemaps-zipped')
    mkDir(myDir)
    return myDir


def shakemapExtractDir():
    """Create (if needed) and return the path to the base shakemap extract dir
    """
    myDir = os.path.join(baseDataDir(), 'shakemaps-extracted')
    mkDir(myDir)
    return myDir


def shakemapDataDir():
    """Create (if needed) and return the path to the base shakemap post
    procesed (tifs and pickled events) data dir.
    """
    myDir = os.path.join(baseDataDir(), 'shakemaps-processed')
    mkDir(myDir)
    return myDir


def shakemapCacheDir():
    """Create (if needed) and return the path to the base shakemap zip dir"""
    myDir = os.path.join(baseDataDir(), 'shakemaps-cache')
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


def purgeWorkingData():
    """Get rid of the shakemaps-* directories - mainly intended for
    invocation from unit tests to ensure there is a clean slate before
    testing."""
    shutil.rmtree(shakemapExtractDir())
    shutil.rmtree(shakemapDataDir())
    shutil.rmtree(shakemapZipDir())


def setupLogger():
    """Run once when the module is loaded and enable logging
    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html
    """
    myLogFile = os.path.join(logDir(), 'realtime.log')
    mySentryUrl = (
        'http://fda607badbe440be9a2fa6b22e759c72'
        ':5e871adb47ac4da1a1114b912deb274a@sentry.linfiniti.com/2')
    setupLoggerSQ(theSentryUrl=mySentryUrl, theLogFile=myLogFile)


def is_event_id(eventid):
    """Check if an id is event id.
    Event id is in form of yyyymmddHHMMSS or '%Y%m%d%H%M%S'
    i.e. 20130110204706
    """
    if len(eventid) != 14:
        return False
    try:
        datetime.strptime(eventid, '%Y%m%d%H%M%S')
    except ValueError:
        return False
    return True
