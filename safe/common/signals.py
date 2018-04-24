"""
InaSAFE Disaster risk assessment tool by AusAid - **Standard signal defs.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

These signals are defined for global use throughout the safe and InaSAFE
application. They provide context for when parts of the application want to
send messages to each other.

See: https://github.com/AIFDR/inasafe/issues/577 for more detailed explanation.

"""

import logging

from pydispatch import dispatcher

from safe.utilities.utilities import get_error_message

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


DYNAMIC_MESSAGE_SIGNAL = 'DynamicMessage'
STATIC_MESSAGE_SIGNAL = 'StaticMessage'
ERROR_MESSAGE_SIGNAL = 'ErrorMessage'

LOGGER = logging.getLogger('InaSAFE')


def send_static_message(sender, message):
    """Send a static message to the listeners.

    Static messages represents a whole new message. Usually it will
    replace the previous message.

    .. versionadded:: 3.3

    :param sender: The sender.
    :type sender: object

    :param message: An instance of our rich message class.
    :type message: safe.messaging.Message

    """
    dispatcher.send(
        signal=STATIC_MESSAGE_SIGNAL,
        sender=sender,
        message=message)


def send_dynamic_message(sender, message):
    """Send a dynamic message to the listeners.

    Dynamic messages represents a progress. Usually it will be appended to
    the previous messages.

    .. versionadded:: 3.3

    :param sender: The sender.
    :type sender: object

    :param message: An instance of our rich message class.
    :type message: safe.messaging.Message

    """
    dispatcher.send(
        signal=DYNAMIC_MESSAGE_SIGNAL,
        sender=sender,
        message=message)


def send_error_message(sender, error_message):
    """Send an error message to the listeners.

    Error messages represents and error. It usually replace the previous
    message since an error has been happened.

    .. versionadded:: 3.3

    :param sender: The sender.
    :type sender: object

    :param error_message: An instance of our rich error message class.
    :type error_message: ErrorMessage
    """
    dispatcher.send(
        signal=ERROR_MESSAGE_SIGNAL,
        sender=sender,
        message=error_message)


def analysis_error(sender, exception, message):
    """A helper to spawn an error and halt processing.

    An exception will be logged, busy status removed and a message
    displayed.

    .. versionadded:: 3.3

    :param sender: The sender.
    :type sender: object

    :param message: an ErrorMessage to display
    :type message: ErrorMessage, Message

    :param exception: An exception that was raised
    :type exception: Exception
    """
    LOGGER.exception(message)
    message = get_error_message(exception, context=message)
    send_error_message(sender, message)
