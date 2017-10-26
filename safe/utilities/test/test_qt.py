# coding=utf-8
"""Tests for Qt specific utiltities."""

import unittest
from safe.utilities.qt import qt_at_least


class TestQt(unittest.TestCase):

    def test_qt_at_least(self):
        """Test that we can compare the installed qt version."""
        # simulate 4.7.2 installed
        test_version = 0x040702

        assert qt_at_least('4.6.4', test_version)
        assert qt_at_least('4.7.2', test_version)
        assert not qt_at_least('4.8.4', test_version)


if __name__ == '__main__':
    unittest.main()
