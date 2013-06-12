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
    SuccessParagraph,
    NumberedList,
    BulletedList,
    Image,
    LineBreak,
    Table,
    Row,
    Cell)


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
        expected_res = 'FOO BAR'
        res = t1.to_html()
        self.assertEqual(expected_res, res)

        t1 = Text('FOO', ImportantText('BAR'), 'function')
        expected_res = 'FOO <strong>BAR</strong> function'
        res = t1.to_html()
        self.assertEqual(expected_res, res)

    def test_line_break(self):
        """Tests Line Break messages are rendered correctly in plain text/html.
        """
        t1 = Message('FOO', LineBreak())

        expected_res = 'FOO\n'
        res = t1.to_text()
        self.assertEqual(expected_res, res)

        expected_res = 'FOO<br/>\n'
        res = t1.to_html()
        self.assertEqual(expected_res, res)

    def test_text_complex(self):
        """Tests Text messages are rendered correctly in plain text/html.
        """
        t1 = Text('FOO')
        ts = ImportantText('STRONG')
        t2 = Text(ts)
        t1.add(t2)
        expected_res = 'FOO *STRONG*'

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
        expected_res = '    FOO\n'
        res = p.to_text()
        self.assertEqual(expected_res, res)

        expected_res = '<p>FOO</p>'
        res = p.to_html()
        self.assertEqual(expected_res, res)

        p1 = Paragraph('FOO', ImportantText('BAR'), 'function')
        expected_res = '<p>FOO <strong>BAR</strong> function</p>'
        res = p1.to_html()
        self.assertEqual(expected_res, res)

    def test_success_paragraph(self):
        """Tests paragraphs are rendered correctly in plain text/html.
        """
        p = SuccessParagraph('FOO')
        expected_res = '    SUCCESS: FOO\n'
        res = p.to_text()
        self.assertEqual(expected_res, res)

        expected_res = '<p>FOO</p>'
        res = p.to_html()
        self.assertEqual(expected_res, res)

        p1 = SuccessParagraph('FOO', ImportantText('BAR'), 'function')
        expected_res = '<p>FOO <strong>BAR</strong> function</p>'
        res = p1.to_html()
        self.assertEqual(expected_res, res)

    @unittest.expectedFailure
    def test_error_on_invalid_keywords(self):
        """Test that an error occurs if unknown keywords are passed.

        The inheritance implementation should allow valid keywords defined in
         the base class or any of its childred, and fail if any unhandled
         keywords are provided.

        """
        NumberedList(
            Text('FOO'),
            ImportantText('BAR'),
            'dsds',
            element_id='error-message',
            style_class='error-class',
            invalid_param=None)

    def test_list(self):
        """Tests complex messages are rendered correctly in plain text/html
        """
        l1 = NumberedList(
            Text('FOO'),
            ImportantText('BAR'),
            'dsds',
            element_id='error-message',
            style_class='error-class')

        expected_res = (
            ' 1. FOO\n'
            ' 2. *BAR*\n'
            ' 3. dsds\n')
        res = l1.to_text()
        self.assertEqual(expected_res, res)

        expected_res = (
            '<ol id="error-message" class="error-class">\n'
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
        expected_res = 'FOO'
        res = m1.to_text()
        self.assertEqual(expected_res, res)

        m2 = Message(m1)
        expected_res = 'FOO\n'
        res = m2.to_text()
        self.assertEqual(expected_res, res)

        m3 = Message(Message('FOO'))
        m3.add(Message('BAR'))
        expected_res = 'FOO\nBAR\n'
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
        im = Image(
            'http://www.google.ch/images/srpr/logo4w.png',
            'Google logo')
        tp.add(im)
        tp.add(em)
        im = Image('http://www.google.ch/images/srpr/NoText.png')
        tp.add(im)
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
            '    the quick brown fox jumps over the lazy dog\n\n'
            'this is a text, this is another text *and this is a strong text* '
            '::google link [http://google.ch]\n'
            '    text for paragraph ::Google logo '
            '[http://www.google.ch/images/srpr/logo4w.png] '
            '_this is an emphasized paragraph text_'
            ' ::http://www.google.ch/images/srpr/NoText.png\n\n')

        res = m.to_text()
        self.assertEqual(expected_res, res)

        expected_res = (
            '<h1>h1 title</h1>\n'
            '<h2>h2 subtitle</h2>\n'
            '<p>the quick brown fox jumps over the lazy dog</p>\n'
            'this is a text, this is another text <strong>and this is a strong'
            ' text</strong> <a href="http://google.ch">google link</a>\n'
            '<p>text for paragraph <img src="'
            'http://www.google.ch/images/srpr/logo4w.png" title="Google logo" '
            'alt="Google logo"/> <em>this is an emphasized paragraph text'
            '</em> <img src="http://www.google.ch/images/srpr/NoText.png" '
            'title="" '
            'alt=""/></p>\n')
        res = m.to_html()
        self.assertEqual(expected_res, res)

    def test_error_message(self):
        """Tests high level error messages are rendered in plain text/html.
        """
        em0 = ErrorMessage('E0p', 'E0d', traceback='E0t')
        em1 = ErrorMessage('E1p')
        em2 = ErrorMessage('E2p', 'E2d', 'E2s', 'E2t')

        em1.append(em2)
        em1.prepend(em0)
        expected_res = (
            '<h5 class="warning"><i class="icon-remove-sign icon-white"></i>'
            ' Problem</h5>\n<p>The following problem(s) were encountered '
            'whilst running the analysis.</p>\n<ul>\n<li>E2p</li>\n<li>E1p'
            '</li>\n<li>E0p</li>\n</ul>\n<h5 class="problem">'
            '<i class="icon-list icon-white"></i> Detail</h5>\n<p>'
            'These additional details were reported when the problem occurred.'
            '</p>\n<ul>\n<li>E0d</li>\n<li>E2d</li>\n</ul>\n'
            '<h5 class="suggestion"><i class="icon-comment icon-white"></i>'
            ' Suggestion</h5>\n<p>You can try the following to'
            ' resolve the issue:</p>\n<ul>\n<li>E2s</li>\n</ul>\n'
            '<h5 class="inverse"><i class="icon-info-sign icon-white"></i>'
            ' Traceback</h5>\n<ol>\n<li>In file E0t</li>\n<li>In file E2t</li>'
            '\n</ol>\n')

        res = em1.to_html()
        self.assertEqual(expected_res, res)

        expected_res = (
            '*****Problem\n\n    The following problem(s) were encountered '
            'whilst running the analysis.\n\n - E2p\n - E1p\n - E0p\n\n'
            '*****Detail\n\n    These additional details were reported when '
            'the problem occurred.\n\n - E0d\n - E2d\n\n*****Suggestion\n\n'
            '    You can try the following to resolve the issue:\n\n - E2s\n\n'
            '*****Traceback\n\n 1. In file E0t\n 2. In file E2t\n\n')
        res = em1.to_text()
        self.assertEqual(expected_res, res)

    def test_table_html(self):
        """Tests cells are rendered correctly in html.
        """
        c1 = Cell('FOO')
        expected_res = '<td>FOO</td>\n'
        res = c1.to_html()
        self.assertEqual(expected_res, res)

        c2 = Cell('FOO', ImportantText('BAR'), 'function')
        expected_res = '<td>FOO <strong>BAR</strong> function</td>\n'
        res = c2.to_html()
        self.assertEqual(expected_res, res)

        r1 = Row(c1, c2, '3a')
        expected_res = (
            '<tr>\n<td>FOO</td>\n<td>FOO <strong>BAR</strong> function</td>\n'
            '<td>3a</td>\n</tr>\n')
        res = r1.to_html()
        self.assertEqual(expected_res, res)

        t1 = Table(r1, Row('1', '2', '3'), ['a', 'b', 'c'])
        expected_res = (
            '<table>\n<tbody>\n<tr>\n<td>FOO</td>\n<td>FOO '
            '<strong>BAR</strong> function</td>\n<td>3a</td>\n</tr>\n<tr>\n'
            '<td>1</td>\n<td>2</td>\n'
            '<td>3</td>\n</tr>\n<tr>\n<td>a</td>\n<td>b</td>\n<td>c</td>\n'
            '</tr>\n</tbody>\n</table>\n')
        res = t1.to_html()
        self.assertEqual(expected_res, res)

        t1.caption = 'Test Caption'
        expected_res = (
            '<table>\n<caption>Test Caption</caption>\n<tbody>\n<tr>\n'
            '<td>FOO</td>\n<td>FOO <strong>BAR</strong> function</td>\n'
            '<td>3a</td>\n</tr>\n<tr>\n<td>1</td>\n<td>2</td>\n<td>3</td>\n'
            '</tr>\n<tr>\n<td>a</td>\n<td>b</td>\n<td>c</td>\n</tr>\n'
            '</tbody>\n</table>\n')
        res = t1.to_html()
        self.assertEqual(expected_res, res)


if __name__ == '__main__':
    suite = unittest.makeSuite(MessagingTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
