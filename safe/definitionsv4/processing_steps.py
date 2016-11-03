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

summary_1_impact_steps = {
    'step_name': tr('Aggregate impact results'),
    'output_layer_name': 'aggregate_hazard',
}

summary_2_aggregation_steps = {
    'step_name': tr('Aggregation results'),
    'output_layer_name': 'aggregation',
}

summary_3_aggregate_hazard_steps = {
    'step_name': tr('Aggregate hazard results'),
    'output_layer_name': 'analysis',
}

assign_highest_value_steps = {
    'step_name': tr('Assign the highest hazard value to the exposure'),
    'output_layer_name': 'exposure_highest_value',
}

assign_inasafe_values_steps = {
    'step_name': tr('Assign InaSAFE values'),
    'output_layer_name': '%s_value_mapped',
}

buffer_steps = {
    'step_name': tr('Buffering'),
    'output_layer_name': 'buffer',
}

clip_steps = {
    'step_name': tr('Clipping'),
    'output_layer_name': '%s_clipped',
}

prepare_vector_steps = {
    'step_name': tr('Cleaning the vector layer'),
    'output_layer_name': '%s_cleaned',
}

reclassify_vector_steps = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': '%s_reclassified',
}

reproject_steps = {
    'step_name': tr('Reprojecting'),
    'output_layer_name': '%s_reprojected',
}

smart_clip_steps = {
    'step_name': tr('Smart clipping'),
    'output_layer_name': 'indivisible_polygons_clipped',
}

union_steps = {
    'step_name': tr('Union'),
    'output_layer_name': '%s_%s_union',
}

"""
Raster package
"""

polygonize_steps = {
    'step_name': tr('Polygonize'),
    'output_layer_name': '%s_polygonized',
    'gdal_layer_name': 'polygonized'
}

reclassify_raster_steps = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': '%s_reclassified',
}

zonal_stats_steps = {
    'step_name': tr('Zonal statistics'),
    'output_layer_name': 'zonal_stats',
}
