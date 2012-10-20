#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
tables.py - v0.04 2009-07-28 Philippe Lagadec

This module provides a few classes to easily generate HTML code such as tables
and lists.

Project website: http://www.decalage.info/python/html

License: CeCILL (open-source GPL compatible), see source code for details.
     http://www.cecill.info
"""

__version__ = '0.04'
__date__ = '2009-07-28'
__author__ = 'Philippe Lagadec'

#--- LICENSE ------------------------------------------------------------------

# Copyright Philippe Lagadec - see http://www.decalage.info/contact for contact
#  info
#
# this module provides a few classes to easily generate HTML tables and lists.
#
# this software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# A copy of the CeCILL license is also provided in these attached files:
# Licence_CeCILL_V2-en.html and Licence_CeCILL_V2-fr.html
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# the fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


#--- CHANGES ------------------------------------------------------------------

# 2008-10-06 v0.01 PL: - First version
# 2008-10-13 v0.02 PL: - added cellspacing and cellpadding to table
#                      - added functions to ease one-step creation of tables
#                        and lists
# 2009-07-21 v0.03 PL: - added column attributes and styles (first attempt)
#                        (thanks to an idea submitted by Michal Cernoevic)
# 2009-07-28 v0.04 PL: - improved column styles, workaround for Mozilla
# 2012-06-22 SAFE fork - refactored to use more modern table semantics and
#                        various other additions / changes to support SAFE
#                        Tim Sutton
# 2012-09-14 Add func: - add new function, column(int) for retrieve all element
#                        in the specific column
#                        Ismail Sunni

#------------------------------------------------------------------------------
#TODO:
# - method to return a generator (yield each row) instead of a single string
# - unicode support (input and output)
# - escape text in cells (optional)
# - constants for standard colors
# - use lxml to generate well-formed HTML ?
# - add classes/functions to generate a HTML page, paragraphs, headings, etc...


#--- thANKS -------------------------------------------------------------------

# - Michal Cernoevic, for the idea of column styles.

#--- REFERENCES ---------------------------------------------------------------

# HTML 4.01 specs: http://www.w3.org/tr/html4/struct/tables.html

# Colors: http://www.w3.org/tr/html4/types.html#type-color

# Columns alignement and style, one of the oldest and trickiest bugs in
# Mozilla: https://bugzilla.mozilla.org/show_bug.cgi?id=915


#--- CONSTANTS ----------------------------------------------------------------

TABLE_STYLE_THINBORDER = ''
DEFAULT_TABLE_CLASS = 'table table-striped condensed'
CAPTION_BOTTOM_CLASS = ' class="caption-bottom"'


class TableCell (object):
    """
    a TableCell object is used to create a cell in a HTML table. (td or th)

    Attributes:
    - text: text in the cell (may contain HTML tags). May be any object which
        can be converted to a string using str().
    - header: bool, false for a normal data cell (td), true for a header cell
      (th)
    - bgcolor: str, background color
    - width: str, width
    - align: str, horizontal alignement (left, center, right, justify or char)
    - char: str, alignment character, decimal point if not specified
    - charoff: str, see HTML specs
    - valign: str, vertical alignment (top|middle|bottom|baseline)
    - style: str, CSS style
    - attribs: dict, additional attributes for the td/th tag

    Reference: http://www.w3.org/tr/html4/struct/tables.html#h-11.2.6
    """

    def __init__(self, text="", bgcolor=None, header=False, width=None,
            align=None, char=None, charoff=None, valign=None, style='',
            attribs=None, cell_class=None, row_span=None, col_span=None):
        """TableCell constructor"""
        self.text = text
        self.bgcolor = bgcolor
        self.header = header
        self.width = width
        self.align = align
        self.char = char
        self.charoff = charoff
        self.valign = valign
        self.style = style
        self.attribs = attribs
        self.cell_class = cell_class
        self.row_span = row_span
        self.col_span = col_span
        if attribs is None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table cell as a string
        .. note:: Since we are using the bootstrap framework we set
           alignment using inlined css as bootstrap will override the
           alignment given by align and valign html attributes.
        """
        attribs_str = ''
        if self.bgcolor:
            self.attribs['bgcolor'] = self.bgcolor
        if self.width:
            self.attribs['width'] = self.width
        if self.align:
            self.attribs['align'] = self.align
            self.style += 'text-align: ' + self.align + ';'
        if self.char:
            self.attribs['char'] = self.char
        if self.charoff:
            self.attribs['charoff'] = self.charoff
        if self.valign:
            self.attribs['valign'] = self.valign
            self.style += 'text-align: ' + self.valign + ';'
        if self.style:
            self.attribs['style'] = self.style
        if self.cell_class:
            self.attribs['class'] = self.cell_class
        if self.row_span:
            self.attribs['rowspan'] = self.row_span
        if self.col_span:
            self.attribs['colspan'] = self.col_span
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.text:
            text = str(self.text)
        else:
            # An empty cell should at least contain a non-breaking space
            text = '&nbsp;'
        if self.header:
            return '   <th%s>%s</th>\n' % (attribs_str, text)
        else:
            return '   <td%s>%s</td>\n' % (attribs_str, text)


class TableRow (object):
    """
    a TableRow object is used to create a row in a HTML table. (tr tag)

    Attributes:
    - cells: list, tuple or any iterable, containing one string or TableCell
         object for each cell
    - header: bool, true for a header row (th),
      false for a normal data row (td)
    - bgcolor: str, background color
    - col_align, col_valign, col_char, col_charoff, col_styles: see Table class
    - attribs: dict, additional attributes for the tr tag

    Reference: http://www.w3.org/tr/html4/struct/tables.html#h-11.2.5
    """

    def __init__(self, cells=None, bgcolor=None, header=False, attribs=None,
            col_align=None, col_valign=None, col_char=None,
            col_charoff=None, col_styles=None):
        """TableCell constructor"""
        self.bgcolor = bgcolor
        self.cells = cells
        self.header = header
        self.col_align = col_align
        self.col_valign = col_valign
        self.col_char = col_char
        self.col_charoff = col_charoff
        self.col_styles = col_styles
        self.attribs = attribs
        if attribs is None:
            self.attribs = {}

    def apply_properties(self, cell, col):
        """Apply properties to the row"""
        # apply column alignment if specified:
        if self.col_align and cell.align is None:
            cell.align = self.col_align[col]
        if self.col_char and cell.char is None:
            cell.char = self.col_char[col]
        if self.col_charoff and cell.charoff is None:
            cell.charoff = self.col_charoff[col]
        if self.col_valign and cell.valign is None:
            # apply column style if specified:
            cell.valign = self.col_valign[col]
        if self.col_styles and cell.style is None:
            cell.style = self.col_styles[col]

    def column_count(self):
        """Return the number of columns in this row"""
        if isinstance(self.cells, basestring):
            #user instantiated the row with only a string for content\
            return 1
        else:
            return len(self.cells)

    def __str__(self):
        """return the HTML code for the table row as a string"""
        attribs_str = ""
        if self.bgcolor:
            self.attribs['bgcolor'] = self.bgcolor
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = '  <tr%s>\n' % attribs_str
        if isinstance(self.cells, basestring):
            #user instantiated the row with only a string for content\
            col = 1
            # setting colspan to 100% will force rows that were
            # created by passing str for the ctor to span the full
            # table width
            cell = TableCell(self.cells, col_span='100%', header=self.header)
            self.apply_properties(cell, col)
            result += str(cell)
        else:
            for cell in self.cells:
                col = self.cells.index(cell)    # cell column index
                if not isinstance(cell, TableCell):
                    cell = TableCell(cell, header=self.header)
                self.apply_properties(cell, col)
                result += str(cell)
        result += '  </tr>\n'
        return result


class Table(object):
    """
    a Table object is used to create a HTML table. (table tag)

    Attributes:
    - rows: list, tuple or any iterable, containing one iterable or TableRow
        object for each row
    - header_row: list, tuple or any iterable, containing the
      header row (optional)
    - class: str, CSS class to use. Defaults to DEFAULT_TABLE_CLASS
    - caption: str, caption for the table
    - border: str or int, border width
    - style: str, table style in CSS syntax (thin black borders by default)
    - width: str, width of the table on the page
    - attribs: dict, additional attributes for the table tag
    - col_width: list or tuple defining width for each column
    - col_align: list or tuple defining horizontal alignment for each column
    - col_char: list or tuple defining alignment character for each column
    - col_charoff: list or tuple defining charoff attribute for each column
    - col_valign: list or tuple defining vertical alignment for each column
    - col_styles: list or tuple of HTML styles for each column

    Reference: http://www.w3.org/tr/html4/struct/tables.html#h-11.2.1
    """

    def __init__(self, rows=None, border=None, style=None, width=None,
            cellspacing=None, cellpadding=None, attribs=None, header_row=None,
            table_class=None,
            col_width=None, col_align=None, col_valign=None,
            col_char=None, col_charoff=None, col_styles=None,
            caption=None, caption_at_bottom=False):
        """TableCell constructor"""
        # Ensure Rows is an array of rows
        if isinstance(rows, TableRow):
            rows = [rows]
        self.border = border
        self.style = style
        # style for thin borders by default
        if style is None:
            self.style = TABLE_STYLE_THINBORDER
        if table_class is None:
            self.table_class = DEFAULT_TABLE_CLASS
        self.caption = caption
        self.caption_at_bottom = caption_at_bottom
        self.width = width
        self.cellspacing = cellspacing
        self.cellpadding = cellpadding
        self.header_row = header_row
        self.rows = rows
        if not rows:
            self.rows = []
        self.attribs = attribs
        if not attribs:
            self.attribs = {}
        self.col_width = col_width
        self.col_align = col_align
        self.col_char = col_char
        self.col_charoff = col_charoff
        self.col_valign = col_valign
        self.col_styles = col_styles

    def mozilla_row_fix(self, row):
    # apply column alignments  and styles to each row if specified:
    # (Mozilla bug workaround)
        if self.col_align and not row.col_align:
            row.col_align = self.col_align
        if self.col_char and not row.col_char:
            row.col_char = self.col_char
        if self.col_charoff and not row.col_charoff:
            row.col_charoff = self.col_charoff
        if self.col_valign and not row.col_valign:
            row.col_valign = self.col_valign
        if self.col_styles and not row.col_styles:
            row.col_styles = self.col_styles
        return row

    def __str__(self):
        """return the HTML code for the table as a string"""
        attribs_str = ""
        if self.table_class:
            self.attribs['class'] = self.table_class
        if self.border:
            self.attribs['border'] = self.border
        if self.style:
            self.attribs['style'] = self.style
        if self.width:
            self.attribs['width'] = self.width
        if self.cellspacing:
            self.attribs['cellspacing'] = self.cellspacing
        if self.cellpadding:
            self.attribs['cellpadding'] = self.cellpadding
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = '<table%s>\n' % attribs_str
        if self.caption is not None:
            caption_class = ''
            if self.caption_at_bottom:
                # Note you can use css to place the caption at the bottom
                #caption.caption-bottom
                #{
                #  caption-side:bottom;
                #}
                caption_class = CAPTION_BOTTOM_CLASS
            result += ' <caption%s>%s</caption>\n' % (
                                    caption_class,
                                    self.caption)
        # insert column tags and attributes if specified:
        if self.col_width:
            for width in self.col_width:
                result += '  <col width="%s">\n' % width

        # First insert a header row if specified:
        if self.header_row:
            result += ' <thead>\n'
            if not isinstance(self.header_row, TableRow):
                result += str(TableRow(self.header_row, header=True))
            else:
                result += str(self.header_row)
            result += ' </thead>\n'
        # then all data rows:
        result += ' <tbody>\n'
        if isinstance(self.rows, basestring):
            #user instantiated the table with only a string for content
            row = TableRow(self.rows)
            self.mozilla_row_fix(row)
            result += str(row)
        else:
            for row in self.rows:
                if not isinstance(row, TableRow):
                    row = TableRow(row)
                self.mozilla_row_fix(row)
                result += str(row)
        result += ' </tbody>\n'
        result += '</table>'
        return result

    def toNewlineFreeString(self):
        """Return a string representation of the table which contains no
        newlines.

        .. note:: any preformatted <pre> blocks will be adversely affected by
           this.
        """
        return self.__str__().replace('\n', '')

    def column(self, col, header=False):
        """Return a list contains all element in col-th column
            Args:
                * col = number columnn
                * header = if False, doesn't include the header
            Returns:
                * list of string represent each element
            Note:
                If there is not column number col in a row, it will be
                represent as empty string ''
        """
        retval = []
        for myRow in self.rows:
            if myRow.header and not header:
                continue
            if col < myRow.column_count():
                retval.append(myRow.cells[col])
            else:
                retval.append('')

        return retval


class List (object):
    """
    a List object is used to create an ordered or unordered list in HTML.
    (UL/OL tag)

    Attributes:
    - lines: list, tuple or any iterable, containing one string for each line
    - ordered: bool, choice between an ordered (OL) or unordered list (UL)
    - attribs: dict, additional attributes for the OL/UL tag

    Reference: http://www.w3.org/tr/html4/struct/lists.html
    """

    def __init__(self, lines=None, ordered=False, start=None, attribs=None):
        """List constructor"""
        if lines:
            self.lines = lines
        else:
            self.lines = []
        self.ordered = ordered
        self.start = start
        if attribs:
            self.attribs = attribs
        else:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the list as a string"""
        attribs_str = ""
        if self.start:
            self.attribs['start'] = self.start
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.ordered:
            tag = 'ol'
        else:
            tag = 'ul'
        result = '<%s%s>\n' % (tag, attribs_str)
        for line in self.lines:
            result += ' <LI>%s\n' % str(line)
        result += '</%s>\n' % tag
        return result


# much simpler definition of a link as a function:
def Link(text, url):
    return '<a href="%s">%s</a>' % (url, text)


def link(text, url):
    return '<a href="%s">%s</a>' % (url, text)


def table(*args, **kwargs):
    'return HTML code for a table as a string. See Table class for parameters.'
    return str(Table(*args, **kwargs))


def htmllist(*args, **kwargs):
    'return HTML code for a list as a string. See List class for parameters.'
    return str(List(*args, **kwargs))

# Show sample usage when this file is launched as a script.
if __name__ == '__main__':

    # open an HTML file to show output in a browser
    f = open('test.html', 'w')

    t = Table()
    t.rows.append(TableRow(['A', 'B', 'C'], header=True))
    t.rows.append(TableRow(['D', 'E', 'F']))
    t.rows.append(('i', 'j', 'k'))
    f.write(str(t) + '<p>\n')
    print str(t)
    print '-' * 79

    t2 = Table([('1', '2'),
                ['3', '4']],
               width='100%', header_row=('col1', 'col2'),
    col_width=('', '75%'))
    f.write(str(t2) + '<p>\n')
    print t2
    print '-' * 79

    t2.rows.append(['5', '6'])
    t2.rows[1][1] = TableCell('new', bgcolor='red')
    t2.rows.append(TableRow(['7', '8'], attribs={'align': 'center'}))
    f.write(str(t2) + '<p>\n')
    print t2
    print '-' * 79

    # sample table with column attributes and styles:
    table_data = [
        ['Smith', 'John', 30, 4.5],
        ['Carpenter', 'Jack', 47, 7],
        ['Johnson', 'Paul', 62, 10.55],
    ]
    htmlcode = table(table_data,
                     header_row=['Last name', 'First name', 'Age', 'Score'],
                     col_width=['', '20%', '10%', '10%'],
                     col_align=['left', 'center', 'right', 'char'],
                     col_styles=['font-size: large', '', 'font-size: small',
                                 'background-color:yellow'])
    f.write(htmlcode + '<p>\n')
    print htmlcode
    print '-' * 79

    def gen_table_squares(n):
        """
        Generator to create table rows for integers from 1 to n
        """
    ##        # First, header row:
    ##        yield TableRow(('x', 'square(x)'), header=True, bgcolor='blue')
    ##        # then all rows:
        for x in range(1, n + 1):
            yield (x, x * x)

        s = Table(rows=gen_table_squares(10), header_row=('x', 'square(x)'))
        f.write(str(s) + '<p>\n')

        print '-' * 79
        l = List(['aaa', 'bbb', 'ccc'])
        f.write(str(l) + '<p>\n')
        l.ordered = True
        f.write(str(l) + '<p>\n')
        l.start = 10
        f.write(str(l) + '<p>\n')

        f.close()
