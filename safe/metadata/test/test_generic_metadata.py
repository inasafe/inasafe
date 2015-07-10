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
from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.test import (
    GENERIC_TEST_FILE_JSON, TEMP_DIR,
    EXISTING_GENERIC_LAYER_TEST_FILE,
    EXISTING_GENERIC_LAYER_TEST_FILE_JSON)


class TestMetadata(TestCase):

    def test_json_write(self):
        with open(GENERIC_TEST_FILE_JSON) as f:
            expected_json = f.read()

        metadata = self.generate_test_metadata()
        filename = unique_filename(suffix='.json', dir=TEMP_DIR)
        metadata.write_as(filename)
        with open(filename) as f:
            written_json = f.read()

        self.assertEquals(expected_json, written_json)

    def test_json_read(self):
        metadata = GenericLayerMetadata(EXISTING_GENERIC_LAYER_TEST_FILE)
        with open(EXISTING_GENERIC_LAYER_TEST_FILE_JSON) as f:
            expected_metadata = f.read()

        self.assertEquals(expected_metadata, metadata.json)

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
