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
__date__ = '29/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
from item.message_element import MessageElement, InvalidMessageItemError
from . import Message, Text, Heading, BulletedList


LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class ErrorMessage():
    """Standard error message"""

    def __init__(self, problem, detail=None, suggestion=None, traceback=None):
        """
        Args:
            problem str or MessageElement describing a problem
            details str or MessageElement with detail of a problem
            suggestion str or MessageElement with a solution to the problem
            traceback TraceBack of the problem

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.problems = []
        self.details = []
        self.suggestions = []
        self.tracebacks = []

        self.problems.append(self._to_message_element(problem))
        self.details.append(self._to_message_element(detail))
        self.suggestions.append(self._to_message_element(suggestion))
        self.tracebacks.append(traceback)

    def _to_message_element(self, element):
        """
        Args:
            element the element to be checked and if necessary converted

        Returns:
            the correct element

        Raises:
            Errors are propagated
        """
        if element is None:
            return None
        elif isinstance(element, basestring):
            return Text(element)
        elif isinstance(element, MessageElement):
            return element
        else:
            raise InvalidMessageItemError

    def _render(self):
        """Create a Message version of this ErrorMessage

        Args:
            none

        Returns:
            the Message instance of this ErrorMessage

        Raises:
            Errors are propagated
        """
        message = Message()
        message.add(Heading('PROBLEM'))
        list = BulletedList()
        for p in self.problems:
            #p is _always_ not None
            list.add(p)
        message.add(list)

        if self.details.count(None) < len(self.details):
            list = BulletedList()
            message.add(Heading('DETAIL'))
            for d in self.details:
                if d is not None:
                    list.add(d)
            message.add(list)

        if self.suggestions.count(None) < len(self.suggestions):
            list = BulletedList()
            message.add(Heading('SUGGESTION'))
            for s in self.suggestions:
                if s is not None:
                    list.add(s)
            message.add(list)

        if self.tracebacks.count(None) < len(self.tracebacks):
            message.add(Heading('TRACEBACK'))
            message.add(str(self.tracebacks))
        return message

    def append(self, error_message):
        """add a ErrorMessage to the end of the queue


        Args:
            ErrorMessage message, an element to add to the message queue

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.problems = self.problems + error_message.problems
        self.details = self.details + error_message.details
        self.suggestions = self.suggestions + error_message.suggestions
        self.tracebacks = self.tracebacks + error_message.tracebacks

    def prepend(self, error_message):
        """add a ErrorMessage to the beginning of the queue


        Args:
            ErrorMessage message, an element to add to the message queue

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.problems = error_message.problems + self.problems
        self.details = error_message.details + self.details
        self.suggestions = error_message.suggestions + self.suggestions
        self.tracebacks = error_message.tracebacks + self.tracebacks

    def clear(self):
        """clear ErrorMessage queue

        Args:
            None

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.problems = []
        self.details = []
        self.suggestions = []
        self.tracebacks = []

    def to_text(self):
        """Render a ErrorMessage queue as plain text

        Args:
            None

        Returns:
            Str the text representation of the message queue

        Raises:
            Errors are propagated
        """

        return self._render().to_text()

    def to_html(self):
        """Render a ErrorMessage queue as html

        Args:
            None

        Returns:
            Str the html representation of the message queue

        Raises:
            Errors are propagated
        """

        return self._render().to_html()