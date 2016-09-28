# coding=utf-8
"""
Definitions for the name of the current step in our algorithms.
"""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

reproject_vector = {
    'step_name': tr('Reprojecting'),
    'output_layer_name': 'reprojected',
}

buffer_vector = {
    'step_name': tr('Buffering'),
    'output_layer_name': 'buffer',
}

reclassify_raster = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': 'reclassified',
}

processing_algorithms = [
    reproject_vector,
    buffer_vector,
    reclassify_raster,
]
