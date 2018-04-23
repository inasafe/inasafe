# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Cell.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""


__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '04/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from .message_element import MessageElement
from .text import Text

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Cell(MessageElement):
    """A class to model table cells in the messaging system."""

    def __init__(self, *args, **kwargs):
        """Creates a cell object

        :param: Text can be Text object or string

        :param header: A flag to indicate if the cell should be treated as
            a header cell. Depending on the ouput format cells may be rendered
            differently e.g. with bold text.
        :type header: bool

        :param span: The number of columns this cell should span. If not
            specified it will span 1 column only. Note that if the renderer
            does not support column spanning this option will be ignored.
        :type span: int

        :param align: A flag to indicate if special alignment should
            be given to cells if supported in the output renderer.
            Valid options are: None, 'left', 'right', 'center'
        :type align: basestring

        :param wrap_slash: Whether to replace slashes with the slash plus the
            html <wbr> tag which will help to e.g. wrap html in small cells if
            it contains a long filename. Disabled by default as it may cause
            side effects if the text contains html markup. Only affects
            to_html calls.
        :type wrap_slash: bool

        We pass the kwargs on to the base class after first removing the
        kwargs that we explicitly expect here so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        # First check if we get a header keyword arg. If we do we will
        # Format each cell with important_text, th or whatever is appropriate.
        self.header_flag = False
        if 'header' in kwargs:
            self.header_flag = kwargs['header']
            # dont pass the kw on to the base class as we handled it here
            kwargs.pop('header')

        # Also check for column spanning
        self.span = 1
        if 'span' in kwargs:
            self.span = kwargs['span']
            # dont pass the kw on to the base class as we handled it here
            kwargs.pop('span')

        # Also check if align parameter is called before calling the ABC
        self.align = None
        if 'align' in kwargs:
            if kwargs['align'] in [None, 'left', 'right', 'center']:
                self.align = kwargs['align']
            # dont pass the kw on to the base class as we handled it here
            kwargs.pop('align')

        # Check if slashes should be wrapped for html
        self.wrap_slash = False
        if 'wrap_slash' in kwargs:
            self.wrap_slash = kwargs['wrap_slash']
            # don't pass the kw on to the base class as we handled it here
            kwargs.pop('wrap_slash')

        super(Cell, self).__init__(**kwargs)

        # Special case for when we want to put a nested table in a cell
        # We don't use isinstance because of recursive imports with table
        class_name = args[0].__class__.__name__
        if class_name in ['BulletedList', 'Table', 'Message']:
            self.content = args[0]
        else:
            self.content = Text(*args)

    def to_html(self):
        """Render a Cell MessageElement as html

        :returns: The html representation of the Cell MessageElement
        :rtype: basestring
        """
        # Apply bootstrap alignment classes first
        if self.align is 'left':
            if self.style_class is None:
                self.style_class = 'text-left'
            else:
                self.style_class += ' text-left'
        elif self.align is 'right':
            if self.style_class is None:
                self.style_class = 'text-right'
            else:
                self.style_class += ' text-right'
        elif self.align is 'center':
            if self.style_class is None:
                self.style_class = 'text-center'
            else:
                self.style_class += ' text-center'

        # Special case for when we want to put a nested table in a cell
        # We don't use isinstance because of recursive imports with table
        class_name = self.content.__class__.__name__
        if class_name in ['BulletedList', 'Table', 'Image', 'Message']:
            html = self.content.to_html()
        else:
            html = self.content.to_html(wrap_slash=self.wrap_slash)

        # Check if we have a header or not then render
        if self.header_flag is True:
            return '<th%s colspan=%i>%s</th>\n' % (
                self.html_attributes(), self.span, html)
        else:
            return '<td%s colspan=%i>%s</td>\n' % (
                self.html_attributes(), self.span, html)

    def to_text(self):
        """Render a Cell MessageElement as plain text.

        :returns: The plain text representation of the Cell MessageElement.
        :rtype: basestring

        """
        if self.header_flag is True:
            return '**%s**' % self.content
        else:
            return '%s' % self.content

    def to_markdown(self):
        """Render a MessageElement queue as markdown

        :returns: Markdown representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')

    def to_dict(self):
        """Render a MessageElement as python dict

        :return: Python dict representation
        :rtype: dict
        """
        obj_dict = super(Cell, self).to_dict()
        child_dict = {
            'type': self.__class__.__name__,
            'header_flag': self.header_flag,
            'align': self.align,
            'wrap_slash': self.wrap_slash,
            'content': self.content.to_dict()
        }
        obj_dict.update(child_dict)
        return obj_dict
