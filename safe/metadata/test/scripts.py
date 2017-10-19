# coding=utf-8
"""Scripts for metadata."""

from safe.metadata.aggregation_layer_metadata import AggregationLayerMetadata
from safe.metadata.exposure_layer_metadata import ExposureLayerMetadata
from safe.metadata.hazard_layer_metadata import HazardLayerMetadata
from safe.metadata.output_layer_metadata import \
    OutputLayerMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def print_properties():
    """Print properties from all metadata in Markdown table."""
    metadata = [
        ExposureLayerMetadata,
        HazardLayerMetadata,
        AggregationLayerMetadata,
        OutputLayerMetadata
    ]

    for the_metadata in metadata:
        print '## ', the_metadata.__name__
        print 'No | Property | Type'
        print '------------ | ------------ | -------------'
        for i, item in enumerate(the_metadata._standard_properties.items()):
            print '%s | %s | %s' % (i + 1, item[0], item[1].split(':')[-1])
        print


if __name__ == '__main__':
    print_properties()
