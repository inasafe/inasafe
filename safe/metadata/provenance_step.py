# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **metadata module.**

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

    def __init__(self, title, description):
        # private members
        self._title = title
        self._description = description
        self._time = datetime.now()

    def __str__(self):
        return "%s: %s\n%s" % (self._time, self._title, self._description)

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def time(self):
        return self._time
