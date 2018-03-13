"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Paragraph.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '28/05/2013'
__copyright__ = ('Copyright 2015, Australia Indonesia Facility for '
                 'Disaster Reduction')

# TODO: I don't really like importing this here as it breaks the modularity of
# TODO: messaging. TS
from safe.utilities.resources import (
    resources_path,
    resource_url)
from text import Text


class Brand(Text):

    """A class to model the inasafe brand.

    .. versionadded: 3.2
    """

    def __init__(self, **kwargs):
        """Creates a brand element.

        For HTML, it will insert a div with class 'branding' - use css to
        set the style of that div as you want it.

        For text, it will create a plain text brand e.g.

        **** InaSAFE - http://inasafe.org ****

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Brand, self).__init__(**kwargs)

    def to_html(self):
        """Render as html.
        """
        uri = resource_url(
            resources_path('img', 'logos', 'inasafe-logo-white.png'))
        snippet = (
            '<div class="branding">'
            '<img src="%s" title="%s" alt="%s" %s/></div>') % (
                uri,
                'InaSAFE',
                'InaSAFE',
                self.html_attributes())
        return snippet

    def to_text(self):
        """Render as plain text.
        """
        return ''

    def to_markdown(self):
        return '# **** InaSAFE - http://inasafe.org ****'

    def to_json(self):
        pass
