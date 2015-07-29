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

import json
from xml.etree import ElementTree

from safe.metadata import BaseMetadata
from safe.metadata.provenance import Provenance
from safe.metadata.utils import reading_ancillary_files, XML_NS


class ImpactLayerMetadata(BaseMetadata):

    # remember to add an attribute or a setter property with the same name
    _special_properties = {
        'provenance': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe_provenance')
    }

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        # Initialise members
        # private members
        self._provenance = Provenance()

        # public members
        self.summary_data = None

        # initialize base class
        super(ImpactLayerMetadata, self).__init__(layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        metadata = super(ImpactLayerMetadata, self).dict

        metadata['provenance'] = self.provenance
        metadata['summary_data'] = self.summary_data

        return metadata

    @property
    def json(self):
        metadata = self.dict

        metadata['provenance'] = self.provenance.json
        return json.dumps(metadata, indent=2, sort_keys=True)

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
        if 'summary_data' in metadata:
            self.summary_data = metadata['summary_data']

    @property
    def xml(self):
        root = super(ImpactLayerMetadata, self).xml
        provenance_path = self._special_properties['provenance']
        provenance_element = root.find(provenance_path, XML_NS)
        if provenance_element is not None:
            provenance_parent = provenance_element.getparent()
            provenance_parent.remove(provenance_element)
        else:
            provenance_parent = '/'.join(provenance_path.split('/')[:-1])
            provenance_parent = root.find(provenance_parent, XML_NS)

        provenance_element = ElementTree.fromstring(self.provenance.xml)
        provenance_parent.append(provenance_element)
        return ElementTree.tostring(root)

    def read_from_xml(self):
        with reading_ancillary_files(self):
            root = super(ImpactLayerMetadata, self).read_from_xml()
            self._read_provenance_from_xml(root)

    def _read_provenance_from_xml(self, root):
        path = self._special_properties['provenance']
        provenance = root.find(path, XML_NS)
        for step in provenance.iter('provenance_step'):
            title = step.find('title').text
            description = step.find('description').text
            timestamp = step.get('timestamp')

            self.append_provenance_step(title, description, timestamp)

    @property
    # there is no setter. provenance can only grow. use append_provenance_step
    def provenance(self):
        return self._provenance

    def append_provenance_step(self, title, description, timestamp=None):
        step_time = self._provenance.append_step(title, description, timestamp)
        if step_time > self.last_update:
            self.last_update = step_time
