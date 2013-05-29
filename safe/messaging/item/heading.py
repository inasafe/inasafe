"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Title Module.**

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

import logging
from message_element import MessageElement, InvalidMessageItemError
from text import Text


LOGGER = logging.getLogger('InaSAFE')
#from pydev import pydevd


class Heading(MessageElement):
    """A Heading class for titles and subtitles much like the h1-h6 in html"""

    def __init__(self, text=None, level=1):
        """Creates a Heading object

        Strings can be passed and are automatically converted in to
        item.Text()

        Args:
            Text text, text to add to the message
            int level, the heading level in html 1-6 in plain text 1-...

        Returns:
            None

        Raises:
            Errors are propagated
        """
        self.text = None
        if level < 1:
            level = 1
        self.level = level

        if text is not None:
            if isinstance(text, basestring):
                self.text = Text(text)
            elif isinstance(text, Text):
                self.text = text
            else:
                raise InvalidMessageItemError

    def to_html(self):
        """Render a Heading MessageElement as html

        Args:
            None

        Returns:
            Str the html representation of the Heading MessageElement

        Raises:
            Errors are propagated
        """
        if self.text is None:
            return

        level = self.level
        if level > 6:
            level = 6
        return '<h%s>%s</h%s>' % (level, self.text.to_html(), level)

    def to_text(self):
        """Render a Heading MessageElement as plain text

        Args:
            None

        Returns:
            Str the plain text representation of the Heading MessageElement

        Raises:
            Errors are propagated
        """
        if self.text is None:
            return

        level = '*' * self.level
        return '%s%s\n' % (level, self.text)
