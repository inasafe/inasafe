"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Paragraph.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from __future__ import absolute_import

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from .message_element import MessageElement
from .text import Text

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Paragraph(MessageElement):
    """A Paragraph class for text blocks much like the p in html."""

    def __init__(self, *args, **kwargs):
        """Creates a Paragraph object

        Strings can be passed and are automatically converted in to item.Text()


        :args: Text text, text to add to the message


        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Paragraph, self).__init__(**kwargs)
        self.text = Text(*args)

    def to_html(self):
        """Render a Paragraph MessageElement as html

        :returns: The html representation of the Paragraph MessageElement

        """
        if self.text is None:
            return
        else:
            return '<p%s>%s%s</p>' % (
                self.html_attributes(), self.html_icon(), self.text.to_html())

    def to_text(self):
        """Render a Paragraph MessageElement as plain text

        :returns: Plain text representation of the Paragraph MessageElement
        """
        if self.text is None:
            return
        else:
            return '    %s\n' % self.text
