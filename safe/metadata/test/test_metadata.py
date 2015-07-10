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

from safe.metadata.base_metadata import BaseMetadata
from safe.metadata.impact_layer_metadata import ImpactLayerMetadata
from unittest import TestCase


class TestMetadata(TestCase):
    def test_no_BaseMeta_instantiation(self):
        """check that we can't instantiate abstract class BaseMetadata with
        abstract methods"""
        with self.assertRaises(TypeError):
            BaseMetadata('random_layer_id')

    def test_metadata(self):
        """Check we can't instantiate with unsupported xml types"""
        metadata = ImpactLayerMetadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'

        # using unsupported xml types
        test_value = 'Random string'
        with self.assertRaises(KeyError):
            metadata.set('ISO19115_TEST', test_value, path, 'gco:RandomString')
