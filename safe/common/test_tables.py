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

import os
import tempfile
import unittest
from tables import Table, TableRow, TableCell, Link


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
        '  <h2>Test Output</h2>\n')
    tmp_dir = None

    def tmpDir(self):
        """Helper to get os temp dir.

        Args: None

        Returns: str Absolute filesystem path to temp dir.

        Raises: None
        """
        if self.tmp_dir is not None:
            return self.tmp_dir

        # Following 4 lines are workaround for tempfile.tempdir() unreliabilty
        myHandle, myFilename = tempfile.mkstemp()
        os.close(myHandle)
        myDir = os.path.dirname(myFilename)
        os.remove(myFilename)

        self.tmp_dir = myDir
        return myDir

    def writeHtml(self, name):
        self.html += ' </body>\n</html>\n'
        file(os.path.join(self.tmpDir(), '%s.html' % name),
             'wt').write(self.html)

    def setUp(self):
        """Fixture run before all tests"""
        self.table_header = ['1', '2', '3', '4']
        self.table_data = [
                    ['a', 'b', 'c', 'd'],
                    ['a', 'b', 'c', 'd'],
                    ['a', 'b', 'c', 'd'],
                    ['a', 'b', 'c', 'd']]
        self.table_row = TableRow(['a', 'b', 'c', 'd'])
        self.table_row_data = [self.table_row,
                               self.table_row,
                               self.table_row,
                               self.table_row]
        self.table_cell_a = TableCell('a')
        self.table_cell_b = TableCell('b')
        self.table_cell_c = TableCell('c')
        self.table_cell_d = TableCell('d')
        self.table_row_cells = TableRow([self.table_cell_a,
                                         self.table_cell_b,
                                         self.table_cell_c,
                                         self.table_cell_d])
        self.table_cell_data = [self.table_row_cells,
                                self.table_row_cells,
                                self.table_row_cells,
                                self.table_row_cells]
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
        self.html += '  <h2>Using Table Rows</h2>\n'
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_row_data)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_by_row_objects')

    def test_table_cells(self):
        """Test table from individual cells"""
        self.html += '  <h2>Using Table Cells</h2>\n'
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       self.html_body,
                                       self.html_table_end))
        actual_result = Table(self.table_cell_data)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_by_cell_objects')

    def test_col_span(self):
        """Testing column spanning"""
        table_cell_ab = TableCell('ab spanned', col_span=2)
        table_row = TableRow([table_cell_ab,
                                         self.table_cell_c,
                                         self.table_cell_d])
        self.html += '  <h2>Spanning Table Columns</h2>\n'
        body = (' <tbody>\n'
                '  <tr>\n'
                '   <td colspan="2">ab spanned</td>\n'
                '   <td>c</td>\n'
                '   <td>d</td>\n'
                '  </tr>\n'
                ' </tbody>\n')
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       body,
                                       self.html_table_end))
        actual_result = Table([table_row])
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_colspanning')

    def test_row_span(self):
        """Testing row spanning"""
        table_cell_aa = TableCell('aa spanned', row_span=2)
        table_row1 = TableRow([table_cell_aa,
                              self.table_cell_b,
                              self.table_cell_c,
                              self.table_cell_d])
        table_row2 = TableRow([self.table_cell_b,
                               self.table_cell_c,
                               self.table_cell_d])
        self.html += '  <h2>Spanning Table Columns</h2>\n'
        body = (' <tbody>\n'
                '  <tr>\n'
                '   <td rowspan="2">aa spanned</td>\n'
                '   <td>b</td>\n'
                '   <td>c</td>\n'
                '   <td>d</td>\n'
                '  </tr>\n'
                '  <tr>\n'
                '   <td>b</td>\n'
                '   <td>c</td>\n'
                '   <td>d</td>\n'
                '  </tr>\n'
                ' </tbody>\n')
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       body,
                                       self.html_table_end))
        actual_result = Table([table_row1, table_row2])
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_rowspanning')

    def test_cell_link(self):
        """Test cell links work"""
        table_cell_link = Link('InaSAFE', 'http://inasafe.org')
        table_row = TableRow([TableCell(table_cell_link),
                              self.table_cell_b,
                              self.table_cell_c,
                              self.table_cell_d])
        self.html += '  <h2>Link Cell Columns</h2>\n'
        body = (' <tbody>\n'
                '  <tr>\n'
                '   <td><a href="http://inasafe.org">InaSAFE</a></td>\n'
                '   <td>b</td>\n'
                '   <td>c</td>\n'
                '   <td>d</td>\n'
                '  </tr>\n'
                ' </tbody>\n')
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       body,
                                       self.html_table_end))
        actual_result = Table([table_row])
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_colspanning')

    def test_cell_header(self):
        """Test we can make a cell as a <th> element"""
        cell = TableCell('Foo', header=True)
        row = TableRow([cell])
        table = Table(row)
        del table

    def test_nested_table_in_cell(self):
        """Test nested table in cell"""
        inner_table = Table([['1', '2', '3']])
        cell = TableCell(inner_table)
        self.html += '  <h2>Table nested in Cell</h2>\n'
        body = (' <tbody>\n'
                '  <tr>\n'
                '   <td><table class="table table-striped condensed">\n'
                ' <tbody>\n'
                '  <tr>\n'
                '   <td>1</td>\n'
                '   <td>2</td>\n'
                '   <td>3</td>\n'
                '  </tr>\n'
                ' </tbody>\n'
                '</table></td>\n'
                '  </tr>\n'
                ' </tbody>\n')
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       body,
                                       self.html_table_end))
        actual_result = Table([[cell]])
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        self.html += str(actual_result)
        self.writeHtml('table_nested_in_cell')
        assert expected_result.strip() == str(actual_result).strip(), message

    def test_row_from_string(self):
        """Test row from string - it should span to the table width too"""
        table_row1 = TableRow([self.table_cell_a,
                               self.table_cell_b,
                               self.table_cell_c,
                               self.table_cell_d])
        self.html += '  <h2>Table row from string</h2>\n'
        body = (' <tbody>\n'
                '  <tr>\n'
                '   <td>a</td>\n'
                '   <td>b</td>\n'
                '   <td>c</td>\n'
                '   <td>d</td>\n'
                '  </tr>\n'
                '  <tr>\n'
                '   <td colspan="100%">foobar</td>\n'
                '  </tr>\n'
                '  <tr>\n'
                '   <td colspan="100%">Piet Pompies</td>\n'
                '  </tr>\n'
                ' </tbody>\n')
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       body,
                                       self.html_table_end))
        actual_result = Table([table_row1, 'foobar', 'Piet Pompies'])
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        self.html += str(actual_result)
        self.writeHtml('table_row_from_string')
        assert expected_result.strip() == str(actual_result).strip(), message

    def test_table_from_string(self):
        """Test table from string - should be a single cell in a single row"""
        self.html += '  <h2>Table from string</h2>\n'
        body = (' <tbody>\n'
                '  <tr>\n'
                '   <td colspan="100%">foobar</td>\n'
                '  </tr>\n'
                ' </tbody>\n')
        expected_result = ('%s%s%s' % (self.html_table_start,
                                       body,
                                       self.html_table_end))
        actual_result = Table('foobar')
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message
        self.html += str(actual_result)
        self.writeHtml('table_table_from_string')

    def test_table_with_colalign(self):
        """Table columns can be right justified"""

        # First with default alignment
        actual_result = Table(['12', '3000', '5'])

        expected_strings = ['<td colspan="100%">12</td>',
                            '<td colspan="100%">3000</td>',
                            '<td colspan="100%">5</td>']
        for s in expected_strings:
            message = ('Did not find expected string "%s" in result: %s'
                       % (s, actual_result))
            assert s in str(actual_result).strip(), message

        # Then using explicit alignment (all right justified)
        # FIXME (Ole): This does not work if e.g. col_align has
        # different strings: col_align = ['right', 'left', 'center']
        actual_result = Table(['12', '3000', '5'],
                              col_align=['right', 'right', 'right'])

        expected_strings = [
            ('<td colspan="100%" align="right" style="text-align: '
             'right;">12</td>'),
            ('<td colspan="100%" align="right" style="text-align: '
             'right;">3000</td>'),
            ('<td colspan="100%" align="right" style="text-align: '
             'right;">5</td>')]
        for s in expected_strings:
            message = ('Did not find expected string "%s" in result: %s'
                       % (s, actual_result))
            assert s in str(actual_result).strip(), message

        # Now try at the TableRow level
        # FIXME (Ole): Breaks tables!
        #row = TableRow(['12', '3000', '5'],
        #               col_align=['right', 'right', 'right'])
        #actual_result = Table(row)
        #print actual_result

        # This breaks too - what's going on?
        #row = TableRow(['12', '3000', '5'])
        #actual_result = Table(row)
        #print actual_result

        # Try at the cell level
        cell_1 = TableCell('12')
        cell_2 = TableCell('3000')
        cell_3 = TableCell('5')
        row = TableRow([cell_1, cell_2, cell_3])
        #print row  # OK
        table = Table(row)
        #print table  # Broken

        # Try at the cell level
        cell_1 = TableCell('12', align='right')
        cell_2 = TableCell('3000', align='right')
        cell_3 = TableCell('5', align='right')
        row = TableRow([cell_1, cell_2, cell_3])
        #print row  # OK

        # This is OK
        for cell in [cell_1, cell_2, cell_3]:
            msg = 'Wrong cell alignment %s' % cell
            assert 'align="right"' in str(cell), msg

        table = Table(row)
        self.html += str(table)
        self.writeHtml('table_column_alignment')

    def test_column(self):
        """Test to retrieve all element in a column.
        """
        table_body = []
        header = TableRow(['header1', 'header2', 'header3', 'header4'],
                          header=True)
        table_body.append(header)
        table_body.append(TableRow([1, 2, 3, 4]))
        table_body.append(TableRow(['a', 'b', 'c', 'd']))
        table_body.append(TableRow(['x', 'y', 'z', 't']))
        myTable = Table(table_body)
        expected_result1 = ['header1', 1, 'a', 'x']
        expected_result2 = [2, 'b', 'y']
        real_result1 = myTable.column(0, True)
        real_result2 = myTable.column(1)
        myMessage1 = "Expected %s but got %s" % (expected_result1,
                                                real_result1)
        myMessage2 = "Expected %s but got %s" % (expected_result2,
                                                 real_result2)
        assert expected_result1 == real_result1, myMessage1
        assert expected_result2 == real_result2, myMessage2

if __name__ == '__main__':
    suite = unittest.makeSuite(TablesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
