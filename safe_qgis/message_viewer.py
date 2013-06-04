"""
InaSAFE Disaster risk assessment tool by AusAid - **Dispatcher gui example.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os
from safe import messaging as m
from third_party.pydispatch import dispatcher

from PyQt4 import Qt, QtGui, QtWebKit

DYNAMIC_MESSAGE_SIGNAL = 'ImpactFunctionMessage'
STATIC_MESSAGE_SIGNAL = 'ApplicationMessage'


class MessageViewer(QtWebKit.QWebView):
    """A simple message queue mockup."""
    def __init__(self, theDock):
        _ = theDock  # needed for promoted Qt widget in designer
        super(MessageViewer, self).__init__()
        self.setWindowTitle('Message Viewer')
        # Always gets replaced when a new message is passed
        self.static_message = None
        # Always get appended until the next static message is called,
        # then cleared
        self.dynamic_messages = []
        #self.show()

        # Read the header and footer html snippets
        base_dir = os.path.dirname(__file__)
        header_path = os.path.join(base_dir, 'resources', 'header.html')
        footer_path = os.path.join(base_dir, 'resources', 'footer.html')
        header_file = file(header_path, 'rt')
        footer_file = file(footer_path, 'rt')
        header = header_file.read()
        self.footer = footer_file.read()
        header_file.close()
        footer_file.close()
        self.header = header.replace('PATH', base_dir)

    def static_message_event(self, sender, message):
        """Static message event handler - set message state based on event."""
        _ = sender  # we arent using it
        self.dynamic_messages = []
        self.static_message = message
        self.show_messages()

    def error_message_event(self, sender, message):
        """Error message event handler - set message state based on event."""
        _ = sender  # we arent using it
        self.dynamic_messages.append(message)
        self.show_messages()

    def dynamic_message_event(self, sender, message):
        """Dynamic event handler - set message state based on event."""
        _ = sender  # we arent using it
        self.dynamic_messages.append(message)
        self.show_messages()

    def show_messages(self):
        """Show all messages."""
        string = self.header
        if self.static_message is not None:
            string += self.static_message.to_html()

        for message in self.dynamic_messages:
            html = message.to_html()
            if html is not None:
                string += html

        string += self.footer
        self.setHtml(string)
        #self.repaint()
        #QtGui.qApp.processEvents()

    def htmlHeader(self):
        """Get a standard html header for wrapping content in."""
        if self.header is None:
            self.header = htmlHeader()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            self.footer = htmlFooter()
        return self.footer

    def pageToText(self):
        """Return the current page contents as plain text."""
        self.page().currentFrame().toPlainText()

    def pageToHtml(self):
        """Return the current page contents as html."""
        self.page().currentFrame().toHtml()
