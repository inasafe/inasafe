# coding=utf-8
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
import logging
from safe import messaging as m
from safe_qgis.utilities.utilities import htmlHeader, htmlFooter

from PyQt4 import QtCore, QtGui, QtWebKit

DYNAMIC_MESSAGE_SIGNAL = 'ImpactFunctionMessage'
STATIC_MESSAGE_SIGNAL = 'ApplicationMessage'
LOGGER = logging.getLogger('InaSAFE')


class MessageViewer(QtWebKit.QWebView):
    """A simple message queue mockup."""
    # noinspection PyOldStyleClasses
    def __init__(self, theParent):
        _ = theParent  # needed for promoted Qt widget in designer
        super(MessageViewer, self).__init__()
        self.setWindowTitle('Message Viewer')
        # We use this var to keep track of the last allocated div id
        # in cases where we are assigning divs ids so we can scroll to them
        self.last_id = 0

        # whether to show or not dev only options
        self.devMode = QtCore.QSettings().value(
            'inasafe/devMode', False).toBool()

        if self.devMode:
            self.settings().globalSettings().setAttribute(
                QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        # Always gets replaced when a new message is passed
        self.static_message = None
        # Always get appended until the next static message is called,
        # then cleared
        self.dynamic_messages = []
        #self.show()

        #base_dir = os.path.dirname(__file__)
        #self.header = header.replace('PATH', base_dir)

    def contextMenuEvent(self, event):
        """Slot automatically called by Qt on right click on the WebView.

        :param event: the event that caused the context menu to be called.
        """

        context_menu = QtGui.QMenu(self)

        #add select all
        action = self.page().action(QtWebKit.QWebPage.SelectAll)
        action.setEnabled(not self.pageToText() == '')
        context_menu.addAction(action)

        #add copy
        action = self.page().action(QtWebKit.QWebPage.Copy)
        action.setEnabled(not self.selectedHtml().isEmpty())
        context_menu.addAction(action)

        #add view source if in dev mode
        if self.devMode:
            action = self.page().action(QtWebKit.QWebPage.InspectElement)
            action.setEnabled(True)
            context_menu.addAction(action)

            #add view to_text if in dev mode
            context_menu.addAction(
                self.tr('log pageToText'),
                self,
                QtCore.SLOT(self._printPageToText()))

        #show the menu
        context_menu.setVisible(True)
        context_menu.exec_(event.globalPos())

    def static_message_event(self, sender, message):
        """Static message event handler - set message state based on event.

        Static message events will clear the message buffer before displaying
        themselves.

        :param sender: Unused - the object that sent the message.
        :param message: A message to show in the viewer.
        :type message: Message
        """
        _ = sender  # we arent using it
        self.dynamic_messages = []
        self.static_message = message
        self.show_messages()

    def error_message_event(self, sender, message):
        """Error message event handler - set message state based on event.

        Error messages are treated as dynamic messages - they don't clear the
        message buffer.

        :param sender: The object that sent the message.
        :param message: A message to show in the viewer.
        :type message: Message
        """
        self.dynamic_message_event(sender, message)

    def dynamic_message_event(self, sender, message):
        """Dynamic event handler - set message state based on event.

        Dynamic messages don't clear the message buffer.

        :param sender: Unused - the object that sent the message.
        :param message: A message to show in the viewer.
        :type message: Message
        """
        _ = sender  # we arent using it
        self.dynamic_messages.append(message)
        self.last_id += 1
        message.element_id = str(self.last_id)
        # TODO probably we should do some escaping of quotes etc in message
        html = message.to_html(in_div_flag=True)
        html = html.replace('\'', '\\\'')
        js = 'document.body.innerHTML += %s' % html
        self.page().mainFrame().evaluateJavaScript(js)
        self.scrollToDiv()

    def scrollToDiv(self):
        """Scroll to the last added div.

        Scroll-to logic would work something like this
        see resources/js/inasafe.js and also
        http://stackoverflow.com/a/4801719
        """
        if self.last_id > 0:
            js = '$(\'#%s\').goTo();' % str(self.last_id)
            #LOGGER.debug(js)
            self.page().mainFrame().evaluateJavaScript(js)

    def show_messages(self):
        """Show all messages."""
        # self.setUrl(QtCore.QUrl(''))
        string = htmlHeader()
        if self.static_message is not None:
            string += self.static_message.to_html()

        # Keep track of the last ID we had so we can scroll to it
        self.last_id = 0
        for message in self.dynamic_messages:
            if message.element_id is None:
                self.last_id += 1
                message.element_id = str(self.last_id)

            html = message.to_html(in_div_flag=True)
            if html is not None:
                string += html

        string += htmlFooter()
        self.setHtml(string)
        self.scrollToDiv()

    def _toMessage(self):
        """Collate all message elements to a single message."""
        myMessage = m.Message()
        myMessage.add(self.static_message)
        for myDynamic in self.dynamic_messages:
            myMessage.add(myDynamic)
        return myMessage

    def pageToText(self):
        """Return the current page contents as plain text."""
        myMessage = self._toMessage()
        return myMessage.to_text()

    def pageToHtml(self):
        """Return the current page contents as html."""
        myMessage = self._toMessage()
        return myMessage.to_html()

    def _printPageToText(self):
        """Print to console the current page contents as plain text."""
        print self.pageToText()
