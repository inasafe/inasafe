# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Dispatcher gui example.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4 import Qt, QtWebKit

from pydispatch import dispatcher

from safe.messaging import (
    Message,
    Heading,
    Paragraph,
    SuccessParagraph,
    Text,
    ImportantText,
    EmphasizedText)
from safe.utilities.resources import resources_path

DYNAMIC_MESSAGE_SIGNAL = 'ImpactFunctionMessage'
STATIC_MESSAGE_SIGNAL = 'ApplicationMessage'


class WebView(QtWebKit.QWebView):

    """A simple message queue mockup."""

    def __init__(self):
        super(WebView, self).__init__()
        self.setWindowTitle('Message Viewer')
        # Always gets replaced when a new message is passed
        self.static_message = None
        # Always get appended until the next static message is called,
        # then cleared
        self.dynamic_messages = []
        self.show()

        # Read the header and footer html snippets
        header_path = resources_path('header.html')
        footer_path = resources_path('footer.html')
        header_file = file(header_path)
        footer_file = file(footer_path)
        header = header_file.read()
        self.footer = footer_file.read()
        header_file.close()
        footer_file.close()
        self.header = header.replace('PATH', resources_path())

    def static_message_event(self, sender, message):
        """Static message event handler - set message state based on event.

        :param message:
        :param sender:
        """
        _ = sender  # we arent using it
        self.dynamic_messages = []
        self.static_message = message
        self.show_messages()

    def dynamic_message_event(self, sender, message):
        """Dynamic event handler - set message state based on event.
        :param message:
        :param sender:
        """
        _ = sender  # we arent using it
        self.dynamic_messages.append(message)
        self.show_messages()

    def show_messages(self):
        """Show all messages."""
        string = self.header
        if self.static_message is not None:
            string += self.static_message.to_html()

        for message in self.dynamic_messages:
            string += message.to_html()

        string += self.footer
        print string
        self.setHtml(string)


class ImpactFunction1():
    """Fake impact function 1
    """

    def __init__(self):
        message = Message(SuccessParagraph('IF1 was initialised'))
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)
        self.count = 0

    def run(self):
        """Run
        """
        self.count += 1
        message = Paragraph('IF1 run %i - running' % self.count)
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)


class ImpactFunction2():
    """Fake impact function 2.
    """

    def __init__(self):
        message = Message(SuccessParagraph('IF2 was initialised'))
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)
        self.count = 0

    def run(self):
        """Run.
        """
        self.count += 1
        message = Paragraph('IF2 run %i - running' % self.count)
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)


class Dock():
    """Dock.
    """

    def __init__(self):
        self.message_queue = WebView()
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
        """Run.
        """
        message = Message()
        message.add(Heading('Processing starting'))
        text = Text('This is an example application showing how the ')
        text.add(ImportantText('new Messaging system'))
        text.add(Text(' works in '))
        text.add(EmphasizedText('InaSAFE'))
        text.add(Text('.'))
        paragraph = Paragraph(text)
        message.add(paragraph)
        paragraph = Paragraph(
            'Sed ut perspiciatis unde omnis iste natus error sit voluptatem '
            'accusantium doloremque laudantium, totam rem aperiam, '
            'eaque ipsa quae ab illo inventore veritatis et quasi architecto '
            'beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem '
            'quia voluptas sit aspernatur aut odit aut fugit, sed quia '
            'consequuntur magni dolores eos qui ratione voluptatem sequi '
            'nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor '
            'sit amet, consectetur, adipisci velit, sed quia non numquam eius '
            'modi tempora incidunt ut labore et dolore magnam aliquam quaerat '
            'voluptatem. Ut enim ad minima veniam, quis nostrum '
            'exercitationem ullam corporis suscipit laboriosam, nisi ut '
            'aliquid ex ea commodi consequatur? Quis autem vel eum iure '
            'reprehenderit qui in ea voluptate velit esse quam nihil molestiae'
            ' consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla'
            ' pariatur?')
        message.add(paragraph)
        message.add(Message(
            Text('This shows how you can create '),
            ImportantText('content inline when you create a message'),
            ' ',
            EmphasizedText('including different styles and so on.')))

        dispatcher.send(
            signal=STATIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

        impact_function1 = ImpactFunction1()
        impact_function2 = ImpactFunction2()
        # Run some tasks that will spawn dynamic messages
        for i in range(1, 10):
            _ = i
            impact_function1.run()
            impact_function2.run()

if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    dock = Dock()
    dock.run()
    sys.exit(app.exec_())
