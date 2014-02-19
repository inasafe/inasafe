# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Import Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__date__ = '05/02/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')
__author__ = 'timlinux'

import os
import unittest

from third_party.pydispatch import dispatcher
from safe_qgis.widgets.message_viewer import MessageViewer
from safe_qgis.safe_interface import messaging as m
from safe_qgis.safe_interface import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL)
from safe_qgis.utilities.utilities import get_error_message

TEST_FILES_DIR = os.path.join(
    os.path.dirname(__file__), '../../test/test_data/test_files')


class MessageViewerTest(unittest.TestCase):
    """Test cases for message viewer module."""

    def setUp(self):
        """Fixture run before all tests"""
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
        """Fixture run after each test"""
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
        """Make a fake error (helper for other tests)
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
        my_expected_result = open(
            TEST_FILES_DIR +
            '/test-error-message.txt',
            'r').read().replace('\n', '')
        self.assertEqual(text, my_expected_result)

    def test_static_and_error(self):
        """Test error message works when there is a static message in place."""
        self.message_viewer.static_message_event(None, m.Message('Hi'))
        text = self.fake_error()
        my_expected_result = open(
            TEST_FILES_DIR +
            '/test-static-error-message.txt',
            'r').read().replace('\n', '')
        self.assertEqual(text, my_expected_result)

if __name__ == '__main__':
    unittest.main()
