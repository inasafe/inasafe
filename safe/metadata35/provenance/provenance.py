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


from safe.metadata35.provenance import ProvenanceStep
from safe.metadata35.provenance import IFProvenanceStep


class Provenance():
    """
    Class to store a list of provenance steps.

    .. versionadded:: 3.2

    """

    def __init__(self):
        # private members
        self._steps = []

    def __str__(self):
        return str(self._steps)

    def __iter__(self):
        return iter(self._steps)

    @property
    def dict(self):
        """
        the python object for rendering json.

        It is called dict to be
        coherent with the other modules but it actually returns a list

        :return: the python object for rendering json
        :rtype: list
        """

        json_list = []
        for step in self.steps:
            json_list.append(step.dict)
        return json_list

    @property
    def xml(self):
        """
        the xml string representation.

        :return: the xml string
        :rtype: str
        """

        xml = '<inasafe_provenance>\n'
        for step in self.steps:
            xml += step.xml
        xml += '</inasafe_provenance>\n'
        return xml

    @property
    def steps(self):
        """
        the steps list.

        :return: the steps list
        :rtype: list
        """

        return self._steps

    @property
    def count(self):
        """
        the size of the list.

        :return: the size
        :rtype: int
        """
        return len(self._steps)

    @property
    def last(self):
        """
        the last step of the list.

        :return: the last step
        :rtype: ProvenanceStep
        """
        return self._steps[-1]

    def get(self, index):
        """
        the step at index position of the list.

        :return: the step at index
        :rtype: ProvenanceStep
        """
        return self._steps[index]

    def append_step(self, title, description, timestamp=None, data=None):
        """
        Append a new provenance step.

        :param title: the title of the ProvenanceStep
        :type title: str

        :param description: the description of the ProvenanceStep
        :type description: str

        :param timestamp: the time of the ProvenanceStep
        :type timestamp: datetime, None, str

        :param data: The data of the ProvenanceStep
        :type data: dict

        :returns: the time of the ProvenanceStep
        :rtype: datetime
        """
        step = ProvenanceStep(title, description, timestamp, data)
        self._steps.append(step)
        return step.time

    def append_if_provenance_step(
            self, title, description, timestamp=None, data=None):
        """Append a new IF provenance step.

        :param title: the title of the IF ProvenanceStep
        :type title: str

        :param description: the description of the IF ProvenanceStep
        :type description: str

        :param timestamp: the time of the IF ProvenanceStep
        :type timestamp: datetime, None

        :param data: The data of the IF ProvenanceStep
        :type data: dict

        :returns: the time of the IF ProvenanceStep
        :rtype: datetime
        """
        step = IFProvenanceStep(title, description, timestamp, data)
        self._steps.append(step)
        return step.time

    def append_provenance_step(self, provenance):
        """Append provenance object

        :param provenance: ProvenanceStep object
        :type provenance: ProvenanceStep
        """

        self._steps.append(provenance)
