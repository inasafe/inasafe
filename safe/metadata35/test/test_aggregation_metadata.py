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
from safe.metadata35 import AggregationLayerMetadata


class TestAggregationMetadata(TestCase):

    def test_standard_properties(self):
        metadata = AggregationLayerMetadata(unique_filename())
        with self.assertRaises(KeyError):
            metadata.get_property('non_existing_key')

        # from BaseMetadata
        metadata.get_property('organisation')

        # from AggregationLayerMetadata
        metadata.get_property('aggregation attribute')
        metadata.get_property('adult ratio attribute')
        metadata.get_property('adult ratio default')
        metadata.get_property('elderly ratio attribute')
        metadata.get_property('elderly ratio default')
        metadata.get_property('female ratio attribute')
        metadata.get_property('female ratio default')
        metadata.get_property('youth ratio attribute')
        metadata.get_property('youth ratio default')
