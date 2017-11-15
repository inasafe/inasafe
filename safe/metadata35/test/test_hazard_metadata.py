# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from unittest import TestCase

from safe.common.utilities import unique_filename
from safe.metadata35 import HazardLayerMetadata


class TestHazardMetadata(TestCase):

    def test_standard_properties(self):
        metadata = HazardLayerMetadata(unique_filename())
        with self.assertRaises(KeyError):
            metadata.get_property('non_existing_key')

        # from BaseMetadata
        metadata.get_property('email')

        # from HazardLayerMetadata
        metadata.get_property('hazard')
        metadata.get_property('hazard_category')
        metadata.get_property('continuous_hazard_unit')
        metadata.get_property('vector_hazard_classification')
        metadata.get_property('raster_hazard_classification')
