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
__date__ = '24/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from abstract_list import AbstractList


class UnorderedList(AbstractList):
    """A class to model free text in the messaging system """

    def __init__(self, *args):
        """Creates a Text object to contain a list of Text objects

        Strings can be passed and are automatically converted in to
        item.Text()

        Args:
            Text message, an element to add to the message

        Returns:
            None

        Raises:
            Errors are propagated
        """
        AbstractList.__init__(self, True, args)

    def to_html(self):
        """Render a Text MessageElement as html

        Args:
            None

        Returns:
            Str the html representation of the Text MessageElement

        Raises:
            Errors are propagated
        """
        if self.items is None:
            return
        else:
            html = '<ul>\n'
            for item in self.items:
                html += '<li>%s</li>\n' % item.to_html()
            html += '</ul>'
            return html

    def to_text(self):
        """Render a Text MessageElement as plain text

        Args:
            None

        Returns:
            Str the plain text representation of the Text MessageElement

        Raises:
            Errors are propagated
        """
        if self.items is None:
            return
        else:
            text = ''
            for item in self.items:
                text += ' - %s\n' % item.to_text()

            return text