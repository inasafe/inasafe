# coding=utf-8
"""Metadata for Output Layer."""

from safe.metadata import GenericLayerMetadata

from safe.metadata.utilities import merge_dictionaries

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class OutputLayerMetadata(GenericLayerMetadata):
    """
    Metadata class for exposure summary layers

    if you need to add a standard XML property that only applies to this
    subclass, do it this way. @property and @propname.setter will be
    generated automatically

    _standard_properties = {
        'TESTprop': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'gco:CharacterString')
    }
    from safe.metadata.utils import merge_dictionaries
    _standard_properties = merge_dictionaries(
        BaseMetadata._standard_properties, _standard_properties)

    .. versionadded:: 3.2
    """

    # remember to add an attribute or a setter property with the same name
    # these are properties that need special getters and setters thus are
    # not put in the standard_properties
    _standard_properties = {
        'exposure_keywords': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'exposure_keywords/'
            'gco:Dictionary'),
        'hazard_keywords': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'hazard_keywords/'
            'gco:Dictionary'),
        'aggregation_keywords': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'aggregation_keywords/'
            'gco:Dictionary'),
        'provenance_data': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'provenance_data/'
            'gco:Dictionary'),
    }
    _standard_properties = merge_dictionaries(
        GenericLayerMetadata._standard_properties, _standard_properties)
