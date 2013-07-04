"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **Logging related code.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import logging
from datetime import date
import getpass
from tempfile import mkstemp

from PyQt4 import QtCore

from safe_qgis.exceptions import MethodUnavailableError

myDir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../', 'third_party'))
if myDir not in sys.path:
    sys.path.append(myDir)

# pylint: disable=F0401
# noinspection PyUnresolvedReferences
from raven.handlers.logging import SentryHandler
# noinspection PyUnresolvedReferences
from raven import Client
# pylint: enable=F0401
LOGGER = logging.getLogger('InaSAFE')


class QgsLogHandler(logging.Handler):
    """A logging handler that will log messages to the QGIS logging console."""

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self)

    def emit(self, theRecord):
        """Try to log the message to QGIS if available, otherwise do nothing.

        Args:
            theRecord: logging record containing whatever info needs to be
                logged.
        Returns:
            None
        Raises:
            None
        """
        try:
            #available from qgis 1.8
            from qgis.core import QgsMessageLog
            # Check logging.LogRecord properties for lots of other goodies
            # like line number etc. you can get from the log message.
            QgsMessageLog.logMessage(theRecord.getMessage(), 'InaSAFE', 0)

        except (MethodUnavailableError, ImportError):
            pass


def addLoggingHanderOnce(theLogger, theHandler):
    """A helper to add a handler to a logger, ensuring there are no duplicates.

    Args:
        * theLogger: logging.logger instance
        * theHandler: logging.Handler instance to be added. It will not be
            added if an instance of that Handler subclass already exists.

    Returns:
        bool: True if the logging handler was added

    Raises:
        None
    """
    myClassName = theHandler.__class__.__name__
    for myHandler in theLogger.handlers:
        if myHandler.__class__.__name__ == myClassName:
            return False

    theLogger.addHandler(theHandler)
    return True


def setupLogger(theLogFile=None, theSentryUrl=None):
    """Run once when the module is loaded and enable logging

    :param theLogFile: Optional full path to a file to write logs to.
    :type theLogFile: str

    :param theSentryUrl: Optional url to sentry api for remote
        logging. Defaults to http://c64a83978732474ea751d432ab943a6b:
        d9d8e08786174227b9dcd8a4c3f6e9da@sentry.linfiniti.com/5 which is the
        sentry project for InaSAFE desktop.
    :type theSentryUrl: str

    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html

    Use this to first initialise the logger (see safe/__init__.py)::

       from safe_qgis import utilities
       utilities.setupLogger()

    You would typically only need to do the above once ever as the
    safe model is initialised early and will set up the logger
    globally so it is available to all packages / subpackages as
    shown below.

    In a module that wants to do logging then use this example as
    a guide to get the initialised logger instance::

       # The LOGGER is initialised in utilities.py by init
       import logging
       LOGGER = logging.getLogger('InaSAFE')

    Now to log a message do::

       LOGGER.debug('Some debug message')

    .. note:: The file logs are written to the inasafe user tmp dir e.g.:
       /tmp/inasafe/23-08-2012/timlinux/logs/inasafe.log

    """
    myLogger = logging.getLogger('InaSAFE')
    myLogger.setLevel(logging.DEBUG)
    myDefaultHanderLevel = logging.DEBUG
    # create formatter that will be added to the handlers
    myFormatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create syslog handler which logs even debug messages
    # (ariel): Make this log to /var/log/safe.log instead of
    #               /var/log/syslog
    # (Tim) Ole and I discussed this - we prefer to log into the
    # user's temporary working directory.
    myTempDir = temp_dir('logs')
    myFilename = os.path.join(myTempDir, 'inasafe.log')
    if theLogFile is None:
        myFileHandler = logging.FileHandler(myFilename)
    else:
        myFileHandler = logging.FileHandler(theLogFile)
    myFileHandler.setLevel(myDefaultHanderLevel)
    # create console handler with a higher log level
    myConsoleHandler = logging.StreamHandler()
    myConsoleHandler.setLevel(logging.INFO)

    myQGISHandler = QgsLogHandler()

    # Sentry handler - this is optional hence the localised import
    # It will only log if pip install raven. If raven is available
    # logging messages will be sent to http://sentry.linfiniti.com
    # We will log exceptions only there. You need to either:
    #  * Set env var 'INSAFE_SENTRY=1' present (value can be anything)
    #  * Enable the 'help improve InaSAFE by submitting errors to a remove
    #    server' option in InaSAFE options dialog
    # before this will be enabled.
    mySettings = QtCore.QSettings()
    myFlag = mySettings.value('inasafe/useSentry', False).toBool()
    if 'INASAFE_SENTRY' in os.environ or myFlag:
        if theSentryUrl is None:
            myClient = Client(
                'http://c64a83978732474ea751d432ab943a6b'
                ':d9d8e08786174227b9dcd8a4c3f6e9da@sentry.linfiniti.com/5')
        else:
            myClient = Client(theSentryUrl)
        mySentryHandler = SentryHandler(myClient)
        mySentryHandler.setFormatter(myFormatter)
        mySentryHandler.setLevel(logging.ERROR)
        if addLoggingHanderOnce(myLogger, mySentryHandler):
            myLogger.debug('Sentry logging enabled')
    else:
        myLogger.debug('Sentry logging disabled')
    #Set formatters
    myFileHandler.setFormatter(myFormatter)
    myConsoleHandler.setFormatter(myFormatter)
    myQGISHandler.setFormatter(myFormatter)

    # add the handlers to the logger
    addLoggingHanderOnce(myLogger, myFileHandler)
    addLoggingHanderOnce(myLogger, myConsoleHandler)
    addLoggingHanderOnce(myLogger, myQGISHandler)


def temp_dir(sub_dir='work'):
    """Obtain the temporary working directory for the operating system.

    An inasafe subdirectory will automatically be created under this and
    if specified, a user subdirectory under that.

    .. note:: You can use this together with unique_filename to create
       a file in a temporary directory under the inasafe workspace. e.g.::

           tmpdir = temp_dir('testing')
           tmpfile = unique_filename(dir=tmpdir)
           print tmpfile
           /tmp/inasafe/23-08-2012/timlinux/testing/tmpMRpF_C

    If you specify INASAFE_WORK_DIR as an environment var, it will be
    used in preference to the system temp directory.

    :param sub_dir: Optional argument which will cause an additional
        subdirectory to be created e.g. \/tmp\/inasafe\/foo\/
    :type sub_dir: str

    :returns: Path to the output clipped layer (placed in the system temp dir).

    :raises: Any errors from the underlying system calls.
    """
    user = getpass.getuser().replace(' ', '_')
    current_date = date.today()
    date_string = current_date.isoformat()
    if 'INASAFE_WORK_DIR' in os.environ:
        new_directory = os.environ['INASAFE_WORK_DIR']
    else:
        # Following 4 lines are a workaround for tempfile.tempdir()
        # unreliabilty
        handle, filename = mkstemp()
        os.close(handle)
        new_directory = os.path.dirname(filename)
        os.remove(filename)

    path = os.path.join(new_directory, 'inasafe', date_string, user, sub_dir)

    if not os.path.exists(path):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        old_mask = os.umask(0000)
        os.makedirs(path, 0777)
        # Reinstate the old mask for tmp
        os.umask(old_mask)
    return path
