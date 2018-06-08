"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Numbered List**

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

from .abstract_list import AbstractList

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class NumberedList(AbstractList):
    """A class to model free text in the messaging system."""

    def __init__(self, *args, **kwargs):
        """Creates a Text object to contain a list of Text objects

        Strings can be passed and are automatically converted in to
        item.Text()

        Args:
            Text message, an element to add to the message

        Returns:
            None

        Raises:
            Errors are propagated

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(NumberedList, self).__init__(*args, **kwargs)

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
            html = '<ol%s>\n' % self.html_attributes()
            for item in self.items:
                html += '<li>%s</li>\n' % item.to_html()
            html += '</ol>'
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
            for i, item in enumerate(self.items):
                text += ' %s. %s\n' % (i + 1, item.to_text())

            return text
