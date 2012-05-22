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
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message

    def test_table_with_header(self):
        '''Test html render of a table with header row(s).'''
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_header,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data, header_row=self.table_header)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message

    def test_table_caption(self):
        """Test table caption"""
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_caption,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data, caption=self.table_caption)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        #also test bottom caption
        expected_result = ('%s%s%s%s' % (self.html_table_start,
                                       self.html_bottom_caption,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_data,
                              caption=self.table_caption,
                              caption_at_bottom=True)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
