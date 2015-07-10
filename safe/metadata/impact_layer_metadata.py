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
import json

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.metadata.base_metadata import BaseMetadata
from safe.metadata.provenance.provenance import Provenance


class ImpactLayerMetadata(BaseMetadata):

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        # Initialise members
        # private members
        self._provenance = Provenance()

        # public members
        self.report = None
        self.summary_data = None

        # initialize base class
        super(ImpactLayerMetadata, self).__init__(layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        metadata = super(ImpactLayerMetadata, self).dict

        metadata['provenance'] = self.provenance
        metadata['report'] = self.report
        metadata['summary_data'] = self.summary_data

        return metadata

    @property
    def json(self):
        metadata = self.dict

        provenance = []
        for step in self.provenance:
            provenance.append(step.json)
        metadata['provenance'] = provenance
        return json.dumps(metadata, indent=2, sort_keys=True)

    @property
    def xml(self):
        # TODO (MB): implement this
        xml = super(ImpactLayerMetadata, self).xml
        raise NotImplementedError('Still need to write this')

    def read_from_json(self):
        metadata = super(ImpactLayerMetadata, self).read_from_json()
        if 'provenance' in metadata:
            for provenance_step in metadata['provenance']:
                try:
                    self.append_provenance_step(
                        provenance_step['title'],
                        provenance_step['description'],
                        provenance_step['time'],
                    )
                except KeyError:
                    # we want to get as much as we can without raising errors
                    pass
        if 'report' in metadata:
            self.report = metadata['report']
        if 'summary_data' in metadata:
            self.summary_data = metadata['summary_data']

    def read_from_xml(self):
        # TODO (MB): implement this
        super(ImpactLayerMetadata, self).read_from_xml()

    @property
    # there is no setter. provenance can only grow. use append_provenance_step
    def provenance(self):
        return self._provenance

    def append_provenance_step(self, title, description, timestamp=None):
        step_time = self._provenance.append_step(title, description, timestamp)
        if step_time > self.last_update:
            self.last_update = step_time
