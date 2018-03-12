# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **Logging related code.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import logging
import os
import sys

from osgeo import gdal

# This is ugly but we dont have a better solution yet...
safe_extras_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'safe_extras'))
if safe_extras_dir not in sys.path:
    sys.path.append(safe_extras_dir)

# We add "# NOQA" because imports are not done at top of file.

from qgis.core import QgsMessageLog  # NOQA
from PyQt4.QtCore import QT_VERSION_STR, QSettings  # NOQA We can't move to
# our settings class.

from raven.handlers.logging import SentryHandler  # NOQA
from safe.common.utilities import log_file_path  # NOQA
from safe.common.version import get_version  # NOQA
from safe.definitions.provenance import (
    provenance_gdal_version,
    provenance_os,
    provenance_qgis_version,
    provenance_qt_version,
)  # NOQA
from safe.definitions.sentry import PRODUCTION_SERVER  # NOQA
from safe.utilities.i18n import tr  # NOQA
from safe.utilities.gis import qgis_version  # NOQA
from safe.utilities.utilities import readable_os_version  # NOQA

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class QgsLogHandler(logging.Handler):
    """A logging handler that will log messages to the QGIS logging console."""

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self)

    def emit(self, record):
        """Try to log the message to QGIS if available, otherwise do nothing.

        :param record: logging record containing whatever info needs to be
                logged.
        """
        try:
            # Check logging.LogRecord properties for lots of other goodies
            # like line number etc. you can get from the log message.
            QgsMessageLog.logMessage(record.getMessage(), 'InaSAFE', 0)
        except MemoryError:
            message = tr(
                'Due to memory limitations on this machine, InaSAFE can not '
                'handle the full log')
            print message
            QgsMessageLog.logMessage(message, 'InaSAFE', 0)


def add_logging_handler_once(logger, handler):
    """A helper to add a handler to a logger, ensuring there are no duplicates.

    :param logger: Logger that should have a handler added.
    :type logger: logging.logger

    :param handler: Handler instance to be added. It will not be added if an
        instance of that Handler subclass already exists.
    :type handler: logging.Handler

    :returns: True if the logging handler was added, otherwise False.
    :rtype: bool
    """
    class_name = handler.__class__.__name__
    for logger_handler in logger.handlers:
        if logger_handler.__class__.__name__ == class_name:
            return False

    logger.addHandler(handler)
    return True


def setup_logger(logger_name, log_file=None, sentry_url=None):
    """Run once when the module is loaded and enable logging.

    :param logger_name: The logger name that we want to set up.
    :type logger_name: str

    :param log_file: Optional full path to a file to write logs to.
    :type log_file: str

    :param sentry_url: Optional url to sentry api for remote
        logging. Defaults to URL defined in safe.definitions.sentry.py
        which is the sentry project for InaSAFE desktop.
    :type sentry_url: str

    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html

    Now to log a message do::

       LOGGER.debug('Some debug message')

    .. note:: The file logs are written to the inasafe user tmp dir e.g.:
       /tmp/inasafe/23-08-2012/timlinux/logs/inasafe.log
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    default_handler_level = logging.DEBUG

    # create formatter that will be added to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create syslog handler which logs even debug messages
    # (ariel): Make this log to /var/log/safe.log instead of
    #               /var/log/syslog
    # (Tim) Ole and I discussed this - we prefer to log into the
    # user's temporary working directory.
    inasafe_log_path = log_file_path()
    if log_file is None:
        file_handler = logging.FileHandler(inasafe_log_path)
    else:
        file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(default_handler_level)
    file_handler.setFormatter(formatter)
    add_logging_handler_once(logger, file_handler)

    if 'MUTE_LOGS' not in os.environ:
        # create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        add_logging_handler_once(logger, console_handler)

    # create a QGIS handler
    qgis_handler = QgsLogHandler()
    qgis_handler.setFormatter(formatter)
    add_logging_handler_once(logger, qgis_handler)

    # Sentry handler - this is optional hence the localised import
    # If raven is available logging messages will be sent to
    # http://sentry.kartoza.com
    # We will log exceptions only there. You need to either:
    #  * Set env var 'INASAFE_SENTRY=1' present (value can be anything)
    # before this will be enabled or sentry is enabled in QSettings
    flag = QSettings().value('inasafe/useSentry', False, type=bool)
    env_inasafe_sentry = 'INASAFE_SENTRY' in os.environ

    if env_inasafe_sentry or flag:
        if sentry_url is None:
            sentry_url = PRODUCTION_SERVER

        sentry_handler = SentryHandler(
            dsn=sentry_url,
            release=get_version(),
            tags={
                provenance_gdal_version['provenance_key']: gdal.__version__,
                provenance_os['provenance_key']: readable_os_version(),
                provenance_qgis_version['provenance_key']: qgis_version(),
                provenance_qt_version['provenance_key']: QT_VERSION_STR,
            }
        )
        sentry_handler.setFormatter(formatter)
        sentry_handler.setLevel(logging.ERROR)
        if add_logging_handler_once(logger, sentry_handler):
            logger.debug('Sentry logging enabled in safe')
    else:
        logger.debug('Sentry logging disabled in safe')
