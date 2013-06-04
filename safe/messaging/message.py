"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Message Modele.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
from item.message_element import MessageElement, InvalidMessageItemError
from . import Text


LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class Message(MessageElement):
    """Message object to contain a list of MessageElements"""

    def __init__(self, *args):
        """Creates a message object to contain a list of MessageElements

        Strings can be passed and are automatically converted in to
        item.Text()

        Args:
            MessageElement message, an element to add to the message queue

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.message = []

        for m in args:
            self.add(m)

    def add(self, message):
        """add a MessageElement to the queue

        Strings can be passed and are automatically converted in to
        item.Text()

        Args:
            MessageElement message, an element to add to the message queue

        Returns:
            None

        Raises:
            Errors are propagated
        """
        if isinstance(message, basestring) or self._is_qstring(message):
            self.message.append(Text(message))
        elif isinstance(message, MessageElement):
            self.message.append(message)
        elif isinstance(message, Message):
            self.message.extend(message.message)
        else:
            raise InvalidMessageItemError(message, message.__class__)

    def clear(self):
        """clear MessageElement queue

        Args:
            None

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.message = []

    def to_text(self):
        """Render a MessageElement queue as plain text

        Args:
            None

        Returns:
            Str the text representation of the message queue

        Raises:
            Errors are propagated
        """
        message = ''
        last_was_text = False
        for m in self.message:
            if last_was_text and not isinstance(m, Text):
                message += '\n'

            message += m.to_text()

            if isinstance(m, Text):
                last_was_text = True
            else:
                message += '\n'
                last_was_text = False
        return message

    def to_html(self, noNewline=False):
        """Render a MessageElement queue as html

        Args:
            None

        Returns:
            Str the html representation of the message queue

        Raises:
            Errors are propagated
        """
        message = ''
        last_was_text = False
        for m in self.message:
            if last_was_text and not isinstance(m, Text):
                message += '\n'

            message += m.to_html()

            if isinstance(m, Text):
                last_was_text = True
            else:
                message += '\n'
                last_was_text = False

        if noNewline:
            return message.replace('\n', '')
        return message
