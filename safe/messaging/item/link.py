"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Paragraph.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '28/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from text import Text

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Link(Text):
    """A class to model emphasized text in the messaging system."""

    def __init__(self, uri, text=None, **kwargs):
        """Creates a Emphasized Text Text object

        Args:
            String message, a string to add to the message

        Returns:
            None

        Raises:
            Errors are propagated

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Link, self).__init__(**kwargs)
        self.uri = uri
        self.text = text

    def to_html(self):
        """Render as html

        Args:
            None

        Returns:
            Str the html representation

        Raises:
            Errors are propagated
        """

        text = self.text
        if text is None:
            text = self.uri
        return '<a href="%s"%s>%s</a>' % (
            self.uri, self.html_attributes(), text)

    def to_text(self):
        """Render as plain text

        Args:
            None

        Returns:
            Str the plain text representation

        Raises:
            Errors are propagated
        """
        if self.text is None:
            return '::%s' % self.uri
        return '::%s [%s]' % (self.text, self.uri)
