# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Cell.**

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
from bulleted_list import BulletedList

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Cell(MessageElement):
    """A class to model table cells in the messaging system """

    def __init__(self, *args, **kwargs):
        """Creates a cell object

        :param: Text can be Text object or string


        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Cell, self).__init__(**kwargs)

        # Special case for when we want to put a nested table in a cell
        class_name = args[0].__class__.__name__
        if class_name in ['BulletedList', 'Table']:
            self.content = args[0]
        else:
            self.content = Text(*args)

    def to_html(self):
        """Render a Cell MessageElement as html

        :returns: The html representation of the Cell MessageElement
        :rtype: basestring
        """
        return '<td%s>%s</td>\n' % (
            self.html_attributes(), self.content.to_html())

    def to_text(self):
        """Render a Cell MessageElement as plain text

        :returns: The plain text representation of the Cell MessageElement.
        :rtype: basestring

        """
        return '%s' % self.content

    def to_markdown(self):
        """Render a MessageElement queue as markdown

        :returns: Markdown representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')

    def to_json(self):
        """Render a MessageElement queue as JSON

        :returns: Json representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')
