# coding=utf-8
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
import os

from safe.definitionsv4.versions import inasafe_keyword_version
from safe.definitionsv4.fields import (
    population_count_field,
    exposure_class_field,
    hazard_class_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    female_ratio_field,
    aggregation_name_field,
    exposure_name_field,
    exposure_id_field,
    hazard_name_field)
from safe.common.exceptions import (
    MetadataReadError,
    KeywordNotFoundError,
    NoKeywordsFoundError)
from safe.metadata import (
    ExposureLayerMetadata,
    HazardLayerMetadata,
    AggregationLayerMetadata,
    ExposureImpactedLayerMetadata,
    GenericLayerMetadata)
from safe.definitionsv4.layer_purposes import layer_purpose_exposure_impacted

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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
        elif keywords['layer_purpose'] == \
                layer_purpose_exposure_impacted['key']:
            metadata = ExposureImpactedLayerMetadata(layer_uri)
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
    :param layer_uri:
    :param keyword:
    :return:
    """
    xml_uri = os.path.splitext(layer_uri)[0] + '.xml'
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
    elif metadata.layer_purpose == layer_purpose_exposure_impacted['key']:
        metadata = ExposureImpactedLayerMetadata(layer_uri, xml_uri)

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
    keywords = {}
    temp_keywords = {
        x[0]: x[1]['value'] for x in metadata.dict['properties'].iteritems()}
    included = [
        'aggregation attribute',
        'female ratio attribute',
        'youth ratio attribute',
        'adult ratio attribute',
        'elderly ratio attribute',
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

    if isinstance(metadata, ExposureImpactedLayerMetadata):
        keywords['if_provenance'] = metadata.provenance
    return keywords


def metadata_migration(old_metadata, new_version=inasafe_keyword_version):
    """Migrate metadata to the new version.

    :param old_metadata: Old metadata as dictionary.
    :type old_metadata: dict

    :param new_version: New target keyword version, default current keyword
        version.
    :type new_version: str

    :returns: Migrated metadata.
    :rtype: dict
    """
    new_metadata = {}
    if old_metadata['keyword_version'] == new_version:
        return old_metadata
    elif old_metadata['keyword_version'] == '3.5' and new_version == '4.0':
        new_metadata['inasafe_fields'] = {}
        new_metadata['keyword_version'] = new_version
        for key, value in old_metadata.items():
            if key == 'keyword_version':
                new_metadata['keyword_version'] = new_version
            elif key in ['raster_hazard_classification',
                       'vector_hazard_classification']:
                new_metadata['classification'] = value
            elif key == 'field':
                if old_metadata['layer_purpose'] == 'hazard':
                    new_metadata['inasafe_fields'][
                        hazard_class_field['key']] = value
                elif old_metadata['layer_purpose'] == 'exposure':
                    new_metadata['inasafe_fields'][
                        exposure_class_field['key']] = value
            elif key == 'population_field':
                new_metadata['inasafe_fields'][
                    population_count_field['key']] = value
            elif key == 'area_type_field':
                # Not being used
                pass
            elif key == 'area_population_field':
                new_metadata['inasafe_fields'][
                    population_count_field['key']] = value
            elif key == 'structure_class_field':
                new_metadata['inasafe_fields'][
                    exposure_class_field['key']] = value
            elif key == 'area_name_field':
                new_metadata['inasafe_fields'][
                    exposure_name_field['key']] = value
            elif key == 'name_field':
                new_metadata['inasafe_fields'][
                    exposure_name_field['key']] = value
            elif key == 'area_id_field':
                new_metadata['inasafe_fields'][
                    exposure_id_field['key']] = value
            elif key == 'road_class_field':
                new_metadata['inasafe_fields'][
                    exposure_class_field['key']] = value
            elif key == 'volcano_name_field':
                new_metadata['inasafe_fields'][
                    hazard_name_field['key']] = value
            elif key == 'youth ratio attribute':
                new_metadata['inasafe_fields'][
                    youth_ratio_field['key']] = value
            elif key == 'aggregation attribute':
                new_metadata['inasafe_fields'][
                    aggregation_name_field['key']] = value
            elif key == 'adult ratio attribute':
                new_metadata['inasafe_fields'][
                    adult_ratio_field['key']] = value
            elif key == 'female ratio attribute':
                new_metadata['inasafe_fields'][
                    female_ratio_field['key']] = value
            elif key == 'elderly ratio attribute':
                new_metadata['inasafe_fields'][
                    elderly_ratio_field['key']] = value
            else:
                new_metadata[key] = value

    return new_metadata
