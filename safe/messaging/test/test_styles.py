# coding=utf-8
# Tests for styles
import os
from unittest import TestCase
from safe.messaging.styles import logo_element


class TestStyles(TestCase):

    def test_logo_element(self):
        path = logo_element()
        self.assertTrue('file:///' in path)
