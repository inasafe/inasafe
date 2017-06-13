# coding=utf-8
"""Metadata Utilities."""
import os
import logging
from copy import deepcopy
from datetime import datetime, date

from PyQt4.QtCore import QUrl, QDate, QDateTime, Qt

from safe.common.exceptions import (
    MetadataReadError,
    KeywordNotFoundError,
    NoKeywordsFoundError)
from safe.definitions.layer_purposes import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    layer_purpose_exposure_summary,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_analysis_impacted,
    layer_purpose_exposure_summary_table
)
from safe.definitions.layer_modes import layer_mode_continuous
from safe.definitions.versions import inasafe_keyword_version
from safe.metadata import (
    ExposureLayerMetadata,
    HazardLayerMetadata,
    AggregationLayerMetadata,
    OutputLayerMetadata,
    GenericLayerMetadata)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')

METADATA_CLASSES = {
    layer_purpose_exposure['key']: ExposureLayerMetadata,
    layer_purpose_hazard['key']: HazardLayerMetadata,
    layer_purpose_aggregation['key']: AggregationLayerMetadata,
    layer_purpose_exposure_summary['key']: OutputLayerMetadata,
    layer_purpose_exposure_summary_table['key']: OutputLayerMetadata,
    layer_purpose_analysis_impacted['key']: OutputLayerMetadata,
    layer_purpose_aggregate_hazard_impacted['key']: OutputLayerMetadata
}


def write_iso19115_metadata(layer_uri, keywords):
    """Create metadata  object from a layer path and keywords dictionary.

    :param layer_uri: Uri to layer.
    :type layer_uri: basestring

    :param keywords: Dictionary of keywords.
    :type keywords: dict
    """

    if 'layer_purpose' in keywords:
        if keywords['layer_purpose'] in METADATA_CLASSES:
            metadata = METADATA_CLASSES[keywords['layer_purpose']](layer_uri)
        else:
            metadata = GenericLayerMetadata(layer_uri)
    else:
        metadata = GenericLayerMetadata(layer_uri)

    metadata.update_from_dict(keywords)
    # Always set keyword_version to the latest one.
    metadata.update_from_dict({'keyword_version': inasafe_keyword_version})

    if metadata.layer_is_file_based:
        xml_file_path = os.path.splitext(layer_uri)[0] + '.xml'
        metadata.write_to_file(xml_file_path)
    else:
        metadata.write_to_db()

    return metadata


def read_iso19115_metadata(layer_uri, keyword=None):
    """Retrieve keywords from a metadata object

    :param layer_uri: Uri to layer.
    :type layer_uri: basestring

    :param keyword: The key of keyword that want to be read. If None, return
        all keywords in dictionary.

    :returns: Dictionary of keywords or value of key as string.
    :rtype: dict, basestring
    """
    xml_uri = os.path.splitext(layer_uri)[0] + '.xml'
    if not os.path.exists(xml_uri):
        xml_uri = None
    if not xml_uri and os.path.exists(layer_uri):
        message = 'Layer based file but no xml file.\n'
        message += 'Layer path: %s.' % layer_uri
        raise NoKeywordsFoundError(message)
    metadata = GenericLayerMetadata(layer_uri, xml_uri)
    if metadata.layer_purpose in METADATA_CLASSES:
        metadata = METADATA_CLASSES[metadata.layer_purpose](layer_uri, xml_uri)

    # dictionary comprehension
    keywords = {
        x[0]: x[1]['value'] for x in metadata.dict['properties'].iteritems()
        if x[1]['value'] is not None}
    if 'keyword_version' not in keywords.keys() and xml_uri:
        message = 'No keyword version found. Metadata xml file is invalid.\n'
        message += 'Layer uri: %s\n' % layer_uri
        message += 'Keywords file: %s\n' % os.path.exists(
            os.path.splitext(layer_uri)[0] + '.xml')
        message += 'keywords:\n'
        for k, v in keywords.iteritems():
            message += '%s: %s\n' % (k, v)
        raise MetadataReadError(message)

    # Get dictionary keywords that has value != None
    keywords = {
        x[0]: x[1]['value'] for x in metadata.dict['properties'].iteritems()
        if x[1]['value'] is not None}

    if keyword:
        try:
            return keywords[keyword]
        except KeyError:
            message = 'Keyword with key %s is not found. ' % keyword
            message += 'Layer path: %s' % layer_uri
            raise KeywordNotFoundError(message)

    if isinstance(metadata, OutputLayerMetadata):
        keywords['if_provenance'] = metadata.provenance
    return keywords


def active_classification(keywords, exposure_key):
    """Helper to retrieve active classification for an exposure.

    :param keywords: Hazard layer keywords.
    :type keywords: dict

    :param exposure_key: The exposure key.
    :type exposure_key: str

    :returns: The active classification key. None if there is no active one.
    :rtype: str
    """
    if 'classification' in keywords:
        return keywords['classification']
    if keywords['layer_mode'] == layer_mode_continuous['key']:
        classifications = keywords['thresholds'].get(exposure_key)
    else:
        classifications = keywords['value_maps'].get(exposure_key)
    if classifications is None:
        return None
    for classification, value in classifications.items():
        if value['active']:
            return classification
    return None


def active_thresholds_value_maps(keywords, exposure_key):
    """Helper to retrieve active value maps or thresholds for an exposure.

    :param keywords: Hazard layer keywords.
    :type keywords: dict

    :param exposure_key: The exposure key.
    :type exposure_key: str

    :returns: Active thresholds or value maps.
    :rtype: dict
    """
    if 'classification' in keywords:
        if keywords['layer_mode'] == layer_mode_continuous['key']:
            return keywords['thresholds']
        else:
            return keywords['value_map']
    if keywords['layer_mode'] == layer_mode_continuous['key']:
        classifications = keywords['thresholds'].get(exposure_key)
    else:
        classifications = keywords['value_maps'].get(exposure_key)
    if classifications is None:
        return None
    for value in classifications.values():
        if value['active']:
            return value['classes']
    return None


def copy_layer_keywords(layer_keywords):
    """Helper to make a deep copy of a layer keywords.

    :param layer_keywords: A dictionary of layer's keywords.
    :type layer_keywords: dict

    :returns: A deep copy of layer keywords.
    :rtype: dict
    """
    copy_keywords = {}
    for key, value in layer_keywords.items():
        if isinstance(value, QUrl):
            copy_keywords[key] = value.toString()
        elif isinstance(value, datetime):
            copy_keywords[key] = value.date().isoformat()
        elif isinstance(value, QDate):
            copy_keywords[key] = value.toString(Qt.ISODate)
        elif isinstance(value, QDateTime):
            copy_keywords[key] = value.toString(Qt.ISODate)
        elif isinstance(value, date):
            copy_keywords[key] = value.isoformat()
        else:
            copy_keywords[key] = deepcopy(value)

    return copy_keywords
