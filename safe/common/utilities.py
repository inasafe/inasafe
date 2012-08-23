"""Utilities for InaSAFE
"""

import os
import gettext
import logging

# FIXME (Ole): For some reason this module doesn't work without this
# pylint: disable=W0404
import logging.handlers
# pylint: enable=W0404


class VerificationError(RuntimeError):
    """Exception thrown by verify()
    """
    pass


def verify(statement, message=None):
    """Verification of logical statement similar to assertions
    Input
        statement: expression
        message: error message in case statement evaluates as False

    Output
        None
    Raises
        VerificationError in case statement evaluates to False
    """

    if bool(statement) is False:
        raise VerificationError(message)


def ugettext(s):
    """Translation support
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'i18n'))
    if 'LANG' not in os.environ:
        return s
    lang = os.environ['LANG']
    filename_prefix = 'inasafe'
    t = gettext.translation(filename_prefix,
                            path, languages=[lang], fallback=True)
    return t.ugettext(s)


def setupLogger():
    """Run once when the module is loaded and enable logging
    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html

    Use this to first initialise the logger (see safe/__init__.py)::

       from safe.common import utilities
       utilities.setupLogger()

    You would typically only need to do the above once ever as the
    safe modle is initialised early and will set up the logger
    globally so it is available to all packages / subpackages as
    shown below.

    In a module that wants to do logging then use this example as
    a guide to get the initialised logger instance::

       # The LOGGER is intialised in utilities.py by init
       import logging
       LOGGER = logging.getLogger('InaSAFE')

    Now to log a message do::

       LOGGER.debug('Some debug message')

    Args: None

    Returns: None

    Raises: None
    """
    myLogger = logging.getLogger('InaSAFE')
    myLogger.setLevel(logging.DEBUG)
    # create syslog handler which logs even debug messages
    # FIXME(ariel): Make this log to /var/log/safe.log instead of
    #               /var/log/syslog
    mySysHandler = logging.handlers.SysLogHandler(address='/dev/log')
    mySysHandler.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    myConsoleHandler = logging.StreamHandler()
    myConsoleHandler.setLevel(logging.ERROR)
    # Email handler for errors
    myEmailServer = 'localhost'
    myEmailServerPort = 25
    mySenderAddress = 'logs@inasafe.org'
    myRecipientAddresses = ['tim@linfiniti.com']
    mySubject = 'Error'
    myEmailHandler = logging.handlers.SMTPHandler(
        (myEmailServer, myEmailServerPort),
        mySenderAddress,
        myRecipientAddresses,
        mySubject)
    myEmailHandler.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    myFormatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    mySysHandler.setFormatter(myFormatter)
    myConsoleHandler.setFormatter(myFormatter)
    myEmailHandler.setFormatter(myFormatter)
    # add the handlers to the logger
    myLogger.addHandler(mySysHandler)
    myLogger.addHandler(myConsoleHandler)
    myLogger.info('Safe Logger Module Loaded')
    myLogger.info('----------------------')
    myLogger.info('CWD: %s' % os.path.abspath(os.path.curdir))
