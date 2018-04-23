# coding=utf-8
"""Test Metadata."""

from safe.metadata.utilities import insert_xml_element

from xml.etree import ElementTree
from safe.metadata import BaseMetadata
from safe.metadata import OutputLayerMetadata
from unittest import TestCase

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestMetadata(TestCase):
    def test_no_BaseMeta_instantiation(self):
        """check that we can't instantiate abstract class BaseMetadata with
        abstract methods"""
        with self.assertRaises(TypeError):
            # intended instantiation test... So pylint should ignore this.
            # pylint: disable=abstract-class-instantiated
            BaseMetadata('random_layer_id')

    def test_metadata(self):
        """Check we can't instantiate with unsupported xml types."""
        metadata = OutputLayerMetadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/gco:RandomString'

        # using unsupported xml types
        test_value = 'Random string'
        with self.assertRaises(KeyError):
            metadata.set('ISO19115_TEST', test_value, path)

    def test_insert_xml_element(self):
        """Check we can't insert custom nested elements."""
        root = ElementTree.Element('root')
        b = ElementTree.SubElement(root, 'b')
        ElementTree.SubElement(b, 'c')

        new_element_path = 'd/e/f'
        expected_xml = '<root><b><c /></b><d><e><f>TESTtext</f></e></d></root>'

        element = insert_xml_element(root, new_element_path)
        element.text = 'TESTtext'
        result_xml = ElementTree.tostring(root)

        self.assertEqual(expected_xml, result_xml)
