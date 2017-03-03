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

assign_highest_value_steps = {
    'step_name': tr('Assign the highest hazard value to the exposure'),
    'output_layer_name': 'exposure_highest_value',
}

assign_inasafe_values_steps = {
    'step_name': tr('Assign InaSAFE values'),
    'output_layer_name': '%s_value_mapped',
}

assign_default_values_steps = {
    'step_name': tr('Assign InaSAFE default values'),
    'output_layer_name': '%s_default_values',
}

buffer_steps = {
    'step_name': tr('Buffering'),
    'output_layer_name': 'buffer',
}

clean_geometry_steps = {
    'step_name': tr('Cleaning geometry'),
    'output_layer_name': '%s_geometry_cleaned',
}

clip_steps = {
    'step_name': tr('Clipping'),
    'output_layer_name': '%s_clipped',
}

intersection_steps = {
    'step_name': tr('Intersecting divisible features with polygons'),
    'output_layer_name': '%s_intersected',
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

recompute_counts_steps = {
    'step_name': tr('Recompute counts'),
    'output_layer_name': 'exposure_counts',
}

smart_clip_steps = {
    'step_name': tr('Smart clipping'),
    'output_layer_name': 'exposure_intersect_hazard',
}

summary_1_aggregate_hazard_steps = {
    'step_name': tr('Compute aggregate hazard results'),
    'output_layer_name': 'aggregate_hazard',
}

summary_2_aggregation_steps = {
    'step_name': tr('Compute aggregation results'),
    'output_layer_name': 'aggregation',
}

summary_3_analysis_steps = {
    'step_name': tr('Compute analysis results'),
    'output_layer_name': 'analysis',
}

summary_4_exposure_summary_table_steps = {
    'step_name': tr('Compute exposure summary table'),
    'output_layer_name': 'exposure_summary_table',
}

union_steps = {
    'step_name': tr('Union'),
    'output_layer_name': '%s_%s_union',
}

"""
Raster package
"""

earthquake_displaced = {
    'step_name': tr('People Displaced'),
    'output_layer_name': 'people_displaced'
}

align_steps = {
    'step_name': tr('Align'),
    'output_layer_name': '%s_aligned',
}

polygonize_steps = {
    'step_name': tr('Polygonize'),
    'output_layer_name': '%s_polygonized',
    'gdal_layer_name': 'polygonized'
}

quick_clip_steps = {
    'step_name': tr('Clip by extent'),
    'output_layer_name': '%s_clipped_bbox',
}

rasterize_steps = {
    'step_name': tr('Rasterize'),
    'output_layer_name': '%s_rasterized',
    'gdal_layer_name': 'rasterize'
}

reclassify_raster_steps = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': '%s_reclassified',
}

zonal_stats_steps = {
    'step_name': tr('Zonal statistics'),
    'output_layer_name': 'zonal_stats',
}
