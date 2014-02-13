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

import os
from message_element import MessageElement
from exceptions import InvalidMessageItemError

#FIXME (MB) remove when all to_* methods are implemented
#pylint: disable=W0223


class Text(MessageElement):
    """free text in the messaging with automatically added whitespaces"""

    def __init__(self, *args, **kwargs):
        """Creates a Text object to contain a list of Text objects

        Strings can be passed and are automatically converted in to
        item.Text().

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(Text, self).__init__(**kwargs)
        self.text = []

        for text in args:
            self.add(text)

    def add(self, text):
        """add a Text MessageElement to the existing Text

        Strings can be passed and are automatically converted in to
        item.Text()

        :param text: An element to add to the text.
        :type text: str
        """
        if self._is_stringable(text) or self._is_qstring(text):
            self.text.append(PlainText(text))
        elif isinstance(text, Text):
            self.text.append(text)
        else:
            raise InvalidMessageItemError(text, text.__class__)

    def to_html(self):
        """Render a Text MessageElement as html.

        :returns: Html representation of the Text MessageElement.
        :rtype: str

        """
        if self.text is None:
            return
        else:
            text = ''
            for t in self.text:
                text += t.to_html() + ' '
            return ' '.join(text.split())

    def to_text(self):
        """Render a Text MessageElement as plain text

        :returns: Text representation of the Text MessageElement.
        :rtype: str
        """
        if self.text is None:
            return
        else:
            text = ''
            for t in self.text:
                text += t.to_text() + ' '
            return ' '.join(text.split())


class PlainText(Text):
    """A class to model free text in the messaging system

    We broke our 'one class per file' here because having it as a
    separate file was creating import problems due to a circular references.
    """

    def __init__(self, text, **kwargs):
        """Creates a strong Text object

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
        super(PlainText, self).__init__(**kwargs)
        if self._is_stringable(text) or self._is_qstring(text):
            self.text = str(text)
        else:
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
        icon = self.html_icon()
        attributes = self.html_attributes()
        # Deal with long file names that prevent wrapping
        wrappable_text = self.to_text().replace(os.sep, '<wbr>' + os.sep)
        if icon is not '' and attributes is not '':
            return '<span%s>%s%s</span>' % (attributes, icon, wrappable_text)
        else:
            return self.to_text()

    def to_text(self):
        """Render as plain text

        Args:
            None

        Returns:
            Str the plain text representation

        Raises:
            Errors are propagated
        """
        return self.text
