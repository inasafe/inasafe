# coding=utf-8
"""
Definitions for the name of the current step in our algorithms.
"""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

"""
Vector package
"""

buffer_vector = {
    'step_name': tr('Buffering'),
    'output_layer_name': 'buffer',
}

prepare_vector = {
    'step_name': tr('Preparing'),
    'output_layer_name': 'cleaned',
}

reclassify_vector = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': 'reclassified',
}

reproject_vector = {
    'step_name': tr('Reprojecting'),
    'output_layer_name': 'reprojected',
}


"""
Raster package
"""

polygonize_raster = {
    'step_name': tr('Polygonize'),
    'output_layer_name': 'polygonized',
}

reclassify_raster = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': 'reclassified',
}
