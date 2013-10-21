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
import os
import re
import webbrowser

from safe import messaging as m
from safe_qgis.safe_interface import unique_filename
from safe_qgis.utilities.utilities import (
    html_header,
    html_footer,
    map_qrc_to_file)

from PyQt4 import QtCore, QtGui, QtWebKit

DYNAMIC_MESSAGE_SIGNAL = 'ImpactFunctionMessage'
STATIC_MESSAGE_SIGNAL = 'ApplicationMessage'
LOGGER = logging.getLogger('InaSAFE')


class MessageViewer(QtWebKit.QWebView):
    """A simple message queue mockup."""
    static_message_count = 0

    # noinspection PyOldStyleClasses
    def __init__(self, the_parent):
        _ = the_parent  # needed for promoted Qt widget in designer
        super(MessageViewer, self).__init__()
        self.setWindowTitle('Message Viewer')
        # We use this var to keep track of the last allocated div id
        # in cases where we are assigning divs ids so we can scroll to them
        self.last_id = 0

        # whether to show or not dev only options
        self.dev_mode = QtCore.QSettings().value(
            'inasafe/developer_mode', False)

        if self.dev_mode:
            self.settings().globalSettings().setAttribute(
                QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        # Always gets replaced when a new message is passed
        self.static_message = None
        # Always get appended until the next static message is called,
        # then cleared
        self.dynamic_messages = []
        #self.show()

        self.impact_path = None

        #base_dir = os.path.dirname(__file__)
        #self.header = header.replace('PATH', base_dir)

    def contextMenuEvent(self, event):
        """Slot automatically called by Qt on right click on the WebView.

        :param event: the event that caused the context menu to be called.
        """

        context_menu = QtGui.QMenu(self)

        # add select all
        action = self.page().action(QtWebKit.QWebPage.SelectAll)
        action.setEnabled(not self.page_to_text() == '')
        context_menu.addAction(action)

        # add copy
        action = self.page().action(QtWebKit.QWebPage.Copy)
        action.setEnabled(not self.selectedHtml() == '')
        context_menu.addAction(action)

        action_page_to_html_file = QtGui.QAction(self.tr('Open in web '
                                                         'browser'), None)
        action_page_to_html_file.triggered.connect(
            #we use lambda to ignore the parameter coming from triggered
            lambda: self.page_to_html_file(open_browser=True))
        context_menu.addAction(action_page_to_html_file)

        # add view source if in dev mode
        if self.dev_mode:
            action = self.page().action(QtWebKit.QWebPage.InspectElement)
            action.setEnabled(True)
            context_menu.addAction(action)

            # add view to_text if in dev mode
            action_page_to_stdout = QtGui.QAction(self.tr('log pageToText'),
                                                  None)
            action_page_to_stdout.triggered.connect(self.page_to_stdout)
            context_menu.addAction(action_page_to_stdout)

        # show the menu
        context_menu.setVisible(True)
        context_menu.exec_(event.globalPos())

    def static_message_event(self, sender, message):
        """Static message event handler - set message state based on event.

        Static message events will clear the message buffer before displaying
        themselves.

        :param sender: Unused - the object that sent the message.
        :type sender: Object, None

        :param message: A message to show in the viewer.
        :type message: safe.messaging.message.Message
        """

        self.static_message_count += 1

        if message == self.static_message:
            return
        #LOGGER.debug('Static message event %i' % self.static_message_count)
        _ = sender  # we arent using it
        self.dynamic_messages = []
        self.static_message = message
        self.show_messages()

    def error_message_event(self, sender, message):
        """Error message event handler - set message state based on event.

        Error messages are treated as dynamic messages - they don't clear the
        message buffer.

        :param sender: The object that sent the message.
        :type sender: Object, None

        :param message: A message to show in the viewer.
        :type message: Message
        """
        LOGGER.debug('Error message event')
        self.dynamic_message_event(sender, message)

    def dynamic_message_event(self, sender, message):
        """Dynamic event handler - set message state based on event.

        Dynamic messages don't clear the message buffer.

        :param sender: Unused - the object that sent the message.
        :type sender: Object, None

        :param message: A message to show in the viewer.
        :type message: Message
        """
        LOGGER.debug('Dynamic message event')
        _ = sender  # we arent using it
        self.dynamic_messages.append(message)
        # Old way (works but causes full page refresh)
        self.show_messages()
        return

        # New way add html snippet to end of page, not currently working
        # self.last_id += 1
        # message.element_id = str(self.last_id)
        # # TODO probably we should do some escaping of quotes etc in message
        # html = message.to_html(in_div_flag=True)
        # html = html.replace('\'', '\\\'')
        # # We could run into side effect still if messages contain single
        # # quotes
        # LOGGER.debug('HTML: %s' % html)
        # js = 'document.body.innerHTML += \'%s\'' % html
        # LOGGER.debug('JAVASCRIPT: %s' % js)
        # self.page().mainFrame().evaluateJavaScript(js)
        # self.scrollToDiv()

    def scroll_to_div(self):
        """Scroll to the last added div.

        see resources/js/inasafe.js and also
        http://stackoverflow.com/a/4801719
        """
        if self.last_id > 0:
            js = '$(\'#%s\').goTo();' % str(self.last_id)
            #LOGGER.debug(js)
            self.page().mainFrame().evaluateJavaScript(js)

    def show_messages(self):
        """Show all messages."""
        string = html_header()
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

        string += html_footer()
        self.setHtml(string)
        #self.scroll_to_div()

    def to_message(self):
        """Collate all message elements to a single message."""
        my_message = m.Message()
        if self.static_message is not None:
            my_message.add(self.static_message)
        for myDynamic in self.dynamic_messages:
            my_message.add(myDynamic)
        return my_message

    def page_to_text(self):
        """Return the current page contents as plain text."""
        my_message = self.to_message()
        return my_message.to_text()

    def page_to_html(self):
        """Return the current page contents as html."""
        my_message = self.to_message()
        return my_message.to_html()

    def page_to_stdout(self):
        """Print to console the current page contents as plain text."""
        print self.page_to_text()

    def page_to_html_file(self, file_path=None, open_browser=False):
        """Save the current html viewer to an html file adapting the paths.

        if a file_path is passed, it is used, if not self.impact_path is used.
        if both are None, then a unique_filename is generated.

        qrc:/..../ paths gets converted to file:///..../

        :param file_path: the path for the html output file.
        :type file_path: str
        """
        if file_path is None:
            if self.impact_path is None:
                file_path = unique_filename(suffix='.html')
            else:
                file_path = '%s.html' % self.impact_path
        html = self.page().mainFrame().toHtml()
        file_dir = os.path.dirname(file_path)
        reg_exp = re.compile('qrc:/plugins/inasafe/([-./ \w]*)')
        html = reg_exp.sub(lambda match: map_qrc_to_file(match, file_dir),
                           html)

        with open(file_path, 'w') as f:
            f.write(html)

        if open_browser:
            webbrowser.open('file://%s' % file_path)