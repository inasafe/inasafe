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
from safe.metadata35 import BaseMetadata
from safe.metadata35.provenance import Provenance
from safe.metadata35.utils import reading_ancillary_files, XML_NS, prettify_xml
from safe.metadata35.utils import merge_dictionaries

from safe.metadata35.encoder import MetadataEncoder


class ImpactLayerMetadata(BaseMetadata):
    """
    Metadata class for impact layers

    if you need to add a standard XML property that only applies to this
    subclass, do it this way. @property and @propname.setter will be
    generated automatically

    _standard_properties = {
        'TESTprop': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'gco:CharacterString')
    }
    from safe.metadata35.utils import merge_dictionaries
    _standard_properties = merge_dictionaries(
        BaseMetadata._standard_properties, _standard_properties)

    .. versionadded:: 3.2
    """

    # remember to add an attribute or a setter property with the same name
    # these are properties that need special getters and setters thus are
    # not put in the standard_properties
    _standard_properties = {
        'elapsed_time': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'elapsed_time/'
            'gco:Integer'),
        'hazard_title': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard_title/'
            'gco:CharacterString'),
        'postprocessing_report': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'postprocessing_report/'
            'gco:CharacterString'),
        'exposure_title': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'exposure_title/'
            'gco:CharacterString'),
        'legend_title': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'legend_title/'
            'gco:CharacterString'),
        'legend_notes': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'legend_notes/'
            'gco:CharacterString'),
        'exposure_source': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'exposure_source/'
            'gco:CharacterString'),
        'map_title': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'map_title/'
            'gco:CharacterString'),
        'legend_units': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'legend_units/'
            'gco:CharacterString'),
        'impact_summary': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'impact_summary/'
            'gco:CharacterString'),
        'user': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'user/'
            'gco:CharacterString'),
        'host_name': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'host_name/'
            'gco:CharacterString'),
        'time_stamp': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'time_stamp/'
            'gco:CharacterString'),
        'hazard_source': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard_source/'
            'gco:CharacterString'),
        'target_field': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'target_field/'
            'gco:CharacterString'),
        'impact_table': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'impact_table/'
            'gco:CharacterString'),
    }
    _standard_properties = merge_dictionaries(
        BaseMetadata._standard_properties, _standard_properties)

    _special_properties = {
        'provenance': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe_provenance')
    }

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        """
        Constructor

        :param layer_uri: uri of the layer for which the metadata ae
        :type layer_uri: str
        :param xml_uri: uri of an xml file to use
        :type xml_uri: str
        :param json_uri: uri of a json file to use
        :type json_uri: str
        """

        # Initialise members
        # private members
        self._provenance = Provenance()

        # public members
        self.summary_data = None

        # initialize base class
        super(ImpactLayerMetadata, self).__init__(layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        """
        calls the overridden method and adds provenance and summary data

        :return: dictionary representation of the metadata
        :rtype: dict
        """
        metadata = super(ImpactLayerMetadata, self).dict

        metadata['provenance'] = self.provenance
        metadata['summary_data'] = self.summary_data

        return metadata

    @property
    def json(self):
        """
        json representation of the metadata

        :return: json representation of the metadata
        :rtype: str
        """
        metadata = self.dict

        metadata['provenance'] = self.provenance.dict
        json_dumps = json.dumps(
                metadata, indent=2, sort_keys=True, separators=(',', ': '),
                cls=MetadataEncoder)
        if not json_dumps.endswith('\n'):
            json_dumps += '\n'
        return json_dumps

    def read_json(self):
        """
        read metadata from json and set all the found properties.

        :return: the read metadata
        :rtype: dict
        """
        with reading_ancillary_files(self):
            metadata = super(ImpactLayerMetadata, self).read_json()
            if 'provenance' in metadata:
                for provenance_step in metadata['provenance']:
                    try:
                        title = provenance_step['title']
                        if 'IF Provenance' in title:
                            self.append_if_provenance_step(
                                provenance_step['title'],
                                provenance_step['description'],
                                provenance_step['time'],
                                provenance_step['data']
                            )
                        else:
                            self.append_provenance_step(
                                provenance_step['title'],
                                provenance_step['description'],
                                provenance_step['time'],
                            )
                    except KeyError:
                        # we want to get as much as we can without raising
                        # errors
                        pass
            if 'summary_data' in metadata:
                self.summary_data = metadata['summary_data']

        return metadata

    @property
    def xml(self):
        """
        xml representation of the metadata.

        :return: xml representation of the metadata
        :rtype: ElementTree.Element
        """

        root = super(ImpactLayerMetadata, self).xml
        provenance_path = self._special_properties['provenance']
        provenance_element = root.find(provenance_path, XML_NS)

        # find the provenance parent tag
        if provenance_element is not None:
            # there is already a provenance tag so we remove it
            provenance_parent = provenance_element.getparent()
            provenance_parent.remove(provenance_element)
        else:
            # find the parent using the provenance path minus one level
            provenance_parent = '/'.join(provenance_path.split('/')[:-1])
            provenance_parent = root.find(provenance_parent, XML_NS)

        # generate the provenance xml element
        provenance_element = ElementTree.fromstring(self.provenance.xml)
        provenance_parent.append(provenance_element)
        return prettify_xml(ElementTree.tostring(root))

    def read_xml(self):
        """
        read metadata from xml and set all the found properties.

        :return: the root element of the xml
        :rtype: ElementTree.Element
        """

        with reading_ancillary_files(self):
            root = super(ImpactLayerMetadata, self).read_xml()
            if root is not None:
                self._read_provenance_from_xml(root)
        return root

    def _read_provenance_from_xml(self, root):
        """
        read metadata provenance from xml.

        :param root: container in which we search
        :type root: ElementTree.Element
        """
        path = self._special_properties['provenance']
        provenance = root.find(path, XML_NS)
        for step in provenance.iter('provenance_step'):
            title = step.find('title').text
            description = step.find('description').text
            timestamp = step.get('timestamp')

            if 'IF Provenance' in title:
                data = {}
                from safe.metadata35.provenance import IFProvenanceStep
                keys = IFProvenanceStep.impact_functions_fields
                for key in keys:
                    value = step.find(key)
                    if value is not None:
                        data[key] = value.text
                    else:
                        data[key] = ''
                self.append_if_provenance_step(
                        title, description, timestamp, data)
            else:
                self.append_provenance_step(title, description, timestamp)

    @property
    def provenance(self):
        """
        Get the provenance elements of the metadata

        there is no setter as provenance can only grow. use
        append_provenance_step to add steps

        :return: The provenance element
        :rtype: Provenance
        """
        return self._provenance

    def append_provenance_step(self, title, description, timestamp=None):
        """
        Add a step to the provenance of the metadata

        :param title: The title of the step.
        :type title: str

        :param description: The content of the step
        :type description: str

        :param timestamp: the time of the step
        :type timestamp: datetime, str
        """
        step_time = self._provenance.append_step(title, description, timestamp)
        if step_time > self.last_update:
            self.last_update = step_time

    def append_if_provenance_step(
            self, title, description, timestamp=None, data=None):
        """Add a if provenance step to the provenance of the metadata

        :param title: The title of the step.
        :type title: str

        :param description: The content of the step
        :type description: str

        :param timestamp: the time of the step
        :type timestamp: datetime, str

        :param data: The data of the step.
        :type data: dict
        """
        step_time = self._provenance.append_if_provenance_step(
                title, description, timestamp, data)
        if step_time > self.last_update:
            self.last_update = step_time

    def update_from_dict(self, keywords):
        """Update metadata value from a keywords dictionary.

        :param keywords:
        :return:
        """
        super(ImpactLayerMetadata, self).update_from_dict(keywords)

        if 'if_provenance' in list(keywords.keys()):
            if_provenance = keywords['if_provenance']
            for provenance_step in if_provenance:
                self.provenance.append_provenance_step(provenance_step)
