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

from message_element import MessageElement
from exceptions import InvalidMessageItemError
from text import PlainText


class AbstractList(MessageElement):
    """A class to model free text in the messaging system """

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
        super(AbstractList, self).__init__(**kwargs)

        self.items = []

        for item in args:
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
        if isinstance(item, basestring) or self._is_qstring(item):
            self.items.append(PlainText(item))
        elif isinstance(item, MessageElement):
            self.items.append(item)
        else:
            raise InvalidMessageItemError(item, item.__class__)

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
