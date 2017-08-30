# coding=utf-8
"""Hazard Layer Metadata."""

from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.utilities import merge_dictionaries

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
        'hazard': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard/'
            'gco:CharacterString'),
        'hazard_category': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard_category/'
            'gco:CharacterString'),
        'continuous_hazard_unit': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'continuous_hazard_unit/'
            'gco:CharacterString'),
        'value_maps': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'value_map/'
            'gco:Dictionary'),
        'thresholds': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'thresholds/'
            'gco:Dictionary'),
        'active_band': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'active_band/'
            'gco:Integer'),
    }
    _standard_properties = merge_dictionaries(
        GenericLayerMetadata._standard_properties, _standard_properties)
