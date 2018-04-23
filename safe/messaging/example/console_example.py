"""
InaSAFE Disaster risk assessment tool by AusAid - **Dispatcher console example
.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from __future__ import print_function
from builtins import range
from builtins import object

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from pydispatch import dispatcher

from safe.messaging import (
    Message,
    Paragraph,
    SuccessParagraph,
    Text,
    ImportantText,
    EmphasizedText)

DYNAMIC_MESSAGE_SIGNAL = 'ImpactFunctionMessage'
STATIC_MESSAGE_SIGNAL = 'ApplicationMessage'


class ConsoleView(object):

    """A simple console based message queue mockup."""

    def __init__(self):
        # Always gets replaced when a new message is passed
        self.static_message = None
        # Message always get appended until the next static message is called,
        # then cleared
        self.dynamic_messages = []

    def static_message_event(self, sender, message):
        """Static message event handler - set message state based on event."""
        _ = sender  # NOQA
        self.dynamic_messages = []
        self.static_message = message
        self.show_messages()

    def dynamic_message_event(self, sender, message):
        """Dynamic event handler - set message state based on event."""
        _ = sender  # NOQA
        self.dynamic_messages.append(message)
        self.show_messages()

    def show_messages(self):
        """Show all messages."""
        string = ''
        if self.static_message is not None:
            string += self.static_message.to_text()

        for message in self.dynamic_messages:
            string += message.to_text()

        # fix_print_with_import
        print(string)


class ImpactFunction1(object):

    """Feedback progress for the impact function."""

    def __init__(self):
        message = Message(SuccessParagraph('IF1 was initialised'))
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)
        self.count = 0

    def run(self):
        self.count += 1
        message = Paragraph('IF1 run %i - running' % self.count)
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)


class App(object):

    """Class for messaging."""

    def __init__(self):
        self.message_queue = ConsoleView()
        # Set up dispatcher for dynamic messages
        # Dynamic messages will not clear the message queue so will be appended
        # to existing user messages
        dispatcher.connect(
            self.message_queue.dynamic_message_event,
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)
        # Set up dispatcher for static messages
        # Static messages clear the message queue and so the display is 'reset'
        dispatcher.connect(
            self.message_queue.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

    def run(self):
        message = Message(
            Text('This shows how you can create '),
            ImportantText('content inline when you create a message'),
            ' ',
            EmphasizedText('including different styles and so on.'))

        dispatcher.send(
            signal=STATIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

        impact_function1 = ImpactFunction1()
        # Run some tasks that will spawn dynamic messages
        for i in range(1, 10):
            _ = i  # NOQA
            impact_function1.run()


if __name__ == '__main__':
    app = App()
    app.run()
