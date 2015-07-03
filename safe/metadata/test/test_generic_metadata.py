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
from safe.metadata.generic_layer_metadata import GenericLayerMetadata

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from unittest import TestCase

from safe.metadata.test import JSON_GENERIC_TEST_FILE, TEMP_DIR
from safe.common.utilities import unique_filename


class TestMetadata(TestCase):
    def test_read(self):
        metadata = self.generate_test_metadata()

    def test_json_write(self):
        with open(JSON_GENERIC_TEST_FILE) as f:
            test_json = f.read()

        metadata = self.generate_test_metadata()
        filename = unique_filename(suffix='.json', dir=TEMP_DIR)
        metadata.write_as(filename)
        with open(filename) as f:
            written_json = f.read()

        self.assertEquals(written_json, test_json)

    def generate_test_metadata(self):
        metadata = GenericLayerMetadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'
        # using str
        test_value = 'Random string'
        metadata.set('ISO19115_STR', test_value, path, 'gco:CharacterString')
        test_value = 1234
        metadata.set('ISO19115_INT', test_value, path, 'gco:CharacterString')
        test_value = 1234.5678
        metadata.set('ISO19115_FLOAT', test_value, path, 'gco:CharacterString')
        metadata.report = 'My super report'
        return metadata
