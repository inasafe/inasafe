# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Message Element.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
import json

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class MessageElement(object):

    def __init__(
            self,
            element_id=None,
            style_class=None,
            icon=None,
            attributes=None):
        """
        Constructor for a message element
        :param element_id: Optional id - will be ignored in text renderer.
        :param style_class: Optional class = will be ignored in text renderer.

        :param icon: Optional bootstrap glyph icon class used for html renderer
        :param attributes: Optional html attributes you can add to an element.

        :return: None

        For glyphicons see http://twitter.github.io/bootstrap/base-css
        .html#icons

        e.g. icon='icon-search' when used will cause self.html_icon to return
         <i class="icon-search"></i>

        You can use the attributes flag  to pass any arbitrary html
        attributes to the generated html. e.g.

        Text('foo', attributes='width: "100%"')

        """
        self.element_id = element_id
        self.style_class = style_class
        self.icon = icon
        self.attributes = attributes

    def __unicode__(self):
        return self.to_text()

    def __str__(self):
        return self.__unicode__()

    @staticmethod
    def _is_qstring(message):
        """Check if its a QString without adding any dep to PyQt4."""
        my_class = str(message.__class__)
        my_class_name = my_class.replace('<class \'', '').replace('\'>', '')
        if my_class_name == 'PyQt4.QtCore.QString':
            return True

        return False

    @staticmethod
    def _is_stringable(message):
        return (isinstance(message, basestring) or
                isinstance(message, int) or
                isinstance(message, long) or
                isinstance(message, float))

    def to_html(self):
        """Render a MessageElement queue as html

        :returns: Html representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')

    def to_text(self):
        """Render a MessageElement queue as text

        :returns: Text representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')

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
        return {
            'type': self.__class__.__name__,
            'element_id': self.element_id,
            'style_class': self.style_class,
            'icon': self.icon,
            'attributes': self.attributes
        }

    def to_json(self):
        """Render a MessageElement queue as JSON

        :returns: Json representation of the Text MessageElement.
        :rtype: str
        """
        return json.dumps(self.to_dict())

    def html_attributes(self):
        """Get extra html attributes such as id and class."""
        extra_attributes = ''
        if self.element_id is not None:
            extra_attributes = ' id="%s"' % self.element_id
        if self.style_class is not None:
            extra_attributes = '%s class="%s"' % (
                extra_attributes, self.style_class)
        if self.attributes is not None:
            extra_attributes = '%s %s' % (extra_attributes, self.attributes)
        return extra_attributes

    def html_icon(self):
        """Get bootstrap style glyphicon.

        For glyphicons see http://twitter.github.io/bootstrap/base-css
        .html#icons

        e.g. icon='icon-search' when used will cause self.html_icon to return
         <i class="icon-search"></i>

        """
        icon = ''
        if self.icon is not None:
            icon = '<i class="%s"></i> ' % self.icon
        return icon
