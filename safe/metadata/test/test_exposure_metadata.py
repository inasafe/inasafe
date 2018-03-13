# coding=utf-8
"""Test Exposure Metadata."""

from unittest import TestCase

from safe.common.utilities import unique_filename
from safe.metadata import ExposureLayerMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestExposureMetadata(TestCase):

    def test_standard_properties(self):
        metadata = ExposureLayerMetadata(unique_filename())
        with self.assertRaises(KeyError):
            metadata.get_property('non_existing_key')

        # from BaseMetadata
        metadata.get_property('title')

        # from ExposureLayerMetadata
        metadata.get_property('exposure')
        metadata.get_property('exposure_unit')
        metadata.get_property('value_map')
