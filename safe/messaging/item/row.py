# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Row**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from __future__ import absolute_import

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '04/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from .exceptions import InvalidMessageItemError

from .cell import Cell
from .image import Image
from .message_element import MessageElement


# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Row(MessageElement):
    """A class to model table rows in the messaging system."""

    def __init__(self, *args, **kwargs):
        """Creates a row object

        :param *args: args can be list or Cell of values to prepopulate the
            row cells with.
        :type *args: list, Cell

        :param header: A flag to indicate if the cell should be treated as
            a header cell. Depending on the ouput format cells may be rendered
            differently e.g. with bold text.
        :type header: bool

        :param align: A flag to indicate if special alignment should
            be given to cells in the row if supported in the output renderer.
            Valid options are: None, 'left', 'right', 'center'

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        header_flag = False
        if 'header' in kwargs:
            header_flag = kwargs['header']
            kwargs.pop('header')

        # Also check if align parameter is called before calling the ABC
        align = None
        if 'align' in kwargs:
            if kwargs['align'] in [None, 'left', 'right', 'center']:
                align = kwargs['align']
            kwargs.pop('align')

        # Now pass the rest of the kwargs to the base class
        super(Row, self).__init__(**kwargs)

        self.cells = []

        for arg in args:
            self.add(arg, header_flag, align=align)

    def add(self, item, header_flag=False, align=None):
        """Add a Cell to the row

        :param item: An element to add to the Cells can be list or Cell object.
        :type item: basestring, QString, list, Cell

        :param header_flag: Flag indicating it the item is a header or not.
        :type header_flag: bool

        :param align: Optional alignment qualifier for all cells in the row.
        :type align: basestring

        """

        if self._is_stringable(item) or self._is_qstring(item):
            self.cells.append(Cell(item, header=header_flag, align=align))
        elif isinstance(item, Cell):
            self.cells.append(item)
        elif isinstance(item, Image):
            self.cells.append(Cell(item))
        elif isinstance(item, list):
            for i in item:
                self.cells.append(Cell(i, header=header_flag, align=align))
        else:
            raise InvalidMessageItemError(item, item.__class__)

    def to_html(self):
        """Render a Text MessageElement as html.

        :returns: The html representation of the Text MessageElement
        :rtype: basestring

        """
        row = '<tr%s>\n' % self.html_attributes()
        for cell in self.cells:
            row += cell.to_html()
        row += '</tr>\n'

        return row

    def to_text(self):
        """Render a Text MessageElement as plain text

        :returns: The plain text representation of the row.
        :rtype: basestring
        """
        row = '---\n'
        for index, cell in enumerate(self.cells):
            if index > 0:
                row += ', '
            row += cell.to_text()
        row += '---'

        return row

    def to_dict(self):
        """Render a MessageElement as python dict

        :return: Python dict representation
        :rtype: dict
        """
        obj_dict = super(Row, self).to_dict()
        cells_dict = [c.to_dict() for c in self.cells]
        child_dict = {
            'type': self.__class__.__name__,
            'cells': cells_dict
        }
        obj_dict.update(child_dict)
        return child_dict
