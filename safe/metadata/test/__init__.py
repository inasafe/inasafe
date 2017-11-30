# coding=utf-8
"""Init File for Test Package."""

# DO NOT REMOVE THIS
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
import os
from safe.common.utilities import temp_dir

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

TEMP_DIR = temp_dir(sub_dir='test/metadata')
TEST_DIR = os.path.dirname(__file__)

EXISTING_IMPACT_FILE = os.path.join(
    TEST_DIR, 'data', 'existing_exposure_impacted.shp')
# this is a file generated from TestImpactMetadata.generate_test_metadata()
EXISTING_IMPACT_JSON = os.path.join(
    TEST_DIR, 'data', 'existing_exposure_impacted.json')
EXISTING_IMPACT_XML = os.path.join(
    TEST_DIR, 'data', 'existing_exposure_impacted.xml')

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
