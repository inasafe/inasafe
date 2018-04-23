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

from .exceptions import InvalidMessageItemError

from .message_element import MessageElement
from .text import Text


# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Heading(MessageElement):
    """A Heading class for titles and subtitles much like the h1-h6 in html"""

    def __init__(self, text=None, level=1, **kwargs):
        """Creates a Heading object

        Strings can be passed and are automatically converted in to
        item.Text()

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python


        :param text: Text to add to the message as a heading.
        :type text: basestring

        :param level: The heading level in html 1-6 in plain text 1-...
        :type level: int

        :returns: None
        """
        super(Heading, self).__init__(**kwargs)

        self.text = None
        if level < 1:
            level = 1
        self.level = level

        if text is not None:
            if self._is_stringable(text) or self._is_qstring(text):
                self.text = Text(text)
            elif isinstance(text, Text):
                self.text = text
            else:
                raise InvalidMessageItemError(text, text.__class__)

    def to_html(self):
        """Render a Heading MessageElement as html

        :returns: The html representation of the Heading MessageElement.
        :rtype: str
        """
        if self.text is None:
            return

        level = self.level
        if level > 6:
            level = 6
        return '<h%s%s><a id="%s"></a>%s%s</h%s>' % (
            level,
            self.html_attributes(),
            self.element_id,
            self.html_icon(),
            self.text.to_html(),
            level)

    def to_text(self):
        """Render a Heading MessageElement as plain text

        :returns: The plain text representation of the Heading MessageElement.
        """
        if self.text is None:
            return

        level = '*' * self.level
        return '%s%s\n' % (level, self.text)
