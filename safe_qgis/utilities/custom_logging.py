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

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import logging

# noinspection PyPackageRequirements
from PyQt4 import QtCore

third_party_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../', 'third_party'))
if third_party_dir not in sys.path:
    sys.path.append(third_party_dir)
# pylint: disable=F0401
# noinspection PyUnresolvedReferences,PyPackageRequirements
from raven.handlers.logging import SentryHandler
# noinspection PyUnresolvedReferences,PyPackageRequirements
from raven import Client
# pylint: enable=F0401

from safe.api import add_logging_handler_once
from safe_qgis.utilities.utilities import tr

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
            from qgis.core import QgsMessageLog
            # Check logging.LogRecord properties for lots of other goodies
            # like line number etc. you can get from the log message.
            QgsMessageLog.logMessage(record.getMessage(), 'InaSAFE', 0)
        #Make sure it doesn't crash if using Safe without QGIS
        except ImportError:
            pass
        except MemoryError:
            message = tr(
                'Due to memory limitations on this machine, InaSAFE can not '
                'handle the full log')
            print message
            QgsMessageLog.logMessage(message, 'InaSAFE', 0)


def setup_logger(sentry_url=None):
    """Run once when the module is loaded and enable logging.

    :param sentry_url: Optional url to sentry api for remote
        logging. Defaults to http://c64a83978732474ea751d432ab943a6b:
        d9d8e08786174227b9dcd8a4c3f6e9da@sentry.linfiniti.com/5 which is the
        sentry project for InaSAFE desktop.
    :type sentry_url: str

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
    logger = logging.getLogger('InaSAFE')
    # create formatter that will be added to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    qgis_handler = QgsLogHandler()
    qgis_handler.setFormatter(formatter)
    add_logging_handler_once(logger, qgis_handler)

    # Sentry handler - this is optional hence the localised import
    # It will only log if pip install raven. If raven is available
    # logging messages will be sent to http://sentry.linfiniti.com
    # We will log exceptions only there. You need to either:
    #  * Set env var 'INSAFE_SENTRY=1' present (value can be anything)
    #  * Enable the 'help improve InaSAFE by submitting errors to a remove
    #    server' option in InaSAFE options dialog
    # before this will be enabled.
    settings = QtCore.QSettings()
    flag = settings.value('inasafe/useSentry', False)
    if 'INASAFE_SENTRY' in os.environ or flag:
        if sentry_url is None:
            client = Client(
                'http://c64a83978732474ea751d432ab943a6b'
                ':d9d8e08786174227b9dcd8a4c3f6e9da@sentry.linfiniti.com/5')
        else:
            client = Client(sentry_url)
        sentry_handler = SentryHandler(client)
        sentry_handler.setFormatter(formatter)
        sentry_handler.setLevel(logging.ERROR)
        if add_logging_handler_once(logger, sentry_handler):
            logger.debug('Sentry logging enabled in safe_qgis')
        elif 'INASAFE_SENTRY' in os.environ:
            logger.debug('Sentry logging already enabled in safe')
    else:
        logger.debug('Sentry logging disabled in safe_qgis')
