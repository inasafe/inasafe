# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Converter Test Cases.**

Contact : kolesov.dm@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'kolesov.dm@gmail.com'
__date__ = '20/01/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from safe.test.utilities import (
    standard_data_path, get_qgis_app, clone_shp_layer)
from safe.gisv4.attributes.class_mapper import write_class_names

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestClassMapper(unittest.TestCase):

    def setUp(self):
        self.polygon_base = standard_data_path('hazard', '')

    def test_write_class_names(self):
        """Test we can write class names properly for a hazard."""
        layer = clone_shp_layer(
            'floods',
            include_keywords=True,
            source_directory=self.polygon_base)
        self.assertTrue(write_class_names(layer))
        provider = layer.dataProvider()
        fields = provider.fields()
        print fields


