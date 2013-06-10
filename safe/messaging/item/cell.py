"""
InaSAFE Disaster risk assessment tool developed by AusAid - **ItemList module.**

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
from text import Text


class Cell(MessageElement):
    """A class to model table cells in the messaging system """

    def __init__(self, *args, **kwargs):
        """Creates a cell object

        Args:
            text can be Text object or string

        Returns:
            None

        Raises:
            Errors are propagated

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Cell, self).__init__(**kwargs)

        self.text = Text(*args)

    def to_html(self):
        """Render a Cell MessageElement as html

        Args:
            None

        Returns:
            Str the html representation of the Cell MessageElement

        Raises:
            Errors are propagated
        """
        return '<td%s>%s</td>\n' % (
            self.html_attributes(), self.text.to_html())

    def to_text(self):
        """Render a Cell MessageElement as plain text

        Args:
            None

        Returns:
            Str the plain text representation of the Cell MessageElement

        Raises:
            Errors are propagated
        """
        return '%s' % self.text
