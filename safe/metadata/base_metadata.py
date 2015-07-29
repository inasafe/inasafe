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
                                 insert_xml_element, reading_ancillary_files)
from safe.utilities.i18n import tr


class BaseMetadata(object):
    # define as Abstract base class
    __metaclass__ = abc.ABCMeta

    # paths in xml files for standard properties these are the ones we try
    # to read from an xml file
    _standard_properties = {
        'organisation': (
            'gmd:contact/'
            'gmd:CI_ResponsibleParty/'
            'gmd:organisationName/'
            'gco:CharacterString'),
        'email': (
            'gmd:contact/'
            'gmd:CI_ResponsibleParty/'
            'gmd:contactInfo/'
            'gmd:CI_Contact/'
            'gmd:address/'
            'gmd:CI_Address/'
            'gmd:electronicMailAddress/'
            'gco:CharacterString'),
        'document_date': (
            'gmd:dateStamp/'
            'gco:Date'),
        'abstract': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:abstract/'
            'gco:CharacterString'),
        'title': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:citation/'
            'gmd:CI_Citation/'
            'gmd:title/'
            'gco:CharacterString'),
        'license': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:resourceConstraints/'
            'gmd:MD_Constraints/'
            'gmd:useLimitation/'
            'gco:CharacterString'),
        'url': (
            'gmd:distributionInfo/'
            'gmd:MD_Distribution/'
            'gmd:transferOptions/'
            'gmd:MD_DigitalTransferOptions/'
            'gmd:onLine/'
            'gmd:CI_OnlineResource/'
            'gmd:linkage/'
            'gmd:URL'),
        'report': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe_report/'
            'gco:CharacterString'),
    }

    def __eq__(self, other):
        return self.dict == other.dict

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

        self._reading_ancillary_file = False
        self._properties = {}

        # initialise the properties
        for name, path in self._standard_properties.iteritems():
            self.set(name, None, path)

        self._last_update = datetime.now()

        # check if metadata already exist on disk
        self.read_from_ancillary_file(xml_uri)

    @abc.abstractproperty
    def dict(self):
        metadata = {}
        properties = {}
        for name, prop in self.properties.iteritems():
            properties[name] = prop.dict
        metadata['properties'] = properties
        return metadata

    @abc.abstractproperty
    def xml(self):
        tree = ElementTree.parse(METADATA_XML_TEMPLATE)
        root = tree.getroot()

        for name, prop in self.properties.iteritems():
            path = prop.xml_path
            elem = root.find(path, XML_NS)
            if elem is None:
                # create elem
                elem = insert_xml_element(root, path)
            elem.text = self.get_xml_value(name)

        return root

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
                        self.set(prop['name'], prop['value'], prop['xml_path'])
                    except KeyError:
                        # we just skip if we don't have something, we want
                        # to have as much as possible read from the JSON
                        pass
        return metadata

    @abc.abstractmethod
    def read_from_xml(self):
        with reading_ancillary_files(self):
            # this raises a IOError if the file doesn't exist
            root = ElementTree.parse(self.xml_uri).getroot()
            for name, path in self._standard_properties.iteritems():
                value = self._read_property_from_xml(root, path)
                if value is not None:
                    # this calls the default setters
                    setattr(self, name, value)

        return root

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

    def get_value(self, property_name):
        return self.get_property(property_name).value

    def get_xml_value(self, property_name):
        try:
            return self.get_property(property_name).xml_value
        except KeyError:
            return None

    def get_property(self, property_name):
        return self.properties[property_name]

    @property
    def properties(self):
        return self._properties

    def update(self, name, value):
        self.get_property(name).value = value

    def set(self, name, value, xml_path):
        xml_type = xml_path.split('/')[-1]
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

    def save(self, save_json=True, save_xml=True):
        if save_json:
            with open(self.json_uri, 'w') as f:
                f.write(self.json)
        if save_xml:
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
        return self.get_value('organisation')

    @organisation.setter
    def organisation(self, value):
        path = self._standard_properties['organisation']
        self.set('organisation', value, path)

    @property
    def email(self):
        return self.get_value('email')

    @email.setter
    def email(self, value):
        path = self._standard_properties['email']
        self.set('email', value, path)

    @property
    def document_date(self):
        return self.get_value('document_date')

    @document_date.setter
    def document_date(self, value):
        path = self._standard_properties['document_date']
        self.set('document_date', value, path)

    @property
    def abstract(self):
        return self.get_value('abstract')

    @abstract.setter
    def abstract(self, value):
        path = self._standard_properties['abstract']
        self.set('abstract', value, path)

    @property
    def title(self):
        return self.get_value('title')

    @title.setter
    def title(self, value):
        path = self._standard_properties['title']
        self.set('title', value, path)

    @property
    def license(self):
        return self.get_value('license')

    @license.setter
    def license(self, value):
        path = self._standard_properties['license']
        self.set('license', value, path)

    @property
    def url(self):
        return self.get_value('url')

    @url.setter
    def url(self, value):
        path = self._standard_properties['url']
        self.set('url', value, path)

    @property
    def report(self):
        return self.get_value('report')

    @report.setter
    def report(self, value):
        path = self._standard_properties['report']
        self.set('report', value, path)
