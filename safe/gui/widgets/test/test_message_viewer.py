# coding=utf-8
"""Test Message Viewer."""

import os
import unittest

from pydispatch import dispatcher

from safe.definitions.constants import INASAFE_TEST
from safe.gui.widgets.message_viewer import MessageViewer
from safe import messaging as m
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL)
from safe.utilities.utilities import get_error_message

from safe.test.utilities import get_qgis_app

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

__copyright__ = "Copyright 2013, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class MessageViewerTest(unittest.TestCase):

    """Test cases for message viewer module."""

    def setUp(self):
        """Fixture run before all tests."""
        os.environ['LANG'] = 'en'
        self.message_viewer = MessageViewer(None)
        self.message_viewer.show()
        # Set up dispatcher for dynamic messages
        # Dynamic messages will not clear the message queue so will be appended
        # to existing user messages
        dispatcher.connect(
            self.message_viewer.dynamic_message_event,
            signal=DYNAMIC_MESSAGE_SIGNAL)
        # Set up dispatcher for static messages
        # Static messages clear the message queue and so the display is 'reset'
        dispatcher.connect(
            self.message_viewer.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL)
        # Set up dispatcher for error messages
        # Static messages clear the message queue and so the display is 'reset'
        dispatcher.connect(
            self.message_viewer.error_message_event,
            signal=ERROR_MESSAGE_SIGNAL)

    def tearDown(self):
        """Fixture run after each test."""
        self.message_viewer = None

    def test_dynamic_message(self):
        """Test we can send dynamic messages to the message viewer."""
        self.message_viewer.dynamic_message_event(None, m.Message('Hi'))
        text = self.message_viewer.page_to_text()
        self.assertEqual(text, 'Hi\n')

    def test_static_message(self):
        """Test we can send static messages to the message viewer."""
        self.message_viewer.static_message_event(None, m.Message('Hi'))
        text = self.message_viewer.page_to_text()
        self.assertEqual(text, 'Hi\n')

    def fake_error(self):
        """Make a fake error (helper for other tests).

        :returns: Contents of the message viewer as string and with newlines
            stripped off.
        :rtype : str
        """
        e = Exception()
        context = 'Something went wrong'
        message = get_error_message(e, context=context)
        self.message_viewer.error_message_event(None, message)
        text = self.message_viewer.page_to_text().replace('\n', '')
        return text

    def test_error_message(self):
        """Test we can send error messages to the message viewer."""
        text = self.fake_error()
        self.assertIn('Exception****Suggestion', text)

    def test_static_and_error(self):
        """Test error message works when there is a static message in place."""
        self.message_viewer.static_message_event(None, m.Message('Hi'))
        text = self.fake_error()
        self.assertIn('****Problem', text)


if __name__ == '__main__':
    unittest.main()
