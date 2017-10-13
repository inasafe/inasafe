# coding=utf-8
"""Metadata for Output Layer."""

import json
from xml.etree import ElementTree
from safe.metadata import BaseMetadata

from safe.metadata.utilities import reading_ancillary_files, prettify_xml
from safe.metadata.utilities import XML_NS
from safe.metadata.utilities import merge_dictionaries
from safe.metadata.encoder import MetadataEncoder

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class OutputLayerMetadata(BaseMetadata):
    """
    Metadata class for exposure summary layers

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
    from safe.metadata.utils import merge_dictionaries
    _standard_properties = merge_dictionaries(
        BaseMetadata._standard_properties, _standard_properties)

    .. versionadded:: 3.2
    """

    # remember to add an attribute or a setter property with the same name
    # these are properties that need special getters and setters thus are
    # not put in the standard_properties
    _standard_properties = {
        'exposure_keywords': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'exposure_keywords/'
            'gco:Dictionary'),
        'hazard_keywords': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard_keywords/'
            'gco:Dictionary'),
        'aggregation_keywords': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'aggregation_keywords/'
            'gco:Dictionary'),
        'provenance_data': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'provenance_data/'
            'gco:Dictionary'),
    }
    _standard_properties = merge_dictionaries(
        BaseMetadata._standard_properties, _standard_properties)

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
        
        # initialize base class
        super(
            OutputLayerMetadata, self).__init__(
            layer_uri, xml_uri, json_uri
        )

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
            metadata = super(OutputLayerMetadata, self).read_json()

        return metadata

    @property
    def xml(self):
        """
        xml representation of the metadata.

        :return: xml representation of the metadata
        :rtype: ElementTree.Element
        """

        root = super(OutputLayerMetadata, self).xml
        return prettify_xml(ElementTree.tostring(root))

    def read_xml(self):
        """
        read metadata from xml and set all the found properties.

        :return: the root element of the xml
        :rtype: ElementTree.Element
        """

        with reading_ancillary_files(self):
            root = super(OutputLayerMetadata, self).read_xml()
        return root

    def update_from_dict(self, keywords):
        """Update metadata value from a keywords dictionary.

        :param keywords:
        :return:
        """
        super(OutputLayerMetadata, self).update_from_dict(keywords)
