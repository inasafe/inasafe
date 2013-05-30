"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Paragraph.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os

from safe.messaging import (
    Message,
    ErrorMessage,
    Text,
    EmphasizedText,
    ImportantText,
    Link,
    Heading,
    Paragraph,
    NumberedList,
    BulletedList,
    Image)


class MessagingTest(unittest.TestCase):
    """Tests for creating and displaying messages
    """

    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_text(self):
        """Tests Text messages are rendered correctly in plain text/html.
        """
        t1 = Text('FOO')
        t2 = Text('BAR')
        expected_res = 'FOO'

        res = t1.to_text()
        self.assertEqual(expected_res, res)

        t1.add(t2)
        expected_res = 'FOOBAR'
        res = t1.to_html()
        self.assertEqual(expected_res, res)

    def test_text_complex(self):
        """Tests Text messages are rendered correctly in plain text/html.
        """
        t1 = Text('FOO')
        ts = ImportantText('STRONG')
        t2 = Text(ts)
        t1.add(t2)
        expected_res = 'FOO*STRONG*'

        res = t1.to_text()
        self.assertEqual(expected_res, res)

    def test_heading(self):
        """Tests heading messages are rendered correctly in plain text/html.
        """
        h = Heading('FOO', -3)
        expected_res = '*FOO\n'
        res = h.to_text()
        self.assertEqual(expected_res, res)

        h = Heading('FOO', 8)
        expected_res = '********FOO\n'
        res = h.to_text()
        self.assertEqual(expected_res, res)

        expected_res = '<h6>FOO</h6>'
        res = h.to_html()
        self.assertEqual(expected_res, res)

    def test_paragraph(self):
        """Tests paragraphs are rendered correctly in plain text/html.
        """
        p = Paragraph('FOO')
        expected_res = '\nFOO\n'
        res = p.to_text()
        self.assertEqual(expected_res, res)

        expected_res = '<p>FOO</p>'
        res = p.to_html()
        self.assertEqual(expected_res, res)

    def test_item_list(self):
        """Tests complex messages are rendered correctly in plain text/html
        """
        l1 = NumberedList(Text('FOO'), ImportantText('BAR'), 'dsds')

        expected_res = (
            ' 0. FOO\n'
            ' 1. *BAR*\n'
            ' 2. dsds\n')
        res = l1.to_text()
        self.assertEqual(expected_res, res)

        expected_res = (
           '<ol>\n'
           '<li>FOO</li>\n'
           '<li><strong>BAR</strong></li>\n'
           '<li>dsds</li>\n'
           '</ol>')
        res = l1.to_html()
        self.assertEqual(expected_res, res)

        l1 = BulletedList(Text('FOO'), ImportantText('BAR'))
        l1.add('dsds')

        expected_res = (
            ' - FOO\n'
            ' - *BAR*\n'
            ' - dsds\n')
        res = l1.to_text()
        self.assertEqual(expected_res, res)

        expected_res = (
           '<ul>\n'
           '<li>FOO</li>\n'
           '<li><strong>BAR</strong></li>\n'
           '<li>dsds</li>\n'
           '</ul>')
        res = l1.to_html()
        self.assertEqual(expected_res, res)

    def test_message(self):
        """Tests high level messages are rendered correctly in plain text/html.
        """
        m1 = Message('FOO')
        expected_res = 'FOO\n'
        res = m1.to_text()
        self.assertEqual(expected_res, res)

        #TODO (MB) Check this double \n going on here
        m2 = Message(m1)
        expected_res = 'FOO\n\n'
        res = m2.to_text()
        self.assertEqual(expected_res, res)

        m3 = Message(Message('FOO'))
        m3.add(Message('BAR'))
        expected_res = 'FOO\n\nBAR\n\n'
        res = m3.to_text()
        self.assertEqual(expected_res, res)

    def test_complex_message(self):
        """Tests complex messages are rendered correctly in plain text/html
        """
        h1 = Heading('h1 title')
        h2 = Heading('h2 subtitle', 2)
        p1 = Paragraph('the quick brown fox jumps over the lazy dog')

        t1 = Text('this is a text, ')
        t1.add(Text('this is another text '))
        ts = ImportantText('and this is a strong text')
        t1.add(ts)
        tl = Link('http://google.ch', 'google link')
        t1.add(tl)
        tp = Text('text for paragraph ')
        em = EmphasizedText('this is an emphasized paragraph text')
        im = Image('http://www.google.ch/images/srpr/logo4w.png', 'Google logo')
        tp.add(im)
        tp.add(em)
        p2 = Paragraph(tp)

        m = Message()
        m.add(h1)
        m.add(h2)
        m.add(p1)
        m.add(t1)
        m.add(p2)

        expected_res = (
            '*h1 title\n\n'
            '**h2 subtitle\n\n'
            '\nthe quick brown fox jumps over the lazy dog\n\n'
            'this is a text, this is another text *and this is a strong text* '
            '::google link [http://google.ch]\n'
            '\ntext for paragraph ::Google logo '
            '[http://www.google.ch/images/srpr/logo4w.png] '
            '_this is an emphasized paragraph text_\n\n')

        res = m.to_text()
        self.assertEqual(expected_res, res)

        expected_res = (
            '<h1>h1 title</h1>\n'
            '<h2>h2 subtitle </h2>\n'
            '<p>the quick brown fox jumps over the lazy dog</p>\n'
            'this is a text, this is another text <strong>and this is a strong '
            'text</strong> <a href="http://google.ch">google link</a>\n'
            '<p>text for paragraph <img src="'
            'http://www.google.ch/images/srpr/logo4w.png" title="Google logo" '
            'alt="Google logo"/> <em>this is an emphasized paragraph text'
            '</em></p>\n')
        res = m.to_html()
        self.assertEqual(expected_res, res)

    def test_error_message(self):
        """Tests high level error messages are rendered in plain text/html.
        """
        em1 = ErrorMessage('SP')
        em2 = ErrorMessage('TP', 'TD', 'TS', 'TT')
        em0 = ErrorMessage('FP', 'FP', traceback='TBTB')

        em1.append(em2)
        em1.prepend(em0)
        expected_res = ("<h1>PROBLEM</h1>\n"
                        "<ul>\n"
                        "<li>FP</li>\n"
                        "<li>SP</li>\n"
                        "<li>TP</li>\n"
                        "</ul>\n"
                        "<h1>DETAIL</h1>\n"
                        "<ul>\n"
                        "<li>FP</li>\n"
                        "<li>TD</li>\n"
                        "</ul>\n"
                        "<h1>SUGGESTION</h1>\n"
                        "<ul>\n"
                        "<li>TS</li>\n"
                        "</ul>\n"
                        "<h1>TRACEBACK</h1>\n"
                        "['TBTB', None, 'TT']")
        res = em1.to_html()
        self.assertEqual(expected_res, res)

        em1 = ErrorMessage('FP')
        em2 = ErrorMessage('SP', detail='SD', traceback='TBTB')

        em1.append(em2)
        expected_res = (
            "*PROBLEM\n"
            "\n"
            " - FP\n"
            " - SP\n"
            "\n"
            "*DETAIL\n"
            "\n"
            " - SD\n"
            "\n"
            "*TRACEBACK\n"
            "\n"
            "[None, 'TBTB']\n")
        res = em1.to_text()
        self.assertEqual(expected_res, res)

if __name__ == '__main__':
    suite = unittest.makeSuite(MessagingTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
