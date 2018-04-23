# coding=utf-8
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
from collections import deque

from .item.exceptions import InvalidMessageItemError
from .item.message_element import MessageElement
from . import Text

LOGGER = logging.getLogger('InaSAFE')
# from pydev import pydevd

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Message(MessageElement):
    """Message object to contain a list of MessageElements."""

    def __init__(self, *args, **kwargs):
        """Creates a message object to contain a list of MessageElements

        Strings can be passed and are automatically converted in to
        item.Text()

        :arg args: One or more elements to add to the message queue


        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        self.in_div_flag = kwargs.pop('in_div_flag', False)
        super(Message, self).__init__(**kwargs)
        # we use a deque (double ended queue) so that we can support
        # prepending as well as appending items.
        self.message = deque()

        for m in args:
            self.add(m)

    def add(self, message):
        """Add a MessageElement to the end of the queue.

        Strings can be passed and are automatically converted in to
        item.Text()

        :param message: An element to add to the message queue.
        :type message: safe.messaging.Message, MessageElement, str

        """
        if self._is_stringable(message) or self._is_qstring(message):
            self.message.append(Text(message))
        elif isinstance(message, MessageElement):
            self.message.append(message)
        elif isinstance(message, Message):
            self.message.extend(message.message)
        else:
            raise InvalidMessageItemError(message, message.__class__)

    def prepend(self, message):
        """Prepend a MessageElement to the beginning of the queue.

        Strings can be passed and are automatically converted in to
        item.Text()

        :param message: An element to add to the message queue.
        :type message: safe.messaging.Message, MessageElement, str

        """
        if self._is_stringable(message) or self._is_qstring(message):
            self.message.appendleft(Text(message))
        elif isinstance(message, MessageElement):
            self.message.appendleft(message)
        elif isinstance(message, Message):
            self.message.extendleft(message.message)
        else:
            raise InvalidMessageItemError(message, message.__class__)

    def clear(self):
        """clear MessageElement queue
        """
        self.message = deque()

    def is_empty(self):
        """Helper to see if this message is empty."""
        if not len(self.message):
            return True
        else:
            return False

    def to_text(self):
        """Render a MessageElement queue as plain text.

        :returns: Plain text representation of the message.
        :rtype: str
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

    # Argument count differs from overriden method
    # pylint: disable=W0221
    def to_html(
            self,
            suppress_newlines=False,
            in_div_flag=False):  # pylint: disable=W0221
        """Render a MessageElement as html.

        :param suppress_newlines: Whether to suppress any newlines in the
            output. If this option is enabled, the entire html output will be
            rendered on a single line.
        :type suppress_newlines: bool

        :param in_div_flag: Whether the message should be placed into an outer
            div element.
        :type in_div_flag: bool

        :returns: HTML representation of the message.
        :rtype: str
        """

        if in_div_flag or self.in_div_flag:
            message = '<div %s>' % self.html_attributes()
        else:
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

        if in_div_flag:
            message += '</div>'

        if suppress_newlines:
            return message.replace('\n', '')
        return message
    # pylint: enable=W0221
