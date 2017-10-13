# coding=utf-8
"""Test Aggregation Metadata."""

from unittest import TestCase

from safe.common.utilities import unique_filename
from safe.metadata import AggregationLayerMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAggregationMetadata(TestCase):

    def test_standard_properties(self):
        metadata = AggregationLayerMetadata(unique_filename())
        with self.assertRaises(KeyError):
            metadata.get_property('non_existing_key')

        # from BaseMetadata
        metadata.get_property('organisation')
