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

from safe.common.utilities import ugettext as tr

from item.message_element import MessageElement, InvalidMessageItemError
from . import (
    Message,
    Text,
    Heading,
    BulletedList,
    NumberedList,
    Paragraph)


LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd

# We defined these styles locally because we use different icons

PROBLEM_STYLE = {
    'level': 5,
    'icon': 'icon-remove-sign icon-white',
    'style_class': 'warning'}

DETAILS_STYLE = {
    'level': 5,
    'icon': 'icon-list icon-white',
    'style_class': 'problem'}

SUGGESTION_STYLE = {
    'level': 5,
    'icon': 'icon-comment icon-white',
    'style_class': 'suggestion'}

TRACEBACK_STYLE = {
    'level': 5,
    'icon': 'icon-info-sign icon-white',
    'style_class': 'inverse'}


class ErrorMessage(MessageElement):
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
        self.tracebacks = NumberedList()

        if problem is not None:
            self.problems.append(self._to_message_element(problem))
        if detail is not None:
            self.details.append(self._to_message_element(detail))
        if suggestion is not None:
            self.suggestions.append(self._to_message_element(suggestion))

        if traceback is not None:
            tokens = traceback.split(' File')
            for token in tokens:
                token = token.strip()
                if len(token) > 0:
                    self.tracebacks.add(Text('In file ' + token))

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
        elif isinstance(element, basestring) or self._is_qstring(element):
            return Text(element)
        elif isinstance(element, MessageElement):
            return element
        else:
            raise InvalidMessageItemError(element, element.__class__)

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
        message.add(Heading(tr('Problem'), **PROBLEM_STYLE))
        message.add(Paragraph(tr(
            'The following problem(s) were encountered whilst running the '
            'analysis.')))
        items = BulletedList()
        for p in reversed(self.problems):
            #p is _always_ not None
            items.add(p)
        message.add(items)

        if len(self.details) > 0:
            items = BulletedList()
            message.add(Heading(tr('Detail'), **DETAILS_STYLE))
            message.add(Paragraph(tr(
                'These additional details were reported when the problem '
                'occurred.')))
            for d in self.details:
                if d is not None:
                    items.add(d)
            message.add(items)

        message.add(Heading(tr('Suggestion'), **SUGGESTION_STYLE))
        message.add(Paragraph(tr(
            'You can try the following to resolve the issue:')))
        if len(self.suggestions) < 1:
            # Standard generic suggestions:
            suggestions = BulletedList()
            suggestions.add(
                'Check that you have the latest version of InaSAFE installed '
                '- you may have encountered a bug that is fixed in a '
                'subsequent release.')
            suggestions.add(
                'Check the InaSAFE documentation to see if you are trying to '
                'do something unsupported.')
            suggestions.add(
                'Report the problem using the issue tracker at '
                'https://github.com/AIFDR/inasafe/issues. Reporting an issue '
                'requires that you first create a free account at '
                'http://github.com. When you report the issue, '
                'please copy and paste the complete contents of this panel '
                'into the issue to ensure the best possible chance of getting '
                'your issue resolved.')
            suggestions.add(
                'Try contacting one of the InaSAFE development team by '
                'sending an email to info@inasafe.org. Please ensure that you '
                'copy and paste the complete contents of this panel into the '
                'email.')
            message.add(suggestions)
        else:
            items = BulletedList()
            for s in reversed(self.suggestions):
                if s is not None:
                    items.add(s)
            message.add(items)

        message.add(Heading(tr('Traceback'), **TRACEBACK_STYLE))
        message.add(self.tracebacks)
        return message

    def append(self, error_message):
        """add a ErrorMessage to the end of the queue.

        Tracebacks are not appended.


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
        self.tracebacks.items.extend(error_message.tracebacks.items)

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

        new_tracebacks = error_message.tracebacks
        new_tracebacks.items.extend(self.tracebacks.items)
        self.tracebacks = new_tracebacks

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
