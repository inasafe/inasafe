# coding=utf-8
"""This module exposure layer metadata implementation."""

from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.utilities import merge_dictionaries
from safe.definitions.keyword_properties import (
    property_exposure,
    property_exposure_unit,
    property_classification,
    property_value_map,
    property_active_band
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ExposureLayerMetadata(GenericLayerMetadata):
    """
    Metadata class for exposure layers

    .. versionadded:: 3.2
    """

    _standard_properties = {
        property_exposure['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'exposure/'
            'gco:CharacterString'),
        property_exposure_unit['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'exposure_unit/'
            'gco:CharacterString'),
        property_classification['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'classification/'
            'gco:CharacterString'),
        property_value_map['key']: (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'value_map/'
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
