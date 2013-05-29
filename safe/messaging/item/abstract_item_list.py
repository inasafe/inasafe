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

from message_element import MessageElement, InvalidMessageItemError
from text import PlainText


class AbstractItemList(MessageElement):
    """A class to model free text in the messaging system """

    def __init__(self, ordered, items):
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
        self.ordered = ordered
        self.items = []

        for item in items:
            self.add(item)

    def add(self, item):
        """add a Text MessageElement to the existing Text

        Strings can be passed and are automatically converted in to
        item.Text()

        Args:
            Text text, an element to add to the text

        Returns:
            None

        Raises:
            Errors are propagated
        """
        if isinstance(item, basestring):
            self.items.append(PlainText(item))
        elif isinstance(item, MessageElement):
            self.items.append(item)
        else:
            raise InvalidMessageItemError

    def to_html(self):
        """Render a Text MessageElement as html

        Args:
            None

        Returns:
            Str the html representation of the Text MessageElement

        Raises:
            Errors are propagated
        """
        raise NotImplementedError('Please don\'t use this class directly')

    def to_text(self):
        """Render a Text MessageElement as plain text

        Args:
            None

        Returns:
            Str the plain text representation of the Text MessageElement

        Raises:
            Errors are propagated
        """
        raise NotImplementedError('Please don\'t use this class directly')