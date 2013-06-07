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
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from paragraph import Paragraph, Text


class SuccessParagraph(Paragraph):
    """A Success Paragraph class for text blocks much like the p in html."""

    def __init__(self, *args, **kwargs):
        """Creates an important paragraph object.

        Args:
            String text, a string to add to the message

        Returns:
            None

        Raises:
            Errors are propagated

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        if 'style_class' in kwargs:
            my_class = '%s alert alert-success' % kwargs['style_class']
            kwargs['style_class'] = my_class
        super(SuccessParagraph, self).__init__(**kwargs)
        self.text = Text(*args)

    def to_html(self):
        """Render a Paragraph MessageElement as html

        Args:
            None

        Returns:
            Str the html representation of the Paragraph MessageElement

        Raises:
            Errors are propagated
        """
        if self.text is None:
            return
        else:
            return '<p>%s</p>' % self.text.to_html()

    def to_text(self):
        """Render a Paragraph MessageElement as plain text

        Args:
            None

        Returns:
            Str the plain text representation of the Paragraph MessageElement

        Raises:
            Errors are propagated
        """
        if self.text is None:
            return
        else:
            return "    SUCCESS: %s\n" % self.text
