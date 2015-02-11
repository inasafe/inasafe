# coding=utf-8
from encodings.utf_8 import encode

__author__ = 'timlinux'

import unittest
from safe.messaging.item.text import PlainText


class TestText(unittest.TestCase):
    def test_plain_text(self):
        text = u'Helloᶁ world'
        try:
            PlainText(text)
        except:
            raise

if __name__ == '__main__':
    unittest.main()

