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
__date__ = '28/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from .text import Text

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class ImportantText(Text):
    """A class to model free text in the messaging system."""

    def __init__(self, text, **kwargs):
        """Creates a Bold Text object

        :param text: A string to add to the message.
        :type text: str

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(ImportantText, self).__init__(**kwargs)
        self.text = text

    def to_html(self):
        """Render as html.

        :returns: The html representation.
        :rtype: str
        """
        return '<strong%s>%s%s</strong>' % (
            self.html_attributes(), self.html_icon(), self.text)

    def to_text(self):
        """Render as plain text

        :returns: The Text representation.
        :rtype: str
        """
        return '*%s*' % self.text
