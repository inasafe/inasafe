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

from safe.common.utilities import log_file_path

LOGGER = logging.getLogger('InaSAFE')


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
        logging. Defaults to http://c64a83978732474ea751d432ab943a6b:
        d9d8e08786174227b9dcd8a4c3f6e9da@sentry.linfiniti.com/5 which is the
        sentry project for InaSAFE desktop.
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
    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Sentry handler - this is optional hence the localised import
    # It will only log if pip install raven. If raven is available
    # logging messages will be sent to http://sentry.linfiniti.com
    # We will log exceptions only there. You need to either:
    #  * Set env var 'INASAFE_SENTRY=1' present (value can be anything)
    # before this will be enabled.
    if 'INASAFE_SENTRY' in os.environ:
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
            logger.debug('Sentry logging enabled in safe')
    else:
        logger.debug('Sentry logging disabled in safe')
    # Set formatters
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add the handlers to the logger
    add_logging_handler_once(logger, file_handler)
    add_logging_handler_once(logger, console_handler)
