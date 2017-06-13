# coding=utf-8
"""Metadata init file."""

# expose for nicer imports
# pylint: disable=unused-import
from safe.metadata.base_metadata import BaseMetadata
from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.output_layer_metadata import (
    OutputLayerMetadata)
from safe.metadata.exposure_layer_metadata import ExposureLayerMetadata
from safe.metadata.hazard_layer_metadata import HazardLayerMetadata
from safe.metadata.aggregation_layer_metadata import AggregationLayerMetadata
# pylint: enable=unused-import

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'
