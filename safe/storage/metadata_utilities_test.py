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
import unittest

from xml.etree import ElementTree

from safe.storage.metadata_utilities import (
    valid_iso_xml,
    write_kw_in_iso_metadata,
    ISO_METADATA_KW_TAG,
    ISO_METADATA_KW_NESTING)

from safe.common.testing import UNITDATA
from safe.common.utilities import unique_filename


class TestCase(unittest.TestCase):
    def test_write_kw_in_iso_metadata(self):
        keyword_file = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'expected_multilayer.keywords'))

        with open(keyword_file) as f:
            keywords = f.read()

        basename, _ = os.path.splitext(keyword_file)
        xml_file = basename + '.xml'

        # there should be no xml file now
        self.assertFalse(os.path.isfile(xml_file))
        xml_file = write_kw_in_iso_metadata(keyword_file)
        tree = ElementTree.parse(xml_file)
        keyword_tag = tree.getroot().find(ISO_METADATA_KW_TAG)
        self.assertIn(keywords, keyword_tag.text)

        # there should be an xml file now
        self.assertTrue(os.path.isfile(xml_file))
        # lets update the file
        xml_file = write_kw_in_iso_metadata(keyword_file)
        tree = ElementTree.parse(xml_file)
        keyword_tag = tree.getroot().find(ISO_METADATA_KW_TAG)
        self.assertIn(keywords, keyword_tag.text)

        os.remove(xml_file)

    def test_valid_iso_xml(self):
        # test when XML file is non existent
        filename = unique_filename(suffix='.xml')
        tree = valid_iso_xml(filename)
        root = tree.getroot()
        self.assertIsNotNone(root.find(ISO_METADATA_KW_TAG))

        data_identification = root.find(ISO_METADATA_KW_NESTING[0] + '/'
                                        + ISO_METADATA_KW_NESTING[1])
        supplemental_info = root.find(ISO_METADATA_KW_NESTING[0] + '/'
                                      + ISO_METADATA_KW_NESTING[1] + '/'
                                      + ISO_METADATA_KW_NESTING[2])

        data_identification.remove(supplemental_info)
        # the xml should now miss the supplementalInformation tag
        self.assertIsNone(root.find(ISO_METADATA_KW_TAG))

        # lets fix the xml
        tree = valid_iso_xml(filename)
        self.assertIsNotNone(tree.getroot().find(ISO_METADATA_KW_TAG))
        os.remove(filename)


if __name__ == '__main__':
    my_suite = unittest.makeSuite(TestCase, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(my_suite)
