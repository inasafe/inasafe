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

from item.exceptions import InvalidMessageItemError
from item.message_element import MessageElement
from safe.utilities.i18n import tr
from . import (
    Message,
    Text,
    Heading,
    BulletedList,
    NumberedList,
    Paragraph)
from .styles import (
    GREEN_LEVEL_4_STYLE,
    ORANGE_LEVEL_5_STYLE,
    TRACEBACK_STYLE,
    TRACEBACK_ITEMS_STYLE,
    ORANGE_LEVEL_4_STYLE)

LOGGER = logging.getLogger('InaSAFE')

# We defined these styles locally because we use different icons


# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class ErrorMessage(MessageElement):
    """Standard error message."""

    def __init__(
            self,
            problem,
            detail=None,
            suggestion=None,
            traceback=None,
            **kwargs):
        """

        :param problem: Description of the problem.
        :type problem: str or MessageElement
        :param detail: Detail of the problem.
        :type detail: str or MessageElement
        :param suggestion: Suggested solution to the problem.
        :type suggestion: str or MessageElement
        :param traceback: A traceback from where the problem occurred.
        :type traceback: str or MessageElement

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(ErrorMessage, self).__init__(**kwargs)
        self.problems = []
        self.details = []
        self.suggestions = []
        self.tracebacks = NumberedList(**TRACEBACK_ITEMS_STYLE)

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
        elif self._is_stringable(element) or self._is_qstring(element):
            return Text(element)
        elif isinstance(element, MessageElement):
            return element
        else:
            raise InvalidMessageItemError(element, element.__class__)

    def standard_suggestions(self):
        """Standard generic suggestions.

        :return: List of standard suggestions for users who encounter errors.
        :rtype: BulletedList
        """
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
            'https://github.com/inasafe/inasafe/issues. Reporting an issue '
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
        return suggestions

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
        message.add(Heading(tr('Problem'), **ORANGE_LEVEL_4_STYLE))
        message.add(Paragraph(tr(
            'The following problem(s) were encountered whilst running the '
            'analysis.')))
        items = BulletedList()
        for p in reversed(self.problems):
            # p is _always_ not None
            items.add(p)
        message.add(items)

        message.add(Heading(tr('Suggestion'), **GREEN_LEVEL_4_STYLE))
        message.add(Paragraph(tr(
            'You can try the following to resolve the issue:')))
        if len(self.suggestions) < 1:
            suggestions = self.standard_suggestions()
            message.add(suggestions)
        else:
            items = BulletedList()
            for s in reversed(self.suggestions):
                if s is not None:
                    items.add(s)
            message.add(items)

        if len(self.details) > 0:
            items = BulletedList()
            message.add(Heading(
                tr('Details'), **ORANGE_LEVEL_5_STYLE))
            message.add(Paragraph(tr(
                'These additional details were reported when the problem '
                'occurred.')))
            for d in self.details:
                if d is not None:
                    items.add(d)
            message.add(items)

        message.add(Heading(tr(
            'Diagnostics'), **TRACEBACK_STYLE))
        message.add(self.tracebacks)
        return message

    def append(self, error_message):
        """Add an ErrorMessage to the end of the queue.

        Tracebacks are not appended.

        :param error_message: An element to add to the message.
        :type error_message: ErrorMessage

        """
        self.problems = self.problems + error_message.problems
        self.details = self.details + error_message.details
        self.suggestions = self.suggestions + error_message.suggestions
        self.tracebacks.items.extend(error_message.tracebacks.items)

    def prepend(self, error_message):
        """Add an ErrorMessage to the beginning of the queue.

        Tracebacks are not prepended.

        :param error_message: An element to add to the message.
        :type error_message: ErrorMessage
        """
        self.problems = error_message.problems + self.problems
        self.details = error_message.details + self.details
        self.suggestions = error_message.suggestions + self.suggestions

        new_tracebacks = error_message.tracebacks
        new_tracebacks.items.extend(self.tracebacks.items)
        self.tracebacks = new_tracebacks

    def clear(self):
        """Clear ErrorMessage.
        """
        self.problems = []
        self.details = []
        self.suggestions = []
        self.tracebacks = []

    def to_text(self):
        """Render an ErrorMessage as plain text.

        :returns: Plain text representation of the error message.
        :rtype: str

        """

        return self._render().to_text()

    # Argument count differs from overriden method
    # pylint: disable=W0221
    def to_html(self, in_div_flag=False):
        """Render a ErrorMessage queue as html.

        :param in_div_flag: Whether the message should be placed into a div
            element.
        :type in_div_flag: Boolean

        :returns: Html representation of the error message.
        :rtype: str
        """

        return self._render().to_html(in_div_flag=in_div_flag)
    # pylint: enable=W0221
