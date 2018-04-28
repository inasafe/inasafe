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
from safe.metadata35.utils import insert_xml_element

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from xml.etree import ElementTree
from safe.metadata35 import BaseMetadata
from safe.metadata35 import ImpactLayerMetadata
from unittest import TestCase


class TestMetadata(TestCase):
    def test_no_BaseMeta_instantiation(self):
        """check that we can't instantiate abstract class BaseMetadata with
        abstract methods"""
        with self.assertRaises(TypeError):
            # intended instantiation test... So pylint should ignore this.
            # pylint: disable=abstract-class-instantiated
            BaseMetadata('random_layer_id')

    def test_metadata(self):
        """Check we can't instantiate with unsupported xml types"""
        metadata = ImpactLayerMetadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/gco:RandomString'

        # using unsupported xml types
        test_value = 'Random string'
        with self.assertRaises(KeyError):
            metadata.set('ISO19115_TEST', test_value, path)

    def test_insert_xml_element(self):
        """Check we can't insert custom nested elements"""
        root = ElementTree.Element('root')
        b = ElementTree.SubElement(root, 'b')
        ElementTree.SubElement(b, 'c')

        new_element_path = 'd/e/f'
        expected_xml = b'<root><b><c /></b><d><e><f>TESTtext</f></e></d></root>'

        element = insert_xml_element(root, new_element_path)
        element.text = 'TESTtext'
        result_xml = ElementTree.tostring(root)

        self.assertEqual(expected_xml, result_xml)
