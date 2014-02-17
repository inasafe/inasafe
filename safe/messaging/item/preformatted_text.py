"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Preformatted.**

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

#FIXME (MB) remove when all to_* methods are implemented
#pylint: disable=W0223


class PreformattedText(Text):
    """A representation for a preformatted text item. """

    def __init__(self, text, **kwargs):
        """Constructor.

        :param text: A string to add to the message.
        :type text: str

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        if 'style_class' in kwargs:
            my_class = '%s prettyprint' % kwargs['style_class']
            kwargs['style_class'] = my_class
        super(PreformattedText, self).__init__(**kwargs)

        self.text = text

    def to_html(self):
        """Render as html <pre> element.

        :returns: The html representation.
        :rtype: str
        """
        mytext = '<pre%s>\n%s</pre>' % (self.html_attributes(), self.text)
        return mytext

    def to_text(self):
        """Render as plain text.

        :param text: A string to add to the message.
        :type text: str

        """
        return '%s' % self.text
