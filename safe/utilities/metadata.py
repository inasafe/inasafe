# coding=utf-8
"""Metadata Utilities."""
import logging
import os
from copy import deepcopy
from datetime import datetime, date

from PyQt4.QtCore import QUrl, QDate, QDateTime, Qt

from safe.common.exceptions import (
    MetadataReadError,
    KeywordNotFoundError,
    NoKeywordsFoundError,
    MetadataConversionError
)
from safe.definitions.layer_modes import layer_mode_continuous
from safe.definitions.layer_purposes import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    layer_purpose_exposure_summary,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_analysis_impacted,
    layer_purpose_exposure_summary_table,
    layer_purpose_aggregation_summary,
    layer_purpose_profiling,
)
from safe.definitions.exposure import (
    exposure_structure,
    exposure_road,
    exposure_population
)
from safe.definitions.versions import inasafe_keyword_version
from safe.metadata import (
    ExposureLayerMetadata,
    HazardLayerMetadata,
    AggregationLayerMetadata,
    OutputLayerMetadata,
    GenericLayerMetadata)

from safe.definitions.fields import (
    adult_ratio_field,
    elderly_ratio_field,
    youth_ratio_field,
    female_ratio_field
)

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
    layer_purpose_aggregate_hazard_impacted['key']: OutputLayerMetadata,
    layer_purpose_aggregation_summary['key']: OutputLayerMetadata,
    layer_purpose_profiling['key']: OutputLayerMetadata,
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
            LOGGER.info(
                'The layer purpose is not supported explicitly. It will use '
                'generic metadata. The layer purpose is %s' %
                keywords['layer_purpose'])
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
    # Remove the prefix for local file. For example csv.
    file_prefix = 'file:'
    if xml_uri.startswith(file_prefix):
        xml_uri = xml_uri[len(file_prefix):]
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


def convert_metadata(keywords, **converter_parameters):
    """Convert metadata from version 4.3 to 3.5

    :param keywords: Metadata to be converted, in version 4.3.
    :type keywords: dict

    :param converter_parameters: Collection of parameters to convert the
        metadata properly.
    :type converter_parameters: dict

    :returns: A metadata version 3.5.
    :rtype: dict
    """
    new_keywords = {}
    # Properties that have the same concepts / values in both 3.5 and 4.3
    same_properties = [
        'organisation',
        'email',
        'date',
        'abstract',
        'title',
        'license',
        'url',
        'layer_purpose',
        'layer_mode',
        'layer_geometry',
        'keyword_version',
        'scale',
        'source',
        'exposure',
        'exposure_unit',
        'hazard',
        'hazard_category',
        'continuous_hazard_unit',
    ]
    for same_property in same_properties:
        if keywords.get(same_property):
            new_keywords[same_property] = keywords.get(same_property)

    # datatype
    if converter_parameters.get('datatype'):
        new_keywords['datatype'] = converter_parameters.get('datatype')

    # No need to set value for multipart polygon and resolution
    layer_purpose = keywords.get('layer_purpose')
    inasafe_fields = keywords.get('inasafe_fields')
    inasafe_default_values = keywords.get('inasafe_default_values')
    if layer_purpose == layer_purpose_exposure['key']:
        exposure = keywords.get('exposure')
        if not exposure:
            raise MetadataConversionError(
                'Layer purpose is exposure but exposure is not set.')
        if inasafe_fields.get('exposure_class_field'):
            exposure_class_field = inasafe_fields.get('exposure_class_field')
            if exposure == exposure_structure['key']:
                new_keywords['structure_class_field'] = exposure_class_field
            elif exposure == exposure_road['key']:
                new_keywords['road_class_field'] = exposure_class_field
    elif layer_purpose == layer_purpose_hazard['key']:
        pass
    elif layer_purpose == layer_purpose_aggregation['key']:
        # Fields
        if inasafe_fields.get(adult_ratio_field['key']):
            new_keywords['adult ratio attribute'] = inasafe_fields[
                adult_ratio_field['key']]
        if inasafe_fields.get(elderly_ratio_field['key']):
            new_keywords['elderly ratio attribute'] = inasafe_fields[
                elderly_ratio_field['key']]
        if inasafe_fields.get(youth_ratio_field['key']):
            new_keywords['youth ratio attribute'] = inasafe_fields[
                youth_ratio_field['key']]
        if inasafe_fields.get(female_ratio_field['key']):
            new_keywords['female ratio attribute'] = inasafe_fields[
                female_ratio_field['key']]
        # Default values
        if inasafe_default_values.get(adult_ratio_field['key']):
            new_keywords['adult ratio default'] = inasafe_default_values[
                adult_ratio_field['key']]
        if inasafe_default_values.get(elderly_ratio_field['key']):
            new_keywords['elderly ratio default'] = inasafe_default_values[
                elderly_ratio_field['key']]
        if inasafe_default_values.get(youth_ratio_field['key']):
            new_keywords['youth ratio default'] = inasafe_default_values[
                youth_ratio_field['key']]
        if inasafe_default_values.get(female_ratio_field['key']):
            new_keywords['female ratio default'] = inasafe_default_values[
                female_ratio_field['key']]

    return new_keywords
