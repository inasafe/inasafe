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
from safe.common.exceptions import (
    MetadataReadError,
    KeywordNotFoundError,
    MissingMetadata,
    NoKeywordsFoundError
)
from safe.metadata import (
    ExposureLayerMetadata,
    HazardLayerMetadata,
    AggregationLayerMetadata,
    ImpactLayerMetadata,
    GenericLayerMetadata
)
from safe.definitions import inasafe_keyword_version


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
        elif keywords['layer_purpose'] == 'aggregation':
            metadata = AggregationLayerMetadata(layer_uri)
        elif keywords['layer_purpose'] == 'impact':
            metadata = ImpactLayerMetadata(layer_uri)
        else:
            metadata = GenericLayerMetadata(layer_uri)
    else:
        metadata = GenericLayerMetadata(layer_uri)

    metadata.update_from_dict(keywords)
    metadata.update_from_dict({'keyword_version': inasafe_keyword_version})

    if metadata.layer_is_file_based:
        xml_file_path = layer_uri.split('.')[0] + '.xml'
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
    if not xml_uri and os.path.exists(layer_uri):
        message = 'Layer based file but no xml file.\n'
        message += 'Layer path: %s.' % layer_uri
        raise NoKeywordsFoundError(message)
    metadata = GenericLayerMetadata(layer_uri, xml_uri)
    if metadata.layer_purpose == 'exposure':
        metadata = ExposureLayerMetadata(layer_uri, xml_uri)
    elif metadata.layer_purpose == 'hazard':
        metadata = HazardLayerMetadata(layer_uri, xml_uri)
    elif metadata.layer_purpose == 'aggregation':
        metadata = AggregationLayerMetadata(layer_uri, xml_uri)
    elif metadata.layer_purpose == 'impact':
        metadata = ImpactLayerMetadata(layer_uri, xml_uri)

    # dictionary comprehension
    keywords = {x[0]: x[1]['value'] for x in metadata.dict['properties'].iteritems() if x[1]['value'] is not None}
    if 'keyword_version' not in keywords.keys() and xml_uri:
        message = 'No keyword version found. Metadata xml file is invalid.\n'
        message += 'Layer uri: %s\n' % layer_uri
        message += 'Keywords file: %s\n' % os.path.exists(layer_uri.split('.')[0] + '.xml')
        message += 'keywords:\n'
        for k, v in keywords.iteritems():
            message += '%s: %s\n' % (k, v)
        raise MetadataReadError(message)
    keywords = {}
    temp_keywords = {x[0]: x[1]['value'] for x in metadata.dict['properties'].iteritems()}
    included = [
        'aggregation attribute'
    ]
    for key in temp_keywords.iterkeys():
        if key in included:
            keywords[key] = temp_keywords[key]
        else:
            if temp_keywords[key] is not None:
                keywords[key] = temp_keywords[key]

    if keyword:
        try:
            return keywords[keyword]
        except KeyError:
            message = 'Keyword with key %s is not found' % keyword
            message += 'Layer path: %s' % layer_uri
            raise KeywordNotFoundError(message)

    return keywords


def write_read_iso_19115_metadata(layer_uri, keywords, keyword=None):
    """Write ISO Metadata, and read again. Check if the keywords same.
    :param layer_uri:
    :param keywords:
    :type keywords: dict
    :return:
    """
    # if os.path.exists(layer_uri):
    #     os.remove(layer_uri.split('.')[0] + '.xml')
    write_iso19115_metadata(layer_uri, keywords)
    iso_19115_keywords = read_iso19115_metadata(layer_uri)
    temp_keywords = keywords.copy()
    # if there is no keyword_version, assume it the latest.
    if 'keyword_version' not in temp_keywords.keys():
        temp_keywords['keyword_version'] = inasafe_keyword_version
    if (temp_keywords != iso_19115_keywords):
        missing_keywords = {}
        missing_keys = set(keywords.keys()) - set(iso_19115_keywords.keys())
        for key in missing_keys:
            missing_keywords[key] = keywords[key]
        message = 'Old metadata: %s\n' % str(keywords)
        message += 'ISO metadata: %s\n' % str(iso_19115_keywords)
        message += 'Layer location : %s\n' % layer_uri
        message += 'Missing keywords:\n'
        for key, value in missing_keywords.iteritems():
            message += '%s: %s\n' % (key, value)
        message += '--------------------\n'
        different_values = {}
        for key in keywords.keys():
            if key in iso_19115_keywords.keys():
                if keywords[key] != iso_19115_keywords[key]:
                    different_values[key] = (
                        keywords[key], iso_19115_keywords[key])
        for key, value in different_values.iteritems():
            message += 'old - %s - %s - type: %s\n' % (key, value[0], type(value[0]))
            message += 'new - %s - %s - type: %s\n' % (key, value[1], type(value[1]))
        raise MissingMetadata(message)
    if os.path.exists(layer_uri.split('.')[0] + '.keywords'):
        os.remove(layer_uri.split('.')[0] + '.keywords')
    if keyword:
        if keyword in iso_19115_keywords.keys():
            return iso_19115_keywords[keyword]
        else:
            return None
    else:
        return iso_19115_keywords
