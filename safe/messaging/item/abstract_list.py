"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Abstract List**

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

from .exceptions import InvalidMessageItemError

from .message_element import MessageElement
from safe.utilities.i18n import tr
from .text import PlainText


class AbstractList(MessageElement):
    """A class to model free text in the messaging system."""

    def __init__(self, *args, **kwargs):
        """Creates a Text object to contain a list of Text objects

        Strings can be passed and are automatically converted in to
        item.Text()

        :param: Text message, an element to add to the message

        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        super(AbstractList, self).__init__(**kwargs)

        self.items = []

        for item in args:
            self.add(item)

    def add(self, item):
        """add a Text MessageElement to the existing Text

        Strings can be passed and are automatically converted in to
        item.Text()

        :param item: Text text, an element to add to the text

        """
        if self._is_stringable(item) or self._is_qstring(item):
            self.items.append(PlainText(item))
        elif isinstance(item, MessageElement):
            self.items.append(item)
        elif item is None or (hasattr(item, 'isNull') and item.isNull()):
            self.items.append(PlainText(
                tr('Null (None) found from the data.')))
        elif isinstance(item, tuple) or isinstance(item, list):
            for i in item:
                # Recursive call
                self.add(i)
        else:
            raise InvalidMessageItemError(item, item.__class__)

    def is_empty(self):
        """Helper to see if this message is empty."""
        if not len(self.items):
            return True
        else:
            return False

    def to_html(self):
        """Render a Text MessageElement as html

        :returns: The html representation of the Text MessageElement.
        """
        raise NotImplementedError('Please don\'t use this class directly')

    def to_text(self):
        """Render a Text MessageElement as plain text

        :returns: plain text representation of the Text MessageElement

        """
        raise NotImplementedError('Please don\'t use this class directly')
