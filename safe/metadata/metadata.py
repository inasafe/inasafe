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

# using this approach:
# http://eli.thegreenplace.net/2009/02/06/getters-and-setters-in-python

from datetime import datetime
import json
import os

from safe.metadata.utils import TYPE_CONVERSIONS
from safe.metadata.provenance import Provenance


class Metadata(object):

    def __init__(self, layer):
        # private members
        self._layer = layer
        self._last_update = datetime.now()
        self._provenance = Provenance()
        self._xml_properties = {}

    @property
    # there is no setter because the layer should not change overtime
    def layer(self):
        return self._layer

    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, time):
        self._last_update = time

    def set_last_update_to_now(self):
        self._last_update = datetime.now()

    @property
    # there is no setter. provenance can only grow. use append_provenance_step
    def provenance(self):
        return self._provenance

    @property
    # there is no setter. use the appropriate setter for each property or set()
    def properties(self):
        return self._xml_properties

    def get(self, xml_property_name):
        return self._xml_properties[xml_property_name].xml_value

    def get_property(self, xml_property_name):
        return self._xml_properties[xml_property_name]

    def update(self, name, value):
        self.get_property(name).value = value

    def set(self, name, value, xml_path, xml_type):
        # check if the desired type is supported
        try:
            property_class = TYPE_CONVERSIONS[xml_type]
        except KeyError:
            raise KeyError('The xml type %s is not supported yet' % xml_type)

        metadata_property = property_class(name, value, xml_path, xml_type)
        self._xml_properties[name] = metadata_property
        self.set_last_update_to_now()

    def append_provenance_step(self, name, description):
        step_time = self._provenance.append_step(name, description)
        self.last_update = step_time

    def xml(self):
        # TODO (MB): implement this
        raise NotImplementedError('Still need to write this')

    def json(self):
        metadata_json = {'layer': self.layer}

        provenance = []
        for step in self.provenance:
            provenance.append(step.json)
        metadata_json['provenance'] = provenance

        properties = {}
        for name, property in self.properties.iteritems():
            properties[name] = property.json
        metadata_json['properties'] = properties
        return json.dumps(metadata_json, indent=2, sort_keys=True)

    def write(self, destination_path):
        file_format = os.path.splitext(destination_path)[1]
        if file_format == '.json':
            metadata = self.json()
        elif file_format == '.xml':
            metadata = self.xml()
        else:
            raise TypeError('The requested file type (%s) is not yet supported'
                            % file_format)
        with open(destination_path, 'w') as f:
            f.write(metadata)

    # Standard XML properties
    @property
    def organisation(self):
        return self.get('organisation')

    @organisation.setter
    def organisation(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:contact/'
                'gmd:CI_ResponsibleParty/'
                'gmd:organisationName')
        return self.set('organisation', value, path, 'gco:CharacterString')

    @property
    def email(self):
        return self.get('email')

    @email.setter
    def email(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:contact/'
                'gmd:CI_ResponsibleParty/'
                'gmd:contactInfo/'
                'gmd:CI_Contact/'
                'gmd:address/'
                'gmd:CI_Address/'
                'gmd:electronicMailAddress')
        return self.set('email', value, path, 'gco:CharacterString')

    @property
    def document_date(self):
        return self.get('document_date')

    @document_date.setter
    def document_date(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:dateStamp')
        return self.set('document_date', value, path, 'gco:Date')

    @property
    def abstract(self):
        return self.get('abstract')

    @abstract.setter
    def abstract(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:identificationInfo/'
                'gmd:MD_DataIdentification/'
                'gmd:abstract')
        return self.set('abstract', value, path, 'gco:CharacterString')

    @property
    def title(self):
        return self.get('title')

    @title.setter
    def title(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:identificationInfo/'
                'gmd:MD_DataIdentification/'
                'gmd:citation/'
                'gmd:CI_Citation/'
                'gmd:title')
        return self.set('title', value, path, 'gco:CharacterString')

    @property
    def license(self):
        return self.get('license')

    @license.setter
    def license(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:identificationInfo/'
                'gmd:MD_DataIdentification/'
                'gmd:resourceConstraints/'
                'gmd:MD_Constraints/'
                'gmd:useLimitation')
        return self.set('license', value, path, 'gco:CharacterString')

    @property
    def url(self):
        return self.get('url')

    @url.setter
    def url(self, value):
        path = ('gmd:MD_Metadata/'
                'gmd:distributionInfo/'
                'gmd:MD_Distribution/'
                'gmd:transferOptions/'
                'gmd:MD_DigitalTransferOptions/'
                'gmd:onLine/'
                'gmd:CI_OnlineResource/'
                'gmd:linkage')
        return self.set('url', value, path, 'gmd:URL')
