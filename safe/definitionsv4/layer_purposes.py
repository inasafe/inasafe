# coding=utf-8

"""Definitions relating to exposure."""
from safe.definitionsv4.concepts import concepts
from safe.definitionsv4.layer_geometry import (
    layer_geometry_raster,
    layer_geometry_line,
    layer_geometry_point,
    layer_geometry_polygon
)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

layer_purpose_exposure = {
    'key': 'exposure',
    'name': tr('Exposure'),
    'description': concepts['exposure']['description'],
    'allowed_geometries': [
        layer_geometry_point,
        layer_geometry_line,
        layer_geometry_polygon,
        layer_geometry_raster
    ],
    'citations': concepts['exposure']['citations'],
}

layer_purpose_hazard = {
    'key': 'hazard',
    'name': tr('Hazard'),
    'description': concepts['hazard']['description'],
    'allowed_geometries': [
        layer_geometry_polygon,
        layer_geometry_raster
    ],
    'citations': concepts['hazard']['citations']
}

layer_purpose_aggregation = {
    'key': 'aggregation',
    'name': tr('Aggregation'),
    'description': tr(
        'An <b>aggregation</b> layer represents regions that can be used to '
        'summarise impact analysis results. For example, we might summarise '
        'the affected people after a flood according to administration '
        'boundaries.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_exposure_impacted = {
    'key': 'exposure_impacted',
    'name': tr('Exposure Impacted'),
    'description': tr(
        'An <b>exposure impacted</b> layer is the result from InaSAFE '
        'analysis. It has fields that represent the result of each exposure '
        'from the hazard in the aggregation area.'),
    'allowed_geometries': [
        layer_geometry_point, layer_geometry_line, layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_aggregate_hazard_impacted = {
    'key': 'aggregate_hazard_impacted',
    'name': tr('Aggregate Hazard Impacted'),
    'description': tr(
        'An <b>aggregate hazard impacted</b> layer is the result from InaSAFE '
        'analysis.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_aggregation_impacted = {
    'key': 'aggregation_impacted',
    'name': tr('Aggregation Impacted'),
    'description': tr(
        'An <b>aggregation impacted</b> layer is the result from InaSAFE '
        'analysis.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_analysis_impacted = {
    'key': 'analysis_impacted',
    'name': tr('Analysis Impacted'),
    'description': tr(
        'An <b>analysis impacted</b> layer is the result from InaSAFE '
        'analysis. It contains only one geometry polygon.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_exposure_breakdown = {
    'key': 'exposure_breakdown',
    'name': tr('Exposure Breakdown'),
    'description': tr(
        'An <b>exposure breakdown</b> layer is the result from InaSAFE '
        'analysis. This layer do not have a geometry.'),
    'allowed_geometries': [],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_profiling = {
    'key': 'profiling',
    'name': tr('Profiling'),
    'description': tr(
        'A <b>profiling</b> layer is the result from InaSAFE analysis. '
        'This layer do not have a geometry.'),
    'allowed_geometries': [],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose = {
    'key': 'layer_purpose',
    'name': tr('Purpose'),
    'description': tr(
        'The purpose of the layer can be hazard layer, exposure layer, or '
        'aggregation layer'),
    'types': [
        layer_purpose_hazard,
        layer_purpose_exposure,
        layer_purpose_aggregation
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}


layer_purposes = [
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation
]
