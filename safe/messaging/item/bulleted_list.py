"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Bulleted List**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from __future__ import absolute_import

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '24/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from .abstract_list import AbstractList

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class BulletedList(AbstractList):
    """A class to model free text in the messaging system."""

    def __init__(self, bullet_style=None, *args, **kwargs):
        """Creates a Text object to contain a list of Text objects

        Strings can be passed and are automatically converted in to
        item.Text()

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(BulletedList, self).__init__(*args, **kwargs)
        self.bullet_style = bullet_style

    def to_html(self):
        """Render a Text MessageElement as html.

        :returns: The html representation of the Text MessageElement
        :rtype: basestring
        """

        if self.items is None:
            return
        else:
            html = '<ul%s>\n' % self.html_attributes()
            for item in self.items:
                if self.bullet_style:
                    html += '<li class="%s">%s</li>\n' % (
                        self.bullet_style, item.to_html())
                else:
                    html += '<li>%s</li>\n' % item.to_html()
            html += '</ul>'
            return html

    def to_text(self):
        """Render a Text MessageElement as plain text.

        :returns: The plain text representation of the Text MessageElement.
        :rtype: basestring
        """
        if self.items is None:
            return
        else:
            text = ''
            for item in self.items:
                text += ' - %s\n' % item.to_text()

            return text
