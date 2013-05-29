from third_party.pydispatch import dispatcher

__author__ = 'timlinux'

import unittest
from message import Message


def handle_event(sender):
    """Simple event handler - will set STATE flag based on event."""
    sender.state = True


class DispatcherTest(unittest.TestCase):
    """Dispatcher test class."""
    state = None
    test_signal = 'Test'
    message_signal = 'Message'
    message = None

    def setUp(self):
        self.state = False
        self.message = None
        dispatcher.connect(
            handle_event, signal=self.test_signal, sender=dispatcher.Any)
        dispatcher.connect(
            self.handle_message_event,
            signal=self.message_signal,
            sender=dispatcher.Any)

    def test_basic_operation(self):
        """Test we can send a basic message."""
        dispatcher.send(signal=self.test_signal, sender=self)
        my_message = 'State changed failed'
        assert self.state, my_message

    def test_messsage(self):
        """Test we can send a basic message, setting it to the dispatcher."""
        message_text = 'Test message'
        message = Message(message_text)
        dispatcher.send(signal=self.message_signal, sender=message)
        # We should have now set the class property self.message to my_message
        self.assertEqual(message_text, self.message)


if __name__ == '__main__':
    unittest.main()
