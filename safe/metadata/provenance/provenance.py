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


from safe.metadata.provenance import ProvenanceStep


class Provenance(object):

    def __init__(self):
        # private members
        self._steps = []

    def __str__(self):
        return str(self._steps)

    def __iter__(self):
        return iter(self._steps)

    @property
    def json(self):
        json = []
        for step in self.steps:
            json.append(step.json)
        return json

    @property
    def xml(self):
        xml = '<inasafe_provenance>'
        for step in self.steps:
            xml += step.xml
        xml += '</inasafe_provenance>'
        return xml

    @property
    def steps(self):
        return self._steps

    @property
    def count(self):
        return len(self._steps)

    @property
    def last(self):
        return self._steps[-1]

    def get(self, index):
        return self._steps[index]

    def append_step(self, title, description, timestamp=None):
        step = ProvenanceStep(title, description, timestamp)
        self._steps.append(step)
        return step.time
