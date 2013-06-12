"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Row**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '04/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from message_element import MessageElement
from exceptions import InvalidMessageItemError
from cell import Cell

#FIXME (MB) remove when all to_* methods are implemented
#pylint: disable=W0223


class Row(MessageElement):
    """A class to model table rows in the messaging system """

    def __init__(self, *args, **kwargs):
        """Creates a row object

        Args:
            args can be list or Cell

        Returns:
            None

        Raises:
            Errors are propagated

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Row, self).__init__(**kwargs)
        self.cells = []

        for arg in args:
            self.add(arg)

    def add(self, item):
        """add a Cell to the row

        list can be passed and are automatically converted to Cell

        Args:
            item an element to add to the Cells can be list or Cell object

        Returns:
            None

        Raises:
            Errors are propagated
        """

        if isinstance(item, basestring) or self._is_qstring(item):
            self.cells.append(Cell(item))
        elif isinstance(item, Cell):
            self.cells.append(item)
        elif isinstance(item, list):
            for i in item:
                self.cells.append(Cell(i))
        else:
            raise InvalidMessageItemError(item, item.__class__)

    def to_html(self):
        """Render a Text MessageElement as html

        Args:
            None

        Returns:
            Str the html representation of the Text MessageElement

        Raises:
            Errors are propagated
        """
        row = '<tr%s>\n' % self.html_attributes()
        for cell in self.cells:
            row += cell.to_html()
        row += '</tr>\n'

        return row

    def to_text(self):
        """Render a Text MessageElement as plain text

        Args:
            None

        Returns:
            Str the plain text representation of the Text MessageElement

        Raises:
            Errors are propagated
        """
        row = '---\n'
        for cell in self.cells:
            row += cell
        row += '---'

        return row
