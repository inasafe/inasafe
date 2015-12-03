# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata utilities module.**

Contact : ole.moller.nielsen@gmail.com

.. versionadded:: 3.3

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '03/12/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
from safe.common.exceptions import MetadataReadError
from safe.metadata import ExposureLayerMetadata, HazardLayerMetadata, \
    AggregationLayerMetadata, ImpactLayerMetadata, GenericLayerMetadata


def write_iso19115_metadata(layer_uri, keywords):
    """Create metadata  object from a layer path and keywords dictionary.

    :param layer_uri: Uri to layer.
    :type layer_uri: str

    :param keywords: Dictionary of keywords.
    :type keywords: dict
    """

    if 'layer_purpose' in keywords.keys():
        if keywords['layer_purpose'] == 'exposure':
            metadata = ExposureLayerMetadata(layer_uri)
        elif keywords['layer_purpose'] == 'hazard':
            metadata = HazardLayerMetadata(layer_uri)
        elif keywords['aggregation'] == 'aggregation':
            metadata = AggregationLayerMetadata(layer_uri)
        elif keywords['layer_purpose'] == 'impact':
            metadata = ImpactLayerMetadata(layer_uri)
        else:
            metadata = GenericLayerMetadata(layer_uri)
    else:
        metadata = GenericLayerMetadata(layer_uri)

    metadata.update_from_dict(keywords)

    if metadata.layer_is_file_based:
        xml_file_path = layer_uri.split('.')[0] + '.xml'
        print xml_file_path
        metadata.write_to_file(xml_file_path)
    else:
        metadata.write_to_db()

    return metadata


def read_iso19115_metadata(layer_uri, keyword=None):
    """Retrieve keywords from a metadata object
    :param layer_uri:
    :param keyword:
    :return:
    """
    xml_uri = layer_uri.split('.')[0] + '.xml'
    if not os.path.exists(xml_uri):
        xml_uri = None
    metadata = GenericLayerMetadata(layer_uri, xml_uri)
    if metadata.layer_purpose == 'exposure':
        metadata = ExposureLayerMetadata(layer_uri, xml_uri)
    elif metadata.layer_purpose == 'hazard':
        metadata = HazardLayerMetadata(layer_uri, xml_uri)
    elif metadata.layer_purpose == 'aggregation':
        metadata = AggregationLayerMetadata(layer_uri, xml_uri)
    elif metadata.layer_purpose == 'impact':
        metadata = ImpactLayerMetadata(layer_uri, xml_uri)

    if keyword:
        try:
            return metadata.dict['properties'][keyword]['value']
        except KeyError:
            raise MetadataReadError
    # dictionary comprehension
    return {x[0]: x[1]['value'] for x in metadata.dict['properties'].iteritems() if x[1]['value'] is not None}