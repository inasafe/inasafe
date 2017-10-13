# coding=utf-8
"""Test Hazard Metadata."""

from unittest import TestCase

from safe.common.utilities import unique_filename
from safe.metadata import HazardLayerMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestHazardMetadata(TestCase):

    def test_standard_properties(self):
        metadata = HazardLayerMetadata(unique_filename())
        with self.assertRaises(KeyError):
            metadata.get_property('non_existing_key')

        # from BaseMetadata
        metadata.get_property('email')

        # from HazardLayerMetadata
        metadata.get_property('hazard')
        metadata.get_property('hazard_category')
        metadata.get_property('continuous_hazard_unit')
        metadata.get_property('thresholds')
        metadata.get_property('value_maps')
