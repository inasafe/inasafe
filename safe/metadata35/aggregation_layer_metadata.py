# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.metadata35.generic_layer_metadata import GenericLayerMetadata
from safe.metadata35.utils import merge_dictionaries


class AggregationLayerMetadata(GenericLayerMetadata):
    """
    Metadata class for aggregation layers

    .. versionadded:: 3.2
    """

    _standard_properties = {
        'aggregation attribute': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'aggregation_attribute/'
            'gco:CharacterString'),
        'adult ratio attribute': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'adult_ratio_attribute/'
            'gco:CharacterString'),
        'adult ratio default': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'adult_ratio_default/'
            'gco:Float'),
        'elderly ratio attribute': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'elderly_ratio_attribute/'
            'gco:CharacterString'),
        'elderly ratio default': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'elderly_ratio_default/'
            'gco:Float'),
        'female ratio attribute': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'female_ratio_attribute/'
            'gco:CharacterString'),
        'female ratio default': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'female_ratio_default/'
            'gco:Float'),
        'youth ratio attribute': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'youth_ratio_attribute/'
            'gco:CharacterString'),
        'youth ratio default': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'youth_ratio_default/'
            'gco:Float')
    }
    _standard_properties = merge_dictionaries(
        GenericLayerMetadata._standard_properties, _standard_properties)
