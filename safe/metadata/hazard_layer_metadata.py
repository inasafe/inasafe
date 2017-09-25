# coding=utf-8
"""This module exposure layer metadata implementation."""

from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.utilities import merge_dictionaries
from safe.definitions.keyword_properties import (
    property_hazard,
    property_hazard_category,
    property_continuous_hazard_unit,
    property_value_maps,
    property_thresholds,
    property_active_band
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class HazardLayerMetadata(GenericLayerMetadata):
    """
    Metadata class for hazard layers

    .. versionadded:: 3.2
    """

    _standard_properties = {
        property_hazard['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard/'
            'gco:CharacterString'),
        property_hazard_category['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard_category/'
            'gco:CharacterString'),
        property_continuous_hazard_unit['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'continuous_hazard_unit/'
            'gco:CharacterString'),
        property_value_maps['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'value_map/'
            'gco:Dictionary'),
        property_thresholds['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'thresholds/'
            'gco:Dictionary'),
        property_active_band['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'active_band/'
            'gco:Integer'),
    }
    _standard_properties = merge_dictionaries(
        GenericLayerMetadata._standard_properties, _standard_properties)
