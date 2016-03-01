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


# expose for nicer imports
from safe.metadata.base_metadata import BaseMetadata
from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.impact_layer_metadata import ImpactLayerMetadata
from safe.metadata.exposure_layer_metadata import ExposureLayerMetadata
from safe.metadata.hazard_layer_metadata import HazardLayerMetadata
from safe.metadata.aggregation_layer_metadata import AggregationLayerMetadata
