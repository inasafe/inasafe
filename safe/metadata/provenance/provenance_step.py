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
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from datetime import datetime


class ProvenanceStep(object):
    """
    Class to store a provenance step.

    Each step can be instantiated passing a time or it will automatically
    generate a timestamp. Each step can represent itself as xml or json

    .. versionadded:: 3.2

    """

    def __init__(self, title, description, timestamp=None):
        # private members
        self._title = title
        self._description = description
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

        return "%s: %s\n%s" % (self._time, self._title, self._description)

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

    @property
    def json(self):
        """
        the json representation.

        :return: the json
        :rtype: dict
        """

        return {
            'title': self.title,
            'description': self.description,
            'time': self.time.isoformat(),
        }

    @property
    def xml(self):
        """
        the xml string representation.

        :return: the xml
        :rtype: str
        """

        xml = (
            '<provenance_step timestamp="%s">'
            '<title>%s</title>'
            '<description>%s</description>'
            '</provenance_step>')
        return xml % (self.time.isoformat(), self.title, self.description)
