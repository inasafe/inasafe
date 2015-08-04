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

    def __getattr__(self, name):
        """
        Dynamically generate getter for each _standard_properties
        """
        if name in self._standard_properties:
            value = self.get_value(name)
        else:
            value = super(BaseMetadata, self).__getattr__(name)
        return value

    def __setattr__(self, name, value):
        """
        Dynamically generate setter for each _standard_properties
        """
        if name in self._standard_properties:
            path = self._standard_properties[name]
            self.set(name, value, path)
        else:
            super(BaseMetadata, self).__setattr__(name, value)

    def __eq__(self, other):
        return self.dict == other.dict

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        # private members
        self._layer_uri = layer_uri
        self._layer_is_file_based = os.path.isfile(layer_uri)

        path = os.path.splitext(layer_uri)[0]

        if xml_uri is None:
            if self.layer_is_file_based:
                self._xml_uri = '%s.xml' % path
            else:
                self._xml_uri = None
        else:
            self._xml_uri = xml_uri

        if json_uri is None:
            if self.layer_is_file_based:
                self._json_uri = '%s.json' % path
            else:
                self._json_uri = None
        else:
            self._json_uri = json_uri

        self._reading_ancillary_files = False
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
    def read_json(self):
        if self.json_uri is None:
            metadata = self._read_json_db()
        else:
            metadata = self._read_json_file()
        if 'properties' in metadata:
            for name, prop in metadata['properties'].iteritems():
                try:
                    self.set(prop['name'], prop['value'], prop['xml_path'])
                except KeyError:
                    # we just skip if we don't have something, we want
                    # to have as much as possible read from the JSON
                    pass
        return metadata

    def _read_json_file(self):
        with open(self.json_uri) as metadata_file:
            try:
                metadata = json.load(metadata_file)
                return metadata
            except ValueError:
                message = tr('the file %s does not appear to be valid JSON')
                message = message % self.json_uri
                raise MetadataReadError(message)

    def _read_json_db(self):
        metadata_str = None  # TODO (MB) implement
        if metadata_str is None:
            return {}
        try:
            metadata = json.loads(metadata_str)
            return metadata
        except ValueError:
            message = tr('the file DB entry for %s does not appear to be '
                         'valid JSON')
            message = message % self.layer_uri
            raise MetadataReadError(message)

    @abc.abstractmethod
    def read_xml(self):
        if self.xml_uri is None:
            root = self._read_xml_db()
        else:
            root = self._read_xml_file()
        if root is not None:
            for name, path in self._standard_properties.iteritems():
                value = self._read_property_from_xml(root, path)
                if value is not None:
                    # this calls the default setters
                    setattr(self, name, value)

        return root

    def _read_xml_file(self):
        # this raises a IOError if the file doesn't exist
        root = ElementTree.parse(self.xml_uri).getroot()
        return root

    def _read_xml_db(self):
        metadata_str = None  # TODO (MB) implement
        if metadata_str is None:
            return None
        root = ElementTree.fromstring(metadata_str)
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
        except TypeError:
            if self._reading_ancillary_files:
                # we are parsing files so we want to accept as much as
                # possible without raising exceptions
                pass
            else:
                raise

    def save(self, save_json=True, save_xml=True):
        if self.layer_is_file_based:
            if save_json:
                self.write_as(self.json_uri)
            if save_xml:
                self.write_as(self.xml_uri)
        else:
            if save_json:
                self.write_to_db('json')
            if save_xml:
                self.write_to_db('xml')

    def write_as(self, destination_path):
        file_format = os.path.splitext(destination_path)[1][1:]
        metadata = self.get_writable_metadata(file_format)

        with open(destination_path, 'w') as f:
            f.write(metadata)

        return metadata

    def write_to_db(self, file_format):
        metadata = self.get_writable_metadata(file_format)
        # TODO (MB) implement this
        return metadata

    def get_writable_metadata(self, file_format):
        if file_format == 'json':
            metadata = self.json
        elif file_format == 'xml':
            metadata = '<?xml version="1.0" encoding="UTF-8"?>\n'
            metadata += self.xml
        else:
            raise TypeError('The requested file type (%s) is not yet supported'
                            % file_format)
        return metadata

    def read_from_ancillary_file(self, custom_xml):
        # we explicitly check if a custom XML was passed so we give it
        # priority on the JSON. If no custom XML is passed, JSON has priority
        if custom_xml and os.path.isfile(self.xml_uri):
            self.read_xml()
        else:
            if not self.read_json():
                self.read_xml()

    @property
    def layer_is_file_based(self):
        return self._layer_is_file_based
