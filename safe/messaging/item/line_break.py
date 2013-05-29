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


class LineBreak(Text):
    """A class to model line breaks in text the messaging system """

    def to_html(self):
        """Render as html

        Args:
            None

        Returns:
            Str the html representation

        Raises:
            Errors are propagated
        """
        return '<br/>\n'

    def to_text(self):
        """Render as plain text

        Args:
            None

        Returns:
            Str the plain text representation

        Raises:
            Errors are propagated
        """
        return '\n'
