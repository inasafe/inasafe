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

# using this approach:
# http://eli.thegreenplace.net/2009/02/06/getters-and-setters-in-python

import abc
from datetime import datetime
import json
import os
from xml.etree import ElementTree

from safe.common.exceptions import MetadataReadError
from safe.metadata.utils import (METADATA_XML_TEMPLATE,
                                 TYPE_CONVERSIONS,
                                 XML_NS,
                                 insert_xml_element)
from safe.utilities.i18n import tr


class BaseMetadata(object):
    # define as Abstract base class
    __metaclass__ = abc.ABCMeta

    # paths in xml files for standard properties
    _standard_properties = {
        'organisation': (
            'gmd:contact/'
            'gmd:CI_ResponsibleParty/'
            'gmd:organisationName'),
        'email': (
            'gmd:contact/'
            'gmd:CI_ResponsibleParty/'
            'gmd:contactInfo/'
            'gmd:CI_Contact/'
            'gmd:address/'
            'gmd:CI_Address/'
            'gmd:electronicMailAddress'),
        'document_date': (
            'gmd:dateStamp'),
        'abstract': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:abstract'),
        'title': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:citation/'
            'gmd:CI_Citation/'
            'gmd:title'),
        'license': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:resourceConstraints/'
            'gmd:MD_Constraints/'
            'gmd:useLimitation'),
        'url': (
            'gmd:distributionInfo/'
            'gmd:MD_Distribution/'
            'gmd:transferOptions/'
            'gmd:MD_DigitalTransferOptions/'
            'gmd:onLine/'
            'gmd:CI_OnlineResource/'
            'gmd:linkage')
    }

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        # private members
        self._layer_uri = layer_uri
        path = os.path.splitext(layer_uri)[0]
        if xml_uri is None:
            self._xml_uri = '%s.xml' % path
        else:
            self._xml_uri = xml_uri
        if json_uri is None:
            self._json_uri = '%s.json' % path
        else:
            self._json_uri = json_uri

        self._properties = {}

        self._last_update = datetime.now()

        self._reading_ancillary_file = False

        # check if metadata already exist on disk
        self.read_from_ancillary_file(xml_uri)

    @abc.abstractproperty
    def dict(self):
        metadata = {'layer_uri': self.layer_uri}
        properties = {}
        for name, prop in self._properties.iteritems():
            properties[name] = prop.dict
        metadata['properties'] = properties
        return metadata

    @property
    def xml(self):
        tree = ElementTree.parse(METADATA_XML_TEMPLATE)
        root = tree.getroot()

        # get the standard properties
        for name, path in self._standard_properties.iteritems():
            elem = root.find(path, XML_NS)
            if elem is None:
                # create elem
                elem = insert_xml_element(root, path)
            elem.text = self.get_xml_value(name)

        # TODO (MB) have a look if this is a good idea :)
        # check if we have more properties
        for name, path in self._properties.iteritems():
            if name in self._standard_properties:
                continue
            elem = root.find(path, XML_NS)
            if elem is None:
                # create elem
                elem = insert_xml_element(root, path)
            elem.text = self.get_xml_value(name)

        return ElementTree.tostring(root)

    @abc.abstractproperty
    def json(self):
        return json.dumps(self.dict, indent=2, sort_keys=True)

    @abc.abstractmethod
    def read_from_json(self):
        metadata = {}
        with open(self.json_uri) as metadata_file:
            try:
                metadata = json.load(metadata_file)
            except ValueError:
                message = tr('the file %s does not appear to be valid JSON')
                message = message % self.json_uri
                raise MetadataReadError(message)
            if 'properties' in metadata:
                for name, prop in metadata['properties'].iteritems():
                    try:
                        self.set(prop['name'],
                                 prop['value'],
                                 prop['xml_path'],
                                 prop['xml_type'])
                    except KeyError:
                        # we just skip if we don't have something, we want
                        # to have as much as possible read from the JSON
                        pass
        return metadata

    @abc.abstractmethod
    def read_from_xml(self):
        self._reading_ancillary_file = True
        # this raises a IOError if the file doesn't exist
        root = ElementTree.parse(self.xml_uri).getroot()
        for name, path in self._standard_properties.iteritems():
            value = self._read_property_from_xml(root, path)
            if value is not None:
                setattr(self, name, value)

        self._reading_ancillary_file = False

    @staticmethod
    def _read_property_from_xml(root, path):
        element = root.find(path, XML_NS)
        try:
            return element.text.strip(' \t\n\r')
        except AttributeError:
            return None

    @property
    # there is no setter because the layer should not change overtime
    def layer_uri(self):
        return self._layer_uri

    @property
    # there is no setter because the json should not change overtime
    def json_uri(self):
        return self._json_uri

    @property
    # there is no setter because the xml should not change overtime
    def xml_uri(self):
        return self._xml_uri

    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, time):
        self._last_update = time

    def set_last_update_to_now(self):
        self._last_update = datetime.now()

    def get(self, property_name):
        return self._properties[property_name].value

    def get_xml_value(self, property_name):
        try:
            return self._properties[property_name].xml_value
        except KeyError:
            return None

    def get_property(self, property_name):
        return self._properties[property_name]

    def update(self, name, value):
        self.get_property(name).value = value

    def set(self, name, value, xml_path, xml_type):
        # check if the desired type is supported
        try:
            property_class = TYPE_CONVERSIONS[xml_type]
        except KeyError:
            raise KeyError('The xml type %s is not supported yet' % xml_type)

        try:
            metadata_property = property_class(name, value, xml_path, xml_type)
            self._properties[name] = metadata_property
            self.set_last_update_to_now()
            return True
        except TypeError:
            if self._reading_ancillary_file:
                return False
            else:
                raise

    def save(self):
        with open(self.json_uri, 'w') as f:
            f.write(self.json)

        with open(self.xml_uri, 'w') as f:
            f.write(self.xml)

    def write_as(self, destination_path):
        file_format = os.path.splitext(destination_path)[1]
        if file_format == '.json':
            metadata = self.json
        elif file_format == '.xml':
            metadata = '<?xml version="1.0" encoding="UTF-8"?>\n'
            metadata += self.xml
        else:
            raise TypeError('The requested file type (%s) is not yet supported'
                            % file_format)
        with open(destination_path, 'w') as f:
            f.write(metadata)

    def read_from_ancillary_file(self, custom_xml):
        # we explicitly check if a custom XML was passed so we give it
        # priority on the JSON. If no custom XML is passed, JSON has priority
        if custom_xml and os.path.isfile(self.xml_uri):
            self.read_from_xml()
        else:
            if os.path.isfile(self.json_uri):
                self.read_from_json()
            elif os.path.isfile(self.xml_uri):
                self.read_from_xml()

    # Standard XML properties
    @property
    def organisation(self):
        return self.get('organisation')

    @organisation.setter
    def organisation(self, value):
        path = self._standard_properties['organisation']
        return self.set('organisation', value, path, 'gco:CharacterString')

    @property
    def email(self):
        return self.get('email')

    @email.setter
    def email(self, value):
        path = self._standard_properties['email']
        return self.set('email', value, path, 'gco:CharacterString')

    @property
    def document_date(self):
        return self.get('document_date')

    @document_date.setter
    def document_date(self, value):
        path = self._standard_properties['document_date']
        return self.set('document_date', value, path, 'gco:Date')

    @property
    def abstract(self):
        return self.get('abstract')

    @abstract.setter
    def abstract(self, value):
        path = self._standard_properties['abstract']
        return self.set('abstract', value, path, 'gco:CharacterString')

    @property
    def title(self):
        return self.get('title')

    @title.setter
    def title(self, value):
        path = self._standard_properties['title']
        return self.set('title', value, path, 'gco:CharacterString')

    @property
    def license(self):
        return self.get('license')

    @license.setter
    def license(self, value):
        path = self._standard_properties['license']
        return self.set('license', value, path, 'gco:CharacterString')

    @property
    def url(self):
        return self.get('url')

    @url.setter
    def url(self, value):
        path = self._standard_properties['url']
        return self.set('url', value, path, 'gmd:URL')
