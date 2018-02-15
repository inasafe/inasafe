# coding=utf-8
"""Provenance Keys."""

from safe.definitions.layer_purposes import (
    layer_purpose_exposure_summary,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_aggregation_summary,
    layer_purpose_analysis_impacted,
    layer_purpose_exposure_summary_table,
    layer_purpose_profiling
)

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


provenance_action_checklist = {
    'key': 'provenance_action_checklist',
    'name': tr('Action Checklist'),
    'provenance_key': 'action_checklist'
}
provenance_aggregation_keywords = {
    'key': 'provenance_aggregation_keywords',
    'name': tr('Aggregation Keywords'),
    'provenance_key': 'aggregation_keywords'
}
provenance_aggregation_layer = {
    'key': 'provenance_aggregation_layer',
    'name': tr('Aggregation Layer'),
    'provenance_key': 'aggregation_layer'
}
provenance_aggregation_layer_id = {
    'key': 'provenance_aggregation_layer_id',
    'name': tr('Aggregation Layer ID'),
    'provenance_key': 'aggregation_layer_id'
}
provenance_analysis_extent = {
    'key': 'provenance_analysis_extent',
    'name': tr('Analysis Extent'),
    'provenance_key': 'analysis_extent'
}
provenance_analysis_question = {
    'key': 'provenance_analysis_question',
    'name': tr('Analysis Question'),
    'provenance_key': 'analysis_question'
}
provenance_data_store_uri = {
    'key': 'provenance_data_store_uri',
    'name': tr('Data Store URI'),
    'provenance_key': 'data_store_uri'
}
provenance_duration = {
    'key': 'provenance_duration',
    'name': tr('Duration'),
    'provenance_key': 'duration'
}
provenance_end_datetime = {
    'key': 'provenance_end_datetime',
    'name': tr('End Datetime'),
    'provenance_key': 'end_datetime'
}
provenance_exposure_keywords = {
    'key': 'provenance_exposure_keywords',
    'name': tr('Exposure Keywords'),
    'provenance_key': 'exposure_keywords'
}
provenance_exposure_layer = {
    'key': 'provenance_exposure_layer',
    'name': tr('Exposure Layer'),
    'provenance_key': 'exposure_layer'
}
provenance_exposure_layer_id = {
    'key': 'provenance_exposure_layer_id',
    'name': tr('Exposure Layer Id'),
    'provenance_key': 'exposure_layer_id'
}
provenance_multi_exposure_keywords = {
    'key': 'provenance_multi_exposure_keywords',
    'name': tr('Multi Exposure Keywords'),
    'description': tr(
        'A dictionary with each exposure keys and their keywords.'),
    'provenance_key': 'multi_exposure_keywords'
}
provenance_multi_exposure_layers = {
    'key': 'provenance_multi_exposure_layers',
    'name': tr('Multi Exposure Layers'),
    'description': tr('A list of exposure layers.'),
    'provenance_key': 'multi_exposure_layers'
}
provenance_multi_exposure_layers_id = {
    'key': 'provenance_multi_exposure_layers_id',
    'name': tr('Multi Exposure Layers Id'),
    'description': tr('A list of exposure layer IDs.'),
    'provenance_key': 'multi_exposure_layers_id'
}
provenance_multi_exposure_summary_layers = {
    'key': 'provenance_multi_exposure_summary_layers',
    'name': tr('Multi Exposure Summary Layers'),
    'description': tr('A dictionary of exposure summary layers.'),
    'provenance_key': 'multi_exposure_summary_layers'
}
provenance_multi_exposure_summary_layers_id = {
    'key': 'provenance_multi_exposure_summary_layers_id',
    'name': tr('Multi Exposure Summary Layers Id'),
    'description': tr('A dictionary of exposure summary layer IDs.'),
    'provenance_key': 'multi_exposure_summary_layers_id'
}
provenance_multi_exposure_analysis_summary_layers = {
    'key': 'provenance_multi_exposure_analysis_summary_layers',
    'name': tr('Multi Exposure Analysis Summary Layers'),
    'description': tr('A dictionary of exposure analysis summary layers.'),
    'provenance_key': 'multi_exposure_analysis_summary_layers'
}
provenance_multi_exposure_analysis_summary_layers_id = {
    'key': 'provenance_multi_exposure_analysis_summary_layers_id',
    'name': tr('Multi Exposure Analysis Summary Layers Id'),
    'description': tr('A dictionary of exposure analysis summary layer IDs.'),
    'provenance_key': 'multi_exposure_analysis_summary_layers_id'
}
provenance_gdal_version = {
    'key': 'provenance_gdal_version',
    'name': tr('GDAL Version'),
    'provenance_key': 'gdal_version'
}
provenance_hazard_keywords = {
    'key': 'provenance_hazard_keywords',
    'name': tr('Hazard Keywords'),
    'provenance_key': 'hazard_keywords'
}
provenance_hazard_layer = {
    'key': 'provenance_hazard_layer',
    'name': tr('Hazard Layer'),
    'provenance_key': 'hazard_layer'
}
provenance_hazard_layer_id = {
    'key': 'provenance_hazard_layer_id',
    'name': tr('Hazard Layer ID'),
    'provenance_key': 'hazard_layer_id'
}
provenance_host_name = {
    'key': 'provenance_host_name',
    'name': tr('Host Name'),
    'provenance_key': 'host_name'
}
provenance_impact_function_name = {
    'key': 'provenance_impact_function_name',
    'name': tr('Impact Function Name'),
    'provenance_key': 'impact_function_name'
}
provenance_impact_function_title = {
    'key': 'provenance_impact_function_title',
    'name': tr('Impact Function Title'),
    'provenance_key': 'impact_function_title'
}
provenance_inasafe_version = {
    'key': 'provenance_inasafe_version',
    'name': tr('InaSAFE Version'),
    'provenance_key': 'inasafe_version'
}
provenance_map_legend_title = {
    'key': 'provenance_map_legend_title',
    'name': tr('Map Legend Title'),
    'provenance_key': 'map_legend_title'
}
provenance_map_title = {
    'key': 'provenance_map_title',
    'name': tr('Map Title'),
    'provenance_key': 'map_title'
}
provenance_notes = {
    'key': 'provenance_notes',
    'name': tr('Notes'),
    'provenance_key': 'notes'
}
provenance_os = {
    'key': 'provenance_os',
    'name': tr('OS'),
    'provenance_key': 'os'
}
provenance_pyqt_version = {
    'key': 'provenance_pyqt_version',
    'name': tr('PyQT Version'),
    'provenance_key': 'pyqt_version'
}
provenance_qgis_version = {
    'key': 'provenance_qgis_version',
    'name': tr('QGIS Version'),
    'provenance_key': 'qgis_version'
}
provenance_qt_version = {
    'key': 'provenance_qt_version',
    'name': tr('QT Version'),
    'provenance_key': 'qt_version'
}
provenance_requested_extent = {
    'key': 'provenance_requested_extent',
    'name': tr('Requested Extent'),
    'provenance_key': 'requested_extent'
}
provenance_start_datetime = {
    'key': 'provenance_start_datetime',
    'name': tr('Start Datetime'),
    'provenance_key': 'start_datetime'
}
provenance_earthquake_function = {
    'key': 'provenance_earthquake_function',
    'name': tr('Earthquake Function'),
    'provenance_key': 'earthquake_function'
}
provenance_user = {
    'key': 'provenance_user',
    'name': tr('User'),
    'provenance_key': 'user'
}
provenance_crs = {
    'key': 'provenance_crs',
    'name': tr('CRS'),
    'provenance_key': 'crs'
}

provenance_use_rounding = {
    'key': 'provenance_use_rounding',
    'name': tr('Use Rounding'),
    'provenance_key': 'use_rounding'
}

provenance_debug_mode = {
    'key': 'provenance_debug_mode',
    'name': tr('Debug Mode'),
    'provenance_key': 'debug'
}

# Output layer path
provenance_layer_exposure_summary = {
    'key': 'provenance_layer_exposure_summary',
    'name': layer_purpose_exposure_summary['name'],
    'provenance_key': layer_purpose_exposure_summary['key']
}
provenance_layer_aggregate_hazard_impacted = {
    'key': 'provenance_layer_aggregate_hazard_impacted',
    'name': layer_purpose_aggregate_hazard_impacted['name'],
    'provenance_key': layer_purpose_aggregate_hazard_impacted['key']
}
provenance_layer_aggregation_summary = {
    'key': 'provenance_layer_aggregation_summary',
    'name': layer_purpose_aggregation_summary['name'],
    'provenance_key': layer_purpose_aggregation_summary['key']
}
provenance_layer_analysis_impacted = {
    'key': 'provenance_layer_analysis_impacted',
    'name': layer_purpose_analysis_impacted['name'],
    'provenance_key': layer_purpose_analysis_impacted['key']
}
provenance_layer_exposure_summary_table = {
    'key': 'provenance_layer_exposure_summary_table',
    'name': layer_purpose_exposure_summary_table['name'],
    'provenance_key': layer_purpose_exposure_summary_table['key']
}
provenance_layer_profiling = {
    'key': 'provenance_layer_profiling',
    'name': layer_purpose_profiling['name'],
    'provenance_key': layer_purpose_profiling['key']
}

# Layers ID
provenance_layer_exposure_summary_id = {
    'key': 'provenance_layer_exposure_summary_id',
    'name': layer_purpose_exposure_summary['name'] + ' ID',
    'provenance_key': layer_purpose_exposure_summary['key'] + '_id'
}
provenance_layer_aggregate_hazard_impacted_id = {
    'key': 'provenance_layer_aggregate_hazard_impacted_id',
    'name': layer_purpose_aggregate_hazard_impacted['name'] + ' ID',
    'provenance_key': layer_purpose_aggregate_hazard_impacted['key'] + '_id'
}
provenance_layer_aggregation_summary_id = {
    'key': 'provenance_layer_aggregation_summary_id',
    'name': layer_purpose_aggregation_summary['name'] + ' ID',
    'provenance_key': layer_purpose_aggregation_summary['key'] + '_id'
}
provenance_layer_analysis_impacted_id = {
    'key': 'provenance_layer_analysis_impacted_id',
    'name': layer_purpose_analysis_impacted['name'] + ' ID',
    'provenance_key': layer_purpose_analysis_impacted['key'] + '_id'
}
provenance_layer_exposure_summary_table_id = {
    'key': 'provenance_layer_exposure_summary_table_id',
    'name': layer_purpose_exposure_summary_table['name'] + ' ID',
    'provenance_key': layer_purpose_exposure_summary_table['key'] + '_id'
}
provenance_layer_profiling_id = {
    'key': 'provenance_layer_profiling_id',
    'name': layer_purpose_profiling['name'] + ' ID',
    'provenance_key': layer_purpose_profiling['key'] + '_id'
}

provenance_list = [
    provenance_action_checklist,
    provenance_aggregation_keywords,
    provenance_aggregation_layer,
    provenance_aggregation_layer_id,
    provenance_analysis_extent,
    provenance_analysis_question,
    provenance_data_store_uri,
    provenance_duration,
    provenance_earthquake_function,
    provenance_end_datetime,
    provenance_exposure_keywords,
    provenance_exposure_layer,
    provenance_exposure_layer_id,
    provenance_gdal_version,
    provenance_hazard_keywords,
    provenance_hazard_layer,
    provenance_hazard_layer_id,
    provenance_host_name,
    provenance_impact_function_name,
    provenance_impact_function_title,
    provenance_inasafe_version,
    provenance_map_legend_title,
    provenance_map_title,
    provenance_notes,
    provenance_os,
    provenance_pyqt_version,
    provenance_qgis_version,
    provenance_qt_version,
    provenance_requested_extent,
    provenance_start_datetime,
    provenance_user,
    provenance_crs,
    # Output layer path
    provenance_layer_exposure_summary,
    provenance_layer_aggregate_hazard_impacted,
    provenance_layer_aggregation_summary,
    provenance_layer_analysis_impacted,
    provenance_layer_exposure_summary_table,
    provenance_layer_profiling,
    provenance_layer_exposure_summary_id,
    provenance_layer_aggregate_hazard_impacted_id,
    provenance_layer_aggregation_summary_id,
    provenance_layer_analysis_impacted_id,
    provenance_layer_exposure_summary_table_id,
    provenance_layer_profiling_id,
]

# Mapping to global variable in QGIS
duplicated_global_variables = {
    provenance_os['provenance_key']: 'qgis_os_name'
}
