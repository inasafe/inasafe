"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Table Tests implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.4.0'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest
from tables import Table


class TablesTest(unittest.TestCase):
    """Test the SAFE Table"""
    html = ('<!DOCTYPE html>\n'
        '<html lang="en">\n'
        ' <head>\n'
        '   <meta charset="utf-8">\n'
        '   <title>InaSAFE</title>\n'
        '   <meta name="description" content="">\n'
        '   <meta name="author" content="">\n'
        '   <link href="http://twitter.github.com/bootstrap/'
        'assets/css/bootstrap.css" rel="stylesheet">\n'
        '   <style>\n'
        '      caption.caption-bottom\n'
        '      {\n'
        '          caption-side:bottom;\n'
        '      }\n'
        '   </style>\n'
        ' </head>\n'
        ' <body>\n'
        '  <h2>Test Output</h2>\n'
        )

    def writeHtml(self, name):
        self.html += ' </body>\n</html>\n'
        file('/tmp/%s.html' % name, 'wt').write(self.html)

    def setUp(self):
        """Fixture run before all tests"""
        self.table_header = ['1', '2', '3', '4']
        self.table_data = [
                   ['a', 'b', 'c', 'd'],
                   ['a', 'b', 'c', 'd'],
                   ['a', 'b', 'c', 'd'],
                   ['a', 'b', 'c', 'd']
                ]
        self.table_caption = 'Man this is a nice table!'
        self.html_table_start = ('<table class="table table-striped'
                                 ' condensed">\n')
        self.html_table_end = '</table>\n'
        self.html_caption = (' <caption>Man this is a nice table!</caption>\n')
        self.html_bottom_caption = (' <caption class="caption-bottom">'
                                    'Man this is a nice table!</caption>\n')
        self.html_header = (' <thead>\n'
                            '  <tr>\n'
                              '   <th>1</th>\n'
                              '   <th>2</th>\n'
                              '   <th>3</th>\n'
                              '   <th>4</th>\n'
                              '  </tr>\n'
                              ' </thead>\n')
        self.html_body = (' <tbody>\n'
                          '  <tr>\n'
                          '   <td>a</td>\n'
                          '   <td>b</td>\n'
                          '   <td>c</td>\n'
                          '   <td>d</td>\n'
                          '  </tr>\n'
                          '  <tr>\n'
                          '   <td>a</td>\n'
                          '   <td>b</td>\n'
                          '   <td>c</td>\n'
                          '   <td>d</td>\n'
                          '  </tr>\n'
                          '  <tr>\n'
                          '   <td>a</td>\n'
                          '   <td>b</td>\n'
                          '   <td>c</td>\n'
                          '   <td>d</td>\n'
                          '  </tr>\n'
                          '  <tr>\n'
                          '   <td>a</td>\n'
                          '   <td>b</td>\n'
                          '   <td>c</td>\n'
                          '   <td>d</td>\n'
                          '  </tr>\n'
                          ' </tbody>\n')

    def tearDown(self):
        """Fixture run after each test"""
        pass

    def test_simple_table(self):
        """Test simple table creation"""
        self.html += '  <h2>Simple Table</h2>\n'
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('simple_table')

    def test_table_with_header(self):
        '''Test html render of a table with header row(s).'''
        self.html += '  <h2>Table with header</h2>\n'
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_header,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data, header_row=self.table_header)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_with_header')

    def test_table_caption(self):
        """Test table caption"""
        self.html += '  <h2>Caption Top</h2>\n'
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_caption,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data, caption=self.table_caption)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)

        #also test bottom caption
        self.html += '  <h2>Caption Bottom</h2>\n'
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_bottom_caption,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data,
                              caption=self.table_caption,
                              caption_at_bottom=True)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        self.html += str(actual_result)
        self.writeHtml('table_caption')

        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)

    def test_table_by_rows(self):
        """Test table from infividual rows"""
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_header,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data, header_row=self.table_header)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_by_rows')

