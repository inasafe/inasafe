# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = 'b9e2d7536ddcf682e32a156d6d8b0dbc0bb73cc4'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from datetime import datetime


class ProvenanceStep(object):
    """
    Class to store a provenance step.

    Each step can be instantiated passing a time or it will automatically
    generate a timestamp. Each step can represent itself as xml or dict

    .. versionadded:: 3.2

    """

    def __init__(self, title, description, timestamp=None, data=None):
        # private members
        self._title = title
        self._description = description
        self._data = data
        if timestamp is None:
            self._time = datetime.now()
        elif isinstance(timestamp, datetime):
            self._time = timestamp
        elif isinstance(timestamp, basestring):
            self._time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            raise RuntimeError('The timestamp %s has an invalid type (%s)',
                               timestamp, type(timestamp))

    def __str__(self):
        """
        the string representation.

        :return: the string representation
        :rtype: str
        """
        # RMN:
        # FIXME: Mismatched arguments. Should we delete the extra tags?
        # pylint: disable=too-many-format-args
        return "%s: %s\n%s" % (
            self.time, self.title, self.description, self.data)

    @property
    def title(self):
        """
        the title.

        :return: the title
        :rtype: str
        """

        return self._title

    @property
    def description(self):
        """
        the description.

        :return: the description
        :rtype: str
        """

        return self._description

    @property
    def time(self):
        """
        the time.

        :return: the time
        :rtype: datetime
        """

        return self._time

    def data(self, key=None):
        """
        additional data stored in the step.

        :param key: The name of a key stored in the data
        :type key: str
        :return: the stored data
        :rtype: dict
        """
        if key is None:
            return self._data
        else:
            return self._data[key]

    @property
    def dict(self):
        """
        the dict representation.

        :return: the dict
        :rtype: dict
        """

        return {
            'title': self.title,
            'description': self.description,
            'time': self.time.isoformat(),
            'data': self.data()
        }

    @property
    def xml(self):
        """
        the xml string representation.

        :return: the xml
        :rtype: str
        """

        return self._get_xml()

    def _get_xml(self, close_tag=True):
        """
        generate the xml string representation.

        :param close_tag: should the '</provenance_step>' tag be added or not.
        :type close_tag: bool

        :return: the xml
        :rtype: str
        """

        xml = (
            '<provenance_step timestamp="%s">\n'
            '<title>%s</title>\n'
            '<description>%s</description>\n'
            )
        if close_tag:
            xml += '</provenance_step>\n'

        return xml % (self.time.isoformat(), self.title, self.description)
