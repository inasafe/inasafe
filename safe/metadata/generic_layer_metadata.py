# coding=utf-8
"""This module exposure metadata implementation."""

from xml.etree import ElementTree

from safe.metadata import BaseMetadata
from safe.metadata.utilities import reading_ancillary_files, prettify_xml

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class GenericLayerMetadata(BaseMetadata):
    """
    Base class for generic layers such as hazard, exposure and aggregation.

    This class can be subclassed so you can create only a minimal
    concrete class that implements only _standard_properties to add specific
    properties. You can also add a standard XML property that applies to all
    subclasses here. In both cases do it as explained below. @property and
    @propname.setter will be generated automatically

    _standard_properties = {
        'TESTprop': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'gco:CharacterString')
    }
    from safe.metadata.utils import merge_dictionaries
    _standard_properties = merge_dictionaries(
        # change BaseMetadata to GenericLayerMetadata in subclasses
        BaseMetadata._standard_properties, _standard_properties)

    .. versionadded:: 3.2
    """

    def __init__(self, layer_uri, xml_uri=None, json_uri=None):
        """Constructor

        :param layer_uri: URI of the layer for which the metadata.
        :type layer_uri: str
        :param xml_uri: URI of an xml file to use.
        :type xml_uri: str
        :param json_uri: URI of a json file to use.
        :type json_uri: str
        """
        # initialize base class
        super(GenericLayerMetadata, self).__init__(
            layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        """
        calls the overridden method

        :return: Dictionary representation of the metadata.
        :rtype: dict
        """
        return super(GenericLayerMetadata, self).dict

    @property
    def json(self):
        """Calls the overridden method.

        :returns: json representation of the metadata.
        :rtype: str
        """
        return super(GenericLayerMetadata, self).json

    @property
    def xml(self):
        """Calls the overridden method.

        :returns: XML representation of the metadata.
        :rtype: str
        """
        root = super(GenericLayerMetadata, self).xml
        return prettify_xml(ElementTree.tostring(root))

    def read_json(self):
        """Calls the overridden method.

        :returns: The read metadata.
        :rtype: dict
        """
        with reading_ancillary_files(self):
            metadata = super(GenericLayerMetadata, self).read_json()

        return metadata

    def read_xml(self):
        """Calls the overridden method.

        :returns: The read metadata.
        :rtype: ElementTree.Element
        """
        with reading_ancillary_files(self):
            root = super(GenericLayerMetadata, self).read_xml()

        return root

    def update_report(self):
        """Update the report."""
        # TODO (MB): implement this by reading the kw and definitions
        self.report = self.report
        raise NotImplementedError()
