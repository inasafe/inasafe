# coding=utf-8
"""Metadata Utilities."""
import logging
import os
from copy import deepcopy
from datetime import datetime, date

from qgis.PyQt.QtCore import QUrl, QDate, QDateTime, Qt

from safe.common.exceptions import (
    MetadataReadError,
    KeywordNotFoundError,
    NoKeywordsFoundError,
    MetadataConversionError
)
from safe.definitions.exposure import (
    exposure_structure,
    exposure_road,
    exposure_population,
    exposure_land_cover
)
from safe.definitions.fields import (
    adult_ratio_field,
    elderly_ratio_field,
    youth_ratio_field,
    female_ratio_field,
    exposure_name_field,
    exposure_id_field,
    population_count_field,
    hazard_name_field,
    hazard_value_field,
    aggregation_name_field,
)
from safe.definitions.hazard import hazard_volcano, hazard_generic
from safe.definitions.hazard_classifications import (
    generic_hazard_classes,
    flood_hazard_classes,
    tsunami_hazard_classes_ITB,
    volcano_hazard_classes,
)
from safe.definitions.layer_geometry import (
    layer_geometry_raster, layer_geometry_polygon
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
    layer_purpose_earthquake_contour,
)
from safe.definitions.versions import inasafe_keyword_version
from safe.metadata import (
    ExposureLayerMetadata,
    HazardLayerMetadata,
    AggregationLayerMetadata,
    OutputLayerMetadata,
    GenericLayerMetadata
)
from safe.metadata35 import (
    AggregationLayerMetadata as AggregationLayerMetadata35)
from safe.metadata35 import ExposureLayerMetadata as ExposureLayerMetadata35
# 3.5 metadata
from safe.metadata35 import GenericLayerMetadata as GenericLayerMetadata35
from safe.metadata35 import HazardLayerMetadata as HazardLayerMetadata35
from safe.utilities.settings import setting

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
    layer_purpose_earthquake_contour['key']: OutputLayerMetadata
}

METADATA_CLASSES35 = {
    layer_purpose_exposure['key']: ExposureLayerMetadata35,
    layer_purpose_hazard['key']: HazardLayerMetadata35,
    layer_purpose_aggregation['key']: AggregationLayerMetadata35,
}

vector_classification_conversion = {
    generic_hazard_classes['key']: 'generic_vector_hazard_classes',
    flood_hazard_classes['key']: 'flood_vector_hazard_classes',
    volcano_hazard_classes['key']: 'volcano_vector_hazard_classes',
}
raster_classification_conversion = {
    generic_hazard_classes['key']: 'generic_raster_hazard_classes',
    flood_hazard_classes['key']: 'flood_raster_hazard_classes',
    tsunami_hazard_classes_ITB['key']: 'tsunami_hazard_classes_ITB',
}


# noinspection PyPep8Naming
def append_ISO19115_keywords(keywords):
    """Append ISO19115 from setting to keywords.

    :param keywords: The keywords destination.
    :type keywords: dict
    """
    # Map setting's key and metadata key
    ISO19115_mapping = {
        'ISO19115_ORGANIZATION': 'organisation',
        'ISO19115_URL': 'url',
        'ISO19115_EMAIL': 'email',
        'ISO19115_LICENSE': 'license'
    }
    ISO19115_keywords = {}
    # Getting value from setting.
    for key, value in list(ISO19115_mapping.items()):
        ISO19115_keywords[value] = setting(key, expected_type=str)
    keywords.update(ISO19115_keywords)


def write_iso19115_metadata(layer_uri, keywords, version_35=False):
    """Create metadata  object from a layer path and keywords dictionary.

    This function will save these keywords to the file system or the database.

    :param version_35: If we write keywords version 3.5. Default to False.
    :type version_35: bool

    :param layer_uri: Uri to layer.
    :type layer_uri: basestring

    :param keywords: Dictionary of keywords.
    :type keywords: dict
    """
    active_metadata_classes = METADATA_CLASSES
    if version_35:
        active_metadata_classes = METADATA_CLASSES35

    if 'layer_purpose' in keywords:
        if keywords['layer_purpose'] in active_metadata_classes:
            metadata = active_metadata_classes[
                keywords['layer_purpose']](layer_uri)
        else:
            LOGGER.info(
                'The layer purpose is not supported explicitly. It will use '
                'generic metadata. The layer purpose is %s' %
                keywords['layer_purpose'])
            if version_35:
                metadata = GenericLayerMetadata35(layer_uri)
            else:
                metadata = GenericLayerMetadata(layer_uri)
    else:
        if version_35:
            metadata = GenericLayerMetadata35(layer_uri)
        else:
            metadata = GenericLayerMetadata(layer_uri)

    metadata.update_from_dict(keywords)
    # Always set keyword_version to the latest one.
    if not version_35:
        metadata.update_from_dict({'keyword_version': inasafe_keyword_version})

    if metadata.layer_is_file_based:
        xml_file_path = os.path.splitext(layer_uri)[0] + '.xml'
        metadata.write_to_file(xml_file_path)
    else:
        metadata.write_to_db()

    return metadata


def read_iso19115_metadata(layer_uri, keyword=None, version_35=False):
    """Retrieve keywords from a metadata object

    :param layer_uri: Uri to layer.
    :type layer_uri: basestring

    :param keyword: The key of keyword that want to be read. If None, return
        all keywords in dictionary.
    :type keyword: basestring

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
    if version_35:
        metadata = GenericLayerMetadata35(layer_uri, xml_uri)
    else:
        metadata = GenericLayerMetadata(layer_uri, xml_uri)

    active_metadata_classes = METADATA_CLASSES
    if version_35:
        active_metadata_classes = METADATA_CLASSES35

    if metadata.layer_purpose in active_metadata_classes:
        metadata = active_metadata_classes[
            metadata.layer_purpose](layer_uri, xml_uri)

    # dictionary comprehension
    keywords = {
        x[0]: x[1]['value'] for x in list(metadata.dict['properties'].items())
        if x[1]['value'] is not None}
    if 'keyword_version' not in list(keywords.keys()) and xml_uri:
        message = 'No keyword version found. Metadata xml file is invalid.\n'
        message += 'Layer uri: %s\n' % layer_uri
        message += 'Keywords file: %s\n' % os.path.exists(
            os.path.splitext(layer_uri)[0] + '.xml')
        message += 'keywords:\n'
        for k, v in list(keywords.items()):
            message += '%s: %s\n' % (k, v)
        raise MetadataReadError(message)

    # Get dictionary keywords that has value != None
    keywords = {
        x[0]: x[1]['value'] for x in list(metadata.dict['properties'].items())
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
    classifications = None
    if 'classification' in keywords:
        return keywords['classification']
    if keywords['layer_mode'] == layer_mode_continuous['key']:
        classifications = keywords['thresholds'].get(exposure_key)
    elif 'value_maps' in keywords:
        classifications = keywords['value_maps'].get(exposure_key)
    if classifications is None:
        return None
    for classification, value in list(classifications.items()):
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
    for value in list(classifications.values()):
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
    for key, value in list(layer_keywords.items()):
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
    :type converter_parameters: str

    :returns: A metadata version 3.5.
    :rtype: dict
    """
    def single_field(field, field_definition):
        """Returning single field as string.

        :param field: The field property. Can be string or list of string.
        :type field: basestring, list

        :param field_definition: The definition of field.
        :type field_definition: dict

        :returns: The first element of list if only one, or the string if
            it's string.
        :rtype: basestring
        """
        if isinstance(field, list):
            if len(field) == 1:
                return field[0]
            elif len(field) == 0:
                return None
            else:
                raise MetadataConversionError(
                    'Can not convert keyword with multiple field mapping. The '
                    'field concept is %s\nThe fields are %s'
                    % (field_definition['key'], ', '.join(field))
                )
        else:
            return field
    if not keywords.get('keyword_version'):
        raise MetadataConversionError('No keyword version found.')
    if not keywords['keyword_version'].startswith('4'):
        raise MetadataConversionError(
            'Only able to convert metadata version 4.x. Your version is %s' %
            keywords['keyword_version'])
    new_keywords = {
        'keyword_version': '3.5',
    }
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
            if same_property == layer_purpose_hazard['key']:
                if keywords.get(same_property) == hazard_generic['key']:
                    # We use hazard_generic as key for generic hazard
                    new_keywords[same_property] = 'hazard_generic'

    # Mandatory keywords
    try:
        layer_purpose = keywords['layer_purpose']
        layer_geometry = keywords['layer_geometry']
    except KeyError as e:
        raise MetadataConversionError(e)

    # No need to set value for multipart polygon and resolution
    inasafe_fields = keywords.get('inasafe_fields', {})
    inasafe_default_values = keywords.get('inasafe_default_values', {})
    if layer_purpose == layer_purpose_exposure['key']:
        exposure = keywords.get('exposure')
        if not exposure:
            raise MetadataConversionError(
                'Layer purpose is exposure but exposure is not set.')
        if inasafe_fields.get('exposure_type_field'):
            exposure_class_field = inasafe_fields.get('exposure_type_field')
            if exposure == exposure_structure['key']:
                new_keywords['structure_class_field'] = exposure_class_field
            elif exposure == exposure_road['key']:
                new_keywords['road_class_field'] = exposure_class_field
            else:
                if exposure == exposure_land_cover['key']:
                    new_keywords['field'] = exposure_class_field
                else:
                    new_keywords['structure_class_field'] = (
                        exposure_class_field)
        # Data type is only used in population exposure and in v4.x it is
        # always count
        if (exposure == exposure_population['key'] and layer_geometry ==
                layer_geometry_raster['key']):
            new_keywords['datatype'] = 'count'
        if (exposure == exposure_population['key'] and
                layer_geometry == layer_geometry_polygon['key']):
            if inasafe_fields.get(exposure_name_field['key']):
                new_keywords['area_name_field'] = inasafe_fields[
                    exposure_name_field['key']]
            if inasafe_fields.get(exposure_id_field['key']):
                new_keywords['area_id_field'] = inasafe_fields[
                    exposure_id_field['key']]
        if inasafe_fields.get(population_count_field['key']):
            population_field = inasafe_fields[
                population_count_field['key']]
            new_keywords['population_field'] = single_field(
                population_field, population_count_field)
        if inasafe_fields.get(exposure_name_field['key']):
            new_keywords['name_field'] = inasafe_fields[
                exposure_name_field['key']]

        if keywords.get('value_map'):
            new_keywords['value_mapping'] = keywords['value_map']

    elif layer_purpose == layer_purpose_hazard['key']:
        layer_mode = keywords['layer_mode']
        hazard = keywords.get('hazard')
        if not hazard:
            raise MetadataConversionError(
                'Layer purpose is hazard but hazard is not set.')
        if hazard == hazard_volcano['key']:
            if inasafe_fields.get(hazard_name_field['key']):
                new_keywords['volcano_name_field'] = inasafe_fields[
                    hazard_name_field['key']]
        if inasafe_fields.get(hazard_value_field['key']):
            new_keywords['field'] = inasafe_fields[hazard_value_field['key']]

        # Classification and value map (depends on the exposure)
        try:
            target_exposure = converter_parameters['exposure']
        except KeyError:
            raise MetadataConversionError(
                'You should supply target exposure for this hazard.'
            )
        if layer_mode == layer_mode_continuous['key']:
            pass
        # Classified
        else:
            classification = active_classification(keywords, target_exposure)
            value_map = active_thresholds_value_maps(keywords, target_exposure)
            if layer_geometry == layer_geometry_raster['key']:
                raster_classification = raster_classification_conversion.get(
                    classification
                )
                if raster_classification:
                    new_keywords[
                        'raster_hazard_classification'] = raster_classification
                    new_keywords['value_map'] = value_map
                else:
                    raise MetadataConversionError(
                        'Could not convert %s to version 3.5 '
                        'raster hazard classification' % classification
                    )
            else:
                vector_classification = vector_classification_conversion.get(
                    classification
                )
                if vector_classification:
                    new_keywords[
                        'vector_hazard_classification'] = vector_classification
                    new_keywords['value_map'] = value_map
                else:
                    raise MetadataConversionError(
                        'Could not convert %s to version 3.5 '
                        'vector hazard  classification' % classification
                    )

    elif layer_purpose == layer_purpose_aggregation['key']:
        # Fields
        if inasafe_fields.get(adult_ratio_field['key']):
            new_keywords['adult ratio attribute'] = single_field(
                inasafe_fields[adult_ratio_field['key']], adult_ratio_field)
        if inasafe_fields.get(elderly_ratio_field['key']):
            new_keywords['elderly ratio attribute'] = single_field(
                inasafe_fields[elderly_ratio_field['key']],
                elderly_ratio_field)
        if inasafe_fields.get(youth_ratio_field['key']):
            new_keywords['youth ratio attribute'] = single_field(
                inasafe_fields[youth_ratio_field['key']],
                youth_ratio_field)
        if inasafe_fields.get(female_ratio_field['key']):
            new_keywords['female ratio attribute'] = single_field(
                inasafe_fields[female_ratio_field['key']],
                female_ratio_field)
        # Notes(IS) I think people use name for the aggregation attribute
        if inasafe_fields.get(aggregation_name_field['key']):
            new_keywords['aggregation attribute'] = inasafe_fields[
                aggregation_name_field['key']]
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
