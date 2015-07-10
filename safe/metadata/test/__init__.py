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

import os
from safe.common.utilities import temp_dir

TEMP_DIR = temp_dir(sub_dir='test')
TEST_DIR = os.path.dirname(__file__)

EXISTING_IMPACT_LAYER_TEST_FILE = os.path.join(
    TEST_DIR, 'data', 'existing_impact.shp')
EXISTING_IMPACT_LAYER_TEST_FILE_JSON = os.path.join(
    TEST_DIR, 'data', 'existing_impact.json')

EXISTING_GENERIC_LAYER_TEST_FILE = os.path.join(
    TEST_DIR, 'data', 'existing_generic.shp')
EXISTING_GENERIC_LAYER_TEST_FILE_JSON = os.path.join(
    TEST_DIR, 'data', 'existing_generic.json')

IMPACT_TEST_FILE_JSON = os.path.join(TEST_DIR, 'data', 'test_impact.json')
GENERIC_TEST_FILE_JSON = os.path.join(TEST_DIR, 'data', 'test_generic.json')
INVALID_IMPACT_LAYER_JSON = os.path.join(
    TEST_DIR, 'data', 'invalid_impact.json')
INCOMPLETE_IMPACT_LAYER_JSON = os.path.join(
    TEST_DIR, 'data', 'incomplete_impact.json')
