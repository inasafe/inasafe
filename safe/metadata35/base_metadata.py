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

from safe.metadata35.encoder import MetadataEncoder
from future.utils import with_metaclass

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

from safe.common.exceptions import MetadataReadError, HashNotFoundError
from safe.metadata35.metadata_db_io import MetadataDbIO
from safe.metadata35.utils import (
    METADATA_XML_TEMPLATE,
    TYPE_CONVERSIONS,
    XML_NS,
    insert_xml_element,
    read_property_from_xml,
    reading_ancillary_files
)
from safe.utilities.i18n import tr
multipart_polygon_key = 'multipart_polygon'


class BaseMetadata(with_metaclass(abc.ABCMeta, object)):
    """
    Abstract Metadata class, this has to be subclassed.

    if you need to add a standard XML property add it to _standard_properties
    @property and @propname.setter will be generated automatically
    Standard properties are the ones that we try to read from an xml file
    when instantiating a new metadata object.
    Reading from json metadata files is easier because we have an ordered
    structure.

    The class will try to read all she can without throwing errors because
    the more we can read from malformed input the better.

    .. versionadded:: 3.2
    """

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
        'date': (
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
            'inasafe/'
            'report/'
            'gco:CharacterString'),
        'layer_purpose': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'layer_purpose/'
            'gco:CharacterString'),
        'layer_mode': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'layer_mode/'
            'gco:CharacterString'),
        'layer_geometry': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'layer_geometry/'
            'gco:CharacterString'),
        'keyword_version': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'keyword_version/'
            'gco:CharacterString'),
        'scale': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'scale/'
            'gco:CharacterString'),
        'source': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'source/'
            'gco:CharacterString'),
        'datatype': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'datatype/'
            'gco:CharacterString'),
        'multipart_polygon': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            '%s/'
            'gco:Boolean' % multipart_polygon_key),
        'resolution': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'resolution/'
            'gco:FloatTuple')
    }

    def __getattr__(self, name):
        """
        Dynamically generate getter for each _standard_properties.
        """
        if name in self._standard_properties:
            value = self.get_value(name)
        else:
            value = super(BaseMetadata, self).__getattr__(name)
        return value

    def __setattr__(self, name, value):
        """
        Dynamically generate setter for each _standard_properties.
        """
        if name in self._standard_properties:
            path = self._standard_properties[name]
            self.set(name, value, path)
        else:
            super(BaseMetadata, self).__setattr__(name, value)

    def __eq__(self, other):
        return self.dict == other.dict

    @abc.abstractmethod
    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        """
        Constructor.

        :param layer_uri: uri of the layer for which the metadata ae
        :type layer_uri: str
        :param xml_uri: uri of an xml file to use
        :type xml_uri: str
        :param json_uri: uri of a json file to use
        :type json_uri: str
        """
        # private members
        self._layer_uri = layer_uri
        # TODO (MB): maybe use MetadataDbIO.are_metadata_file_based instead
        self._layer_is_file_based = os.path.isfile(layer_uri)

        instantiate_metadata_db = False

        path = os.path.splitext(layer_uri)[0]

        if xml_uri is None:
            if self.layer_is_file_based:
                self._xml_uri = '%s.xml' % path
            else:
                # xml should be stored in cacheDB
                self._xml_uri = None
                instantiate_metadata_db = True
        else:
            self._xml_uri = xml_uri

        if json_uri is None:
            if self.layer_is_file_based:
                self._json_uri = '%s.json' % path
            else:
                # json should be stored in cacheDB
                self._json_uri = None
                instantiate_metadata_db = True

        else:
            self._json_uri = json_uri

        if instantiate_metadata_db:
            self.db_io = MetadataDbIO()

        self.reading_ancillary_files = False
        self._properties = {}

        # initialise the properties
        for name, path in list(self._standard_properties.items()):
            self.set(name, None, path)

        self._last_update = datetime.now()

        try:
            self.read_from_ancillary_file(xml_uri)
        except IOError:
            pass

    @abc.abstractproperty
    def dict(self):
        """
        dictionary representation of the metadata.

        :return: dictionary representation of the metadata
        :rtype: dict
        """
        metadata = {}
        properties = {}
        for name, prop in list(self.properties.items()):
            properties[name] = prop.dict
        metadata['properties'] = properties
        return metadata

    @abc.abstractproperty
    def xml(self):
        """
        xml representation of the metadata.

        :return: xml representation of the metadata
        :rtype: ElementTree.Element
        """
        tree = ElementTree.parse(METADATA_XML_TEMPLATE)
        root = tree.getroot()

        for name, prop in list(self.properties.items()):
            path = prop.xml_path
            elem = root.find(path, XML_NS)
            if elem is None:
                # create elem
                elem = insert_xml_element(root, path)
            elem.text = self.get_xml_value(name)

        return root

    @abc.abstractproperty
    def json(self):
        """
        json representation of the metadata.

        :return: json representation of the metadata
        :rtype: str
        """
        json_dumps = json.dumps(
            self.dict,
            indent=2,
            sort_keys=True,
            separators=(',', ': '),
            cls=MetadataEncoder
        )
        if not json_dumps.endswith('\n'):
            json_dumps += '\n'
        return json_dumps

    @abc.abstractmethod
    def read_json(self):
        """
        read metadata from json and set all the found properties.

        when overriding remember to wrap your calls in reading_ancillary_files

        :return: the read metadata
        :rtype: dict
        """
        with reading_ancillary_files(self):
            if self.json_uri is None:
                metadata = self._read_json_db()
            else:
                metadata = self._read_json_file()
            if 'properties' in metadata:
                for name, prop in list(metadata['properties'].items()):
                    try:
                        self.set(prop['name'], prop['value'], prop['xml_path'])
                    except KeyError:
                        # we just skip if we don't have something, we want
                        # to have as much as possible read from the JSON
                        pass
        return metadata

    def _read_json_file(self):
        """
        read metadata from a json file.

        :return: the parsed json dict
        :rtype: dict
        """
        with open(self.json_uri) as metadata_file:
            try:
                metadata = json.load(metadata_file)
                return metadata
            except ValueError:
                message = tr('the file %s does not appear to be valid JSON')
                message = message % self.json_uri
                raise MetadataReadError(message)

    def _read_json_db(self):
        """
        read metadata from a json string stored in a DB.

        :return: the parsed json dict
        :rtype: dict
        """
        try:
            metadata_str = self.db_io.read_metadata_from_uri(
                self.layer_uri, 'json')
        except HashNotFoundError:
            return {}
        try:
            metadata = json.loads(metadata_str)
            return metadata
        except ValueError:
            message = tr('the file DB entry for %s does not appear to be '
                         'valid JSON')
            message %= self.layer_uri
            raise MetadataReadError(message)

    @abc.abstractmethod
    def read_xml(self):
        """
        read metadata from xml and set all the found properties.

        :return: the root element of the xml
        :rtype: ElementTree.Element
        """
        if self.xml_uri is None:
            root = self._read_xml_db()
        else:
            root = self._read_xml_file()
        if root is not None:
            for name, path in list(self._standard_properties.items()):
                value = read_property_from_xml(root, path)
                if value is not None:
                    # this calls the default setters
                    setattr(self, name, value)

        return root

    def _read_xml_file(self):
        """
        read metadata from an xml file.

        :return: the root element of the xml
        :rtype: ElementTree.Element
        """
        # this raises a IOError if the file doesn't exist
        root = ElementTree.parse(self.xml_uri)
        root.getroot()
        return root

    def _read_xml_db(self):
        """
        read metadata from an xml string stored in a DB.

        :return: the root element of the xml
        :rtype: ElementTree.Element
        """
        try:
            metadata_str = self.db_io.read_metadata_from_uri(
                self.layer_uri, 'xml')
            root = ElementTree.fromstring(metadata_str)
            return root
        except HashNotFoundError:
            return None

    @property
    # there is no setter because the layer should not change overtime
    def layer_uri(self):
        """
        the layer URI.

        :return: the layer URI
        :rtype: str
        """
        return self._layer_uri

    @property
    # there is no setter because the json should not change overtime
    def json_uri(self):
        """
        the json file URI if it is None than the json is coming from a DB.

        :return: the json URI
        :rtype: str, None
        """
        return self._json_uri

    @property
    # there is no setter because the xml should not change overtime
    def xml_uri(self):
        """
        the xml file URI if it is None than the xml is coming from a DB.

        :return: the xml URI
        :rtype: str, None
        """
        return self._xml_uri

    @property
    def last_update(self):
        """
        time of the last update of the metadata in memory.

        :return: time of the last update
        :rtype: datetime
        """
        return self._last_update

    @last_update.setter
    def last_update(self, time):
        """
        set time of the last update of the metadata in memory.

        :param time: the update time
        :type time: datetime
        """
        self._last_update = time

    def set_last_update_to_now(self):
        """
        set time of the last update of the metadata in memory to now.
        """
        self._last_update = datetime.now()

    def get_value(self, name):
        """
        get the typed value of a property.

        The type is the original python type used when the value was set

        :param name: the name of the property
        :type name: str
        :return: the value of the property
        """
        return self.get_property(name).value

    def get_xml_value(self, name):
        """
        get the xml value of a property.

        :param name: the name of the property
        :type name: str
        :return: the value of the property
        :rtype: str
        """

        return self.get_property(name).xml_value

    def get_property(self, name):
        """
        get a property.

        :param name: the name of the property
        :type name: str
        :return: the property
        :rtype: BaseProperty
        """
        return self.properties[name]

    @property
    def properties(self):
        """
        get all properties.

        :return: the properties
        :rtype: dict
        """
        return self._properties

    def update(self, name, value):
        """
        update a property value.

        The accepted type depends on the property type

        :param name: the name of the property
        :type name: str
        :param value: the new value
        """
        self.get_property(name).value = value

    def set(self, name, value, xml_path):
        """
        Create a new metadata property.

        The accepted type depends on the property type which is determined
        by the xml_path

        :param name: the name of the property
        :type name: str
        :param value: the value of the property
        :type value:
        :param xml_path: the xml path where the property should be stored.
        This is split on / and the last element is used to determine the
        property type
        :type xml_path: str
        """

        xml_type = xml_path.split('/')[-1]
        # check if the desired type is supported
        try:
            property_class = TYPE_CONVERSIONS[xml_type]
        except KeyError:
            raise KeyError('The xml type %s is not supported yet' % xml_type)

        try:
            metadata_property = property_class(name, value, xml_path)
            self._properties[name] = metadata_property
            self.set_last_update_to_now()
        except TypeError:
            if self.reading_ancillary_files:
                # we are parsing files so we want to accept as much as
                # possible without raising exceptions
                pass
            else:
                raise

    def save(self, save_json=True, save_xml=True):
        """
        Saves the metadata json and/or xml to a file or DB.

        :param save_json: flag to save json
        :type save_json: bool
        :param save_xml: flag to save xml
        :type save_xml: bool
        """
        if self.layer_is_file_based:
            if save_json:
                self.write_to_file(self.json_uri)
            if save_xml:
                self.write_to_file(self.xml_uri)
        else:
            self.write_to_db(save_json, save_xml)

    def write_to_file(self, destination_path):
        """
        Writes the metadata json or xml to a file.

        :param destination_path: the file path the file format is inferred
        from the destination_path extension.
        :type destination_path: str
        :return: the written metadata
        :rtype: str
        """
        file_format = os.path.splitext(destination_path)[1][1:]
        metadata = self.get_writable_metadata(file_format)

        with open(destination_path, 'w') as f:
            f.write(metadata)

        return metadata

    def write_to_db(self, save_json=True, save_xml=True):
        """
        Stores the metadata json and/or xml in a DB.

        The returned tuple can contain None.

        :param save_json: flag to save json
        :type save_json: bool
        :param save_xml: flag to save xml
        :type save_xml: bool
        :return: the stored metadata
        :rtype: (str, str)
        """
        metadata_json = None
        metadata_xml = None
        if save_json:
            metadata_json = self.get_writable_metadata('json')
        if save_xml:
            metadata_xml = self.get_writable_metadata('xml')
        self.db_io.write_metadata_for_uri(
            self.layer_uri, metadata_json, metadata_xml)
        return metadata_json, metadata_xml

    def get_writable_metadata(self, file_format):
        """
        Convert the metadata to a writable form.

        :param file_format: the needed format can be json or xml
        :type file_format: str
        :return: the dupled metadata
        :rtype: str
        """
        if file_format == 'json':
            metadata = self.json
        elif file_format == 'xml':
            metadata = self.xml
        else:
            raise TypeError('The requested file type (%s) is not yet supported'
                            % file_format)
        return metadata

    def read_from_ancillary_file(self, custom_xml=None):
        """
        try to read xml and json from existing files or db.

        This is used when instantiating a new metadata object. We explicitly
        check if a custom XML was passed so we give it priority on the JSON.
        If no custom XML is passed, JSON has priority

        :param custom_xml: the path to a custom xml file
        :type custom_xml: str
        """

        if custom_xml and os.path.isfile(self.xml_uri):
            self.read_xml()
        else:
            if not self.read_json():
                self.read_xml()

    @property
    def layer_is_file_based(self):
        """
        flag if the layer is file based.

        :return: flag if the layer is file based
        :rtype: bool
        """
        return self._layer_is_file_based

    def update_from_dict(self, keywords):
        """Set properties of metadata using key and value from keywords

        :param keywords: A dictionary of keywords (key, value).
        :type keywords: dict

        """
        for key, value in list(keywords.items()):
            setattr(self, key, value)
