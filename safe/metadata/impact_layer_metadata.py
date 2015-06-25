# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **metadata module.**

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

    def __init__(self, layer):
        super(ImpactLayerMetadata, self).__init__(layer)
        # private members
        self._provenance = Provenance()

        # public members
        self.report = None
        self.summary_data = None

    @property
    # there is no setter. provenance can only grow. use append_provenance_step
    def provenance(self):
        return self._provenance

    def append_provenance_step(self, name, description):
        step_time = self._provenance.append_step(name, description)
        self.last_update = step_time

    @property
    def json(self):
        metadata = super(ImpactLayerMetadata, self).dict

        provenance = []
        for step in self.provenance:
            provenance.append(step.json)
        metadata['provenance'] = provenance
        metadata['report'] = self.report
        metadata['summary_data'] = self.summary_data

        return json.dumps(metadata, indent=2, sort_keys=True)

