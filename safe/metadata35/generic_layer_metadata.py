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

from xml.etree import ElementTree
from safe.metadata35 import BaseMetadata
from safe.metadata35.utils import reading_ancillary_files, prettify_xml


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
    from safe.metadata35.utils import merge_dictionaries
    _standard_properties = merge_dictionaries(
        # change BaseMetadata to GenericLayerMetadata in subclasses
        BaseMetadata._standard_properties, _standard_properties)

    .. versionadded:: 3.2
    """

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
        super(GenericLayerMetadata, self).__init__(
            layer_uri, xml_uri, json_uri)

    @property
    def dict(self):
        """
        calls the overridden method

        :return: dictionary representation of the metadata
        :rtype: dict
        """
        return super(GenericLayerMetadata, self).dict

    @property
    def json(self):
        """
        calls the overridden method

        :return: json representation of the metadata
        :rtype: str
        """
        return super(GenericLayerMetadata, self).json

    @property
    def xml(self):
        """
        calls the overridden method

        :return: xml representation of the metadata
        :rtype: str
        """
        root = super(GenericLayerMetadata, self).xml
        return prettify_xml(ElementTree.tostring(root))

    def read_json(self):
        """
        calls the overridden method

        :return: the read metadata
        :rtype: dict
        """
        with reading_ancillary_files(self):
            metadata = super(GenericLayerMetadata, self).read_json()

        return metadata

    def read_xml(self):
        """
        calls the overridden method

        :return: the read metadata
        :rtype: ElementTree.Element
        """
        with reading_ancillary_files(self):
            root = super(GenericLayerMetadata, self).read_xml()

        return root

    def update_report(self):
        """
        update the report.
        """
        # TODO (MB): implement this by reading the kw and definitions.py
        self.report = self.report
        raise NotImplementedError()
