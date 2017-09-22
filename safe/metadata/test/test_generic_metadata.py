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

import os
import uuid
from unittest import TestCase

from safe.common.utilities import unique_filename
from safe.metadata import GenericLayerMetadata
from safe.metadata.test import (
    TEMP_DIR,
    EXISTING_GENERIC_FILE,
    EXISTING_GENERIC_JSON,
    EXISTING_NO_METADATA)


class TestGenericMetadata(TestCase):

    maxDiff = None

    def test_json_write(self):
        with open(EXISTING_GENERIC_JSON) as f:
            expected_json = f.read()

        metadata = self.generate_test_metadata()
        filename = unique_filename(suffix='.json', dir=TEMP_DIR)
        metadata.write_to_file(filename)
        with open(filename) as f:
            written_json = f.read()

        self.assertMultiLineEqual(expected_json, written_json)

    def test_json_write_no_metadata(self):
        """Test write metadata for no metadata layer file."""
        with open(EXISTING_GENERIC_JSON) as f:
            expected_json = f.read()
        self.assertTrue(os.path.isfile(EXISTING_NO_METADATA))
        self.assertFalse(os.path.isfile(EXISTING_NO_METADATA[:-3] + 'xml'))
        self.assertFalse(os.path.isfile(EXISTING_NO_METADATA[:-3] + 'json'))
        metadata = self.generate_test_metadata(EXISTING_NO_METADATA)
        json_filename = unique_filename(suffix='.json', dir=TEMP_DIR)
        metadata.write_to_file(json_filename)

        with open(json_filename) as f:
            written_json = f.read()

        self.assertEquals(expected_json, written_json)

        # xml_filename = unique_filename(suffix='.xml', dir=TEMP_DIR)
        # metadata.write_to_file(xml_filename)
        # print xml_filename

    def test_json_read(self):
        """Test read json metadata."""
        metadata = GenericLayerMetadata(EXISTING_GENERIC_FILE)
        with open(EXISTING_GENERIC_JSON) as f:
            expected_metadata = f.read()

        self.assertMultiLineEqual(expected_metadata, metadata.json)

        # With filtering
        FILTERED_PATH = (
            EXISTING_GENERIC_FILE + '|layerid=0|subset="population" > 100')
        metadata = GenericLayerMetadata(FILTERED_PATH)
        with open(EXISTING_GENERIC_JSON) as f:
            expected_metadata = f.read()

        self.assertEquals(expected_metadata, metadata.json)

    def test_db_based_metadata(self):
        layer_uri = 'test_db_layer-%s' % uuid.uuid4()
        metadata = self.generate_test_metadata(layer_uri)
        expected_json = metadata.json
        expected_xml = metadata.xml

        try:
            # save to DB
            metadata.save()
            # reread from DB
            metadata.read_json()
            metadata.read_xml()

            self.assertEquals(expected_json, metadata.json)
            self.assertEquals(expected_xml, metadata.xml)

            metadata.abstract = 'lalala'
            metadata.title = 'new test title'
            metadata.save()

            # reread from DB
            metadata = self.generate_test_metadata(layer_uri)
            self.assertNotEqual(expected_json, metadata.json)
            self.assertNotEqual(expected_xml, metadata.xml)

            self.assertEquals(metadata.abstract, 'lalala')
            self.assertEquals(metadata.title, 'new test title')
        finally:
            metadata.db_io.delete_metadata_for_uri(layer_uri)

    def generate_test_metadata(self, layer=None):
        # if you change this you need to update GENERIC_TEST_FILE_JSON
        if layer is None:
            layer = 'random_layer_id'
        metadata = GenericLayerMetadata(layer)
        path = 'gmd:MD_Metadata/gmd:dateStamp/gco:CharacterString'
        # using str
        test_value = 'Random string'
        metadata.set('ISO19115_STR', test_value, path)
        test_value = 1234
        metadata.set('ISO19115_INT', test_value, path)
        test_value = 1234.5678
        metadata.set('ISO19115_FLOAT', test_value, path)
        metadata.report = 'My super report'
        return metadata
