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
__revision__ = 'b9e2d7536ddcf682e32a156d6d8b0dbc0bb73cc4'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.utils import merge_dictionaries


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
        'vector_hazard_classification': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'vector_hazard_classification/'
            'gco:CharacterString'),
        'raster_hazard_classification': (
            'gmd:identificationInfo/'
            'gmd:MD_DataIdentification/'
            'gmd:supplementalInformation/'
            'inasafe/'
            'raster_hazard_classification/'
            'gco:CharacterString')
    }
    _standard_properties = merge_dictionaries(
        GenericLayerMetadata._standard_properties, _standard_properties)
