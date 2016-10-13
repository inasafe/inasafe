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


class HorizontalRule(Text):
    """A class to model horizontal rules in text the messaging system """

    def to_markdown(self):
        """Render as markdown

        :returns: the markdown representation (<hr>)
        :rtype: str

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        return '---\n'

    def to_html(self, **kwargs):
        """Render as html

        :returns: the html representation (<hr>)
        :rtype: str

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(HorizontalRule, self).__init__(**kwargs)
        return '<hr%s/>\n' % self.html_attributes()

    def to_text(self):
        """Render as plain text

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        return '----------------------------------------\n'
