# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


# DO NOT REMOVE THIS
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
import os
from safe.common.utilities import temp_dir

TEMP_DIR = temp_dir(sub_dir='test/metadata')
TEST_DIR = os.path.dirname(__file__)

EXISTING_IMPACT_FILE = os.path.join(TEST_DIR, 'data', 'existing_impact.shp')
# this is a file generated from TestImpactMetadata.generate_test_metadata()
EXISTING_IMPACT_JSON = os.path.join(TEST_DIR, 'data', 'existing_impact.json')
EXISTING_IMPACT_XML = os.path.join(TEST_DIR, 'data', 'existing_impact.xml')

EXISTING_GENERIC_FILE = os.path.join(TEST_DIR, 'data', 'existing_generic.shp')
# this is a file generated from TestGenericMetadata.generate_test_metadata()
EXISTING_GENERIC_JSON = os.path.join(TEST_DIR, 'data', 'existing_generic.json')
EXISTING_GENERIC_XML = os.path.join(TEST_DIR, 'data', 'existing_generic.xml')

INVALID_IMPACT_JSON = os.path.join(TEST_DIR, 'data', 'invalid_impact.json')
INCOMPLETE_IMPACT_JSON = os.path.join(
    TEST_DIR, 'data', 'incomplete_impact.json')

TEST_XML_BASEPATH = 'gmd:identificationInfo/gmd:MD_DataIdentification/'

EXISTING_NO_METADATA = os.path.join(
    TEST_DIR, 'data', 'existing_no_metadata.shp')
